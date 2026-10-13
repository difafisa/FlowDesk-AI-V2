"""S1 — test simulasi sweep threshold (murni, tanpa I/O)."""
from flowdesk.evaluation.calibrate_thresholds import simulate, sweep, BASE


def sc(cid, r, e, inj=0.0, ok=True):
    return {cid: {"is_relevant": r, "contains_answer_evidence": e,
                  "contains_prompt_injection": inj, "ok": ok}}


def test_simulate_sufficient_dengan_evidence_kuat():
    scores = sc("c1", 0.9, 0.9)
    assert simulate(scores, BASE, 0.90, 0.75) == "sufficient"


def test_simulate_evidence_lemah_direscue_oleh_threshold_baru():
    scores = sc("c1", 0.9, 0.48)                     # di bawah 0.55, di atas 0.45
    assert simulate(scores, BASE, 0.90, 0.75) == "uncertain"
    th_loose = {**BASE, "evidence_min": 0.45}
    assert simulate(scores, th_loose, 0.90, 0.75) == "sufficient"



def test_simulate_completeness_rendah_menurunkan_ke_uncertain():
    scores = sc("c1", 0.9, 0.9)
    assert simulate(scores, BASE, 0.60, 0.75) == "uncertain"
    assert simulate(scores, BASE, 0.60, 0.55) == "sufficient"


def test_sweep_menandai_rescued_dangerous_dan_regressed():
    rows = [
        # dulu abstain, evidence nyaris lolos, expected answered -> bisa diselamatkan
        {"id": "a", "decision": "abstained", "expected_decision": "answered",
         "gate_scores": sc("c1", 0.9, 0.48), "completeness": 0.90},
        # expected abstained, evidence kuat -> bahaya kalau threshold dilonggarkan
        {"id": "b", "decision": "abstained", "expected_decision": "abstained",
         "gate_scores": sc("c2", 0.9, 0.48), "completeness": 0.90},
        # dulu answered, expected answered, evidence sangat kuat -> tetap aman
        {"id": "c", "decision": "answered", "expected_decision": "answered",
         "gate_scores": sc("c3", 0.9, 0.90), "completeness": 0.90},
    ]
    rep = sweep(rows, [0.45], [0.75])[0]
    assert rep["rescued"] == ["a"]
    assert rep["dangerous"] == ["b"]
    assert rep["regressed"] == []
