"""Smoke test Jev/TypeSafe — cek kesehatan semua jalur API yang dipakai workflow.

Jalankan dari root:  python scripts/smoke_jev.py
Bukan bagian pytest (memanggil API asli; butuh TYPESAFE_API_KEY di .env).

Yang dites (4 jalur yang benar-benar dipakai graph):
  1. score_chunk         (passage gate — jev_gate)      raise jika API mata
  2. verify_claims       (citation verifier)            None jika API gagal
  3. check_completeness  (jev_decide)                   fail-safe 0.0
  4. scope_check         (jev_decide, jalur insufficient) fail-safe True

Catatan penting soal fail-safe: #3 dan #4 menelan error API (0.0 / True),
jadi kesehatan API ditentukan oleh #1 dan #2. Exit code 0 = sehat, 1 = tidak
— berguna kalau nanti mau dimasukkan ke CI/healthcheck.
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from flowdesk.jev.client import JevClient


PASSAGE = "[1] Pro plan: $49/mo, includes API access and webhooks."

CLAIM_QUESTION = {
    "c0": {
        "type": "choice",
        "instructions": (
            "Claim: The Pro plan costs $49 per month.\n"
            "Judge ONLY whether the passage in `passage` supports, "
            "contradicts, or says nothing about this claim."
        ),
        "criteria": {
            "supports": "The cited passage contains information that "
                        "supports the claim",
            "contradicts": "The cited passage states something that "
                           "contradicts the claim",
            "says_nothing": "The cited passage does not address the "
                            "claim at all",
        },
    }
}


def main() -> int:
    print("Jev smoke test — 4 jalur API yang dipakai workflow\n")
    c = JevClient()
    results = []          # (nama, bool_pass, detail)

    # 1) score_chunk — kanari utama: raise jika key/model/jaringan bermasalah.
    try:
        s = c.score_chunk("Does the Pro plan support webhooks?", PASSAGE)
        results.append(("score_chunk", True,
                        f"relevant={s['is_relevant']:.2f} "
                        f"evidence={s['contains_answer_evidence']:.2f} "
                        f"injection={s['contains_prompt_injection']:.2f}"))
    except Exception as e:
        results.append(("score_chunk", False, f"{type(e).__name__}: {e}"))

    # 2) verify_claims — None = API gagal (fail-safe di client).
    resp = c.verify_claims(PASSAGE, CLAIM_QUESTION)
    if resp is None:
        results.append(("verify_claims", False, "API mengembalikan None"))
    else:
        v = resp["c0"]
        results.append(("verify_claims", True,
                        f"choice={v.choice} confidence={v.confidence:.2f} "
                        "(ekspektasi: supports)"))

    # 3) check_completeness — fail-safe 0.0, nilai hanya informatif.
    comp = c.check_completeness(
        "How much does the Pro plan cost?", PASSAGE)
    results.append(("check_completeness", None,
                    f"completeness={comp:.2f} "
                    "(fail-safe 0.0 bila API mati — lihat tes 1)"))

    # 4) scope_check — fail-safe True, nilai hanya informatif.
    in_scope = c.scope_check("How do I reset my FlowDesk API key?")
    results.append(("scope_check", None,
                    f"in_scope={in_scope} (fail-safe True bila API mati)"))

    print("-" * 64)
    for name, ok, detail in results:
        mark = {True: "PASS", False: "FAIL", None: "INFO"}[ok]
        print(f"[{mark}] {name:20s} {detail}")
    print("-" * 64)

    # Kesehatan API = tes 1 & 2 (satu-satunya yang tidak menelan error).
    healthy = results[0][1] is True and results[1][1] is True
    print("JEV API SEHAT" if healthy else "JEV API BERMASALAH — cek .env / "
          "konsol TypeSafe (key, kuota, nama model)")
    return 0 if healthy else 1


if __name__ == "__main__":
    sys.exit(main())
