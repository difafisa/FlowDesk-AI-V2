"""PRD Phase 04 Tahap 4 — keputusan di KODE, tanpa API call.

Mengubah skor passage gate menjadi keputusan yang dipahami router:
sufficient | uncertain | insufficient | need_more.
Semua angka starting point (cookbook TypeSafe) — kalibrasi ulang
wajib dengan data benchmark lokal.
"""
from flowdesk.guardrails.config import JEV_GATE_THRESHOLDS


def decide_sufficiency(scores: dict[str, dict],
                       thresholds: dict = None,
                       unscored_left: int = 0) -> dict:
    """scores: {chunk_id: {is_relevant, contains_answer_evidence,
    contains_prompt_injection, ok}}. Pure — mudah dites dengan tabel.

    Aturan:
    - chunk gagal dinilai (ok=False)          -> dibuang (score_error)
    - injection > injection_discard           -> dibuang (injection)
    - layak (include) = relevant >= relevant_min
                        AND evidence >= evidence_min
    - ada yang layak -> sufficient (+ daftar included utk context)
    - belum sufficient & ada chunk belum terskor -> need_more (gelombang berikutnya)
    - tidak ada layak, tapi ada relevan saja -> uncertain
    - semua tidak relevan -> insufficient
    """
    t = thresholds or JEV_GATE_THRESHOLDS
    eligible, relevant_only, discarded = [], [], []

    for cid, s in scores.items():
        if not s.get("ok", False):
            discarded.append((cid, "score_error"))
            continue
        if s["contains_prompt_injection"] > t["injection_discard"]:
            discarded.append((cid, "injection"))
            continue
        if (s["is_relevant"] >= t["relevant_min"]
                and s["contains_answer_evidence"] >= t["evidence_min"]):
            eligible.append(cid)
        elif s["is_relevant"] >= t["relevant_min"]:
            relevant_only.append(cid)

    if eligible:
        decision = "sufficient"
    elif unscored_left > 0:
        decision = "need_more"
    elif relevant_only:
        decision = "uncertain"
    else:
        decision = "insufficient"

    return {
        "decision": decision,
        "included": eligible,
        "relevant_only": relevant_only,
        "discarded": [cid for cid, _ in discarded],
        "discard_reasons": dict(discarded),
    }
