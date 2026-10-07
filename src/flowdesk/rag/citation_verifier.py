"""PRD Phase 04 T7 — validasi citation dua lapis.

Lapisan 1 (sudah ada, output_validator.py): [n] harus ada di sources.
Lapisan 2 (baru): per klaim x chunk yang dikutip, satu Choice Jev:
supports | contradicts | says_nothing.
- supports     (conf >= 0.80) -> dibiarkan
- says_nothing (conf >= 0.80) -> marker [n] DIBUANG  (menyelesaikan citation spam)
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
    """Pure — jawaban -> [(kalimat ber-sitasi, [n])]. Kalimat tanpa [n]
    diabaikan (tidak bisa divalidasi dan tidak menyebabkan spam)."""
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
    contradicted: list[str] = field(default_factory=list)   # klaim yang bertentangan
    dropped_markers: int = 0                                # jumlah [n] dibuang (spam)
    needs_review: list[str] = field(default_factory=list)   # klaim conf rendah
    checked: int = 0                                        # pasangan (klaim, [n])


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


def verify_citations(jev, answer: str, sources: list[dict],
                     content_by_index: dict[int, str]) -> CitationCheck:
    """content_by_index: {index sitasi: teks chunk} dari state["chunks"].
    Satu request Jev PER INDEX yang dikutip; tiap request memuat satu
    Choice per klaim yang mengutip index itu."""
    claims = split_claims(answer)
    by_index: dict[int, list[str]] = {}
    for sent, nums in claims:
        for n in nums:
            by_index.setdefault(n, []).append(sent)

    verdicts: dict[int, dict[str, dict]] = {}   # n -> {klaim: {choice, confidence}}
    for n, n_claims in by_index.items():
        if n not in content_by_index:           # tidak ada teks -> biarkan lapisan 1
            continue
        resp = jev.verify_claims(
            content_by_index[n],
            {f"c{i}": _judgement_question(c) for i, c in enumerate(n_claims)},
        )
        verdicts[n] = {
            claim: {"choice": a.choice, "confidence": a.confidence}
            for claim, a in zip(n_claims, resp.values())
        }

    check = CitationCheck(verified_answer=answer)
    for sent, nums in claims:
        for n in nums:
            v = verdicts.get(n, {}).get(sent)
            if v is None:
                continue
            check.checked += 1
            if v["confidence"] < JEV_CITATION_CONF:
                check.needs_review.append(f"[{n}] {sent[:80]}")
            elif v["choice"] == "contradicts":
                check.contradicted.append(f"[{n}] {sent[:80]}")
            elif v["choice"] == "says_nothing":
                check.dropped_markers += 1
                # buang marker [n] itu saja dari kalimat ini
                new_sent = re.sub(rf"\s*\[{n}\]", "", sent)
                if new_sent != sent:
                    check.verified_answer = check.verified_answer.replace(sent, new_sent)
                    sent = new_sent
    return check
