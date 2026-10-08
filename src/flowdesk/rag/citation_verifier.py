"""PRD Phase 04 T7 — validasi citation dua lapis.

Lapisan 1 (sudah ada, output_validator.py): [n] harus ada di sources.
Lapisan 2 (baru): per klaim x chunk yang dikutip, satu Choice Jev:
supports | contradicts | says_nothing.
- supports     (conf >= 0.80) -> dibiarkan
- says_nothing (conf >= 0.80) -> marker [n] DIBUANG  (citation spam)
- contradicts  (conf >= 0.80) -> jawaban diganti abstain (alasan di trace)
- conf < 0.80                  -> dibiarkan, ditandai needs_review di trace

Pemecahan klaim per kalimat dengan regex (MVP). Semua Choice untuk satu
chunk dikirim dalam SATU request (fan-out paralel di server TypeSafe).
"""

import re
from dataclasses import dataclass, field

from flowdesk.guardrails.config import JEV_CITATION_CONF


_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
_CITE = re.compile(r"\[(\d+)\]")


VERDICT_CRITERIA = {
    "supports": "The cited passage contains information that supports the claim",
    "contradicts": "The cited passage states something that contradicts the claim",
    "says_nothing": "The cited passage does not address the claim at all",
}


def split_claims(answer: str) -> list[tuple[str, list[int]]]:
    """Pure — jawaban -> [(kalimat ber-sitasi, [n])].

    Kalimat tanpa [n] diabaikan karena tidak bisa divalidasi
    dan tidak menyebabkan citation spam.
    """
    claims = []

    for sent in _SENT_SPLIT.split(answer):
        sent = sent.strip()

        if not sent:
            continue

        nums = sorted({int(m) for m in _CITE.findall(sent)})

        if nums:
            claims.append((sent, nums))

    return claims


@dataclass
class CitationCheck:
    verified_answer: str
    contradicted: list[str] = field(default_factory=list)
    dropped_markers: int = 0
    needs_review: list[str] = field(default_factory=list)
    checked: int = 0


def _judgement_question(claim: str) -> dict:
    return {
        "type": "choice",
        "instructions": (
            f"Claim: {claim}\n"
            "Judge ONLY whether the passage in `passage` supports, "
            "contradicts, or says nothing about this claim."
        ),
        "criteria": VERDICT_CRITERIA,
    }


def verify_citations(
    jev,
    answer: str,
    sources: list[dict],
    content_by_index: dict[int, str],
) -> CitationCheck:
    """Validasi citation menggunakan dua lapis.

    Layer 1:
        Nomor [n] sudah divalidasi oleh output_validator.py.

    Layer 2:
        Untuk setiap chunk yang dikutip, semua klaim yang mengutip
        chunk tersebut dikirim dalam satu request Jev.

    content_by_index:
        {index sitasi: teks chunk} dari state["chunks"].

    Jika verify_claims() gagal / mengembalikan None, Layer 2 dilewati
    untuk chunk tersebut dan citation tetap dipertahankan oleh Layer 1.
    """
    claims = split_claims(answer)

    # Kelompokkan klaim berdasarkan chunk citation.
    # Contoh:
    # [1] ... [2] ...
    # [1] ...
    #
    # menjadi:
    # {
    #     1: [claim_1, claim_2],
    #     2: [claim_1],
    # }
    by_index: dict[int, list[str]] = {}

    for sent, nums in claims:
        for n in nums:
            by_index.setdefault(n, []).append(sent)

    # n -> {klaim: {choice, confidence}}
    verdicts: dict[int, dict[str, dict]] = {}

    for n, n_claims in by_index.items():
        if n not in content_by_index:
            # Tidak ada teks chunk.
            # Layer 1 tetap menjadi fallback.
            continue

        resp = jev.verify_claims(
            content_by_index[n],
            {
                f"c{i}": _judgement_question(c)
                for i, c in enumerate(n_claims)
            },
        )

        if resp is None:
            # Layer 2 tidak tersedia/gagal.
            # Jangan mengambil keputusan berdasarkan hasil yang tidak ada.
            # Citation tetap dipertahankan oleh Layer 1.
            continue

        # Lookup berdasarkan key eksplisit.
        # Tidak mengandalkan urutan dict dari SDK.
        verdicts[n] = {
            n_claims[i]: {
                "choice": resp[f"c{i}"].choice,
                "confidence": resp[f"c{i}"].confidence,
            }
            for i in range(len(n_claims))
        }

    check = CitationCheck(verified_answer=answer)

    for sent, nums in claims:
        # Kalimat kerja — boleh berubah saat marker dibuang.
        current = sent

        for n in nums:
            # PENTING:
            # Selalu gunakan kalimat ORIGINAL untuk mencari verdict.
            # Jangan menggunakan `current` karena current bisa sudah
            # berubah setelah citation sebelumnya dibuang.
            v = verdicts.get(n, {}).get(sent)

            if v is None:
                continue

            check.checked += 1

            if v["confidence"] < JEV_CITATION_CONF:
                check.needs_review.append(
                    f"[{n}] {sent[:80]}"
                )

            elif v["choice"] == "contradicts":
                check.contradicted.append(
                    f"[{n}] {sent[:80]}"
                )

            elif v["choice"] == "says_nothing":
                new_current = current.replace(f"[{n}]", "")

                if new_current != current:
                    check.dropped_markers += 1
                    current = new_current

        # Substitusi sekali per kalimat + rapikan artefak spasi.
        if current != sent:
            current = re.sub(
                r"\s+([.,;:!?])",
                r"\1",
                current,
            )
            current = re.sub(r"  +", " ", current)

            check.verified_answer = check.verified_answer.replace(
                sent,
                current,
            )

    return check
