"""PRD Phase 04 — JevClient: wrapper ke TypeSafe (Jev asli, System One).

Satu-satunya jalur keputusan evidence-sufficiency. Jev-LLM lama
(decision.py, prompt JSON + regex parse) sudah DIHAPUS — diganti
Noul asli: P(evidence cukup) terkalibrasi, tanpa parsing teks.
Kontrak:
- Balik JevDecision: decision + reason + parse_ok (= API call sukses).
- Tiga zona di KODE (probability-gated routing, bukan di model):
    noul >= noul_sufficient   -> sufficient  (generate)
    noul <= noul_insufficient -> insufficient (escalate, tanpa retry)
    di antaranya              -> uncertain  (retry K=10)
- API gagal/timeout -> JevDecision("uncertain", ..., parse_ok=False).
  Fallback aman: uncertain memicu retry, tidak pernah menjawab
  dengan evidence yang belum dinilai.
- inner injectable -> test tanpa memanggil API asli.
"""
import os
from dataclasses import dataclass

from flowdesk.guardrails.config import JEV_MODEL, JEV_TIMEOUT_S, JEV_THRESHOLDS


@dataclass
class JevDecision:
    decision: str          # sufficient | uncertain | insufficient
    reason: str
    parse_ok: bool         # True = Jev asli menjawab; False = fallback fail-safe


# Satu judgment sempit: apakah evidence cukup menjawab pertanyaan?
# Noul menilai PERNYATAAN (bukan pertanyaan). Instructions bahasa Inggris
# (bahasa pelatihan utama Jev); state tetap berisi teks KB apa adanya.
JEV_SUFFICIENCY_QUESTION = {
    "type": "noul",
    "instructions": (
        "The evidence in `evidence_blocks` directly and completely answers "
        "`question`. Structured records (plan/price rows) are valid evidence "
        "for pricing/feature questions."
    ),
    # criteria opsional untuk Noul: klarifikasi makna yes/no
    "criteria": {
        "yes": "Evidence contains the specific information the question asks for",
        "no": "Evidence is missing key information the question asks for, "
              "or does not address it",
    },
}


class JevClient:
    def __init__(self, inner=None):
        if inner is not None:
            self.inner = inner          # fake utk test
            return
        if not os.environ.get("TYPESAFE_API_KEY"):
            raise RuntimeError(
                "TYPESAFE_API_KEY belum diset di environment/.env")
        from typesafe_sdk import TypeSafeClient
        self.inner = TypeSafeClient(timeout=JEV_TIMEOUT_S)

    def decide(self, question: str, context: str) -> JevDecision:
        """Satu panggilan Jev -> keputusan evidence sufficiency."""
        try:
            resp = self.inner.system_one(
                state={"question": question, "evidence_blocks": context},
                model=JEV_MODEL,
                questions={"sufficiency": JEV_SUFFICIENCY_QUESTION},
            )
        except Exception as e:   # timeout, koneksi, auth, 5xx -> fail-safe
            return JevDecision(
                "uncertain", f"jev api failed: {type(e).__name__}", False)

        p = resp.answers["sufficiency"].noul     # probabilitas "yes" (0..1)

        # Zona routing dihitung di KODE (probability-gated, bukan di model)
        if p >= JEV_THRESHOLDS["noul_sufficient"]:
            decision = "sufficient"
        elif p <= JEV_THRESHOLDS["noul_insufficient"]:
            decision = "insufficient"
        else:
            decision = "uncertain"

        reason = f"noul={p:.2f} -> {decision}"
        return JevDecision(decision, reason, True)
