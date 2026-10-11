"""PRD Phase 05 — generation scorer: groundedness + correctness.

Dipanggil HANYA oleh evaluator (di luar graph) — production tak berubah.
- Groundedness (Noul): P(setiap klaim faktual di jawaban didukung evidence)
  -> anti-halusinasi meter, diukur utk SEMUA jawaban.
- Correctness (Choice correct/partial/wrong): hanya bila kasus punya
  expected_answer — substansi vs referensi, bukan kata per kata.
Dua pertanyaan, SATU request (fan-out paralel di server TypeSafe).
API gagal -> scored=False, kasus dikeluarkan dari metrik generation.
"""
from flowdesk.guardrails.config import JEV_MODEL

GROUNDING_QUESTION = {
    "type": "noul",
    "instructions": (
        "Every factual claim in `answer` is directly supported by the "
        "passages in `evidence`. An answer that adds facts, numbers, or "
        "product capabilities not present in `evidence` is not fully "
        "grounded. Judge claims, not wording or language."
    ),
}

CORRECTNESS_QUESTION = {
    "type": "choice",
    "instructions": (
        "Does `answer` agree with `reference` on every factual point? "
        "Judge substance, not wording or language. Wording differences "
        "that keep the same facts are still correct."
    ),
    "criteria": {
        "correct": "All factual points match the reference",
        "partial": "Some points match, others are missing or wrong",
        "wrong":   "Main facts contradict or are absent from the reference",
    },
}


def score_answer(jev, answer: str, evidence: str,
                 reference: str | None = None) -> dict:
    """Return {scored, groundedness, correctness, error}.
    Jawaban kosong (abstain/escalate/blocked) tidak dinilai."""
    if not answer or not answer.strip():
        return {"scored": False, "groundedness": None,
                "correctness": None, "error": "no_answer"}

    questions = {"groundedness": GROUNDING_QUESTION}
    if reference:
        questions["correctness"] = CORRECTNESS_QUESTION

    resp = jev.judge(
        state={"answer": answer, "evidence": evidence},
        questions=questions,
    )
    if resp is None:
        return {"scored": False, "groundedness": None,
                "correctness": None, "error": "api_failed"}

    out = {"scored": True, "error": "",
           "groundedness": resp["groundedness"].noul}
    out["correctness"] = (resp["correctness"].choice
                          if "correctness" in resp else None)
    return out
