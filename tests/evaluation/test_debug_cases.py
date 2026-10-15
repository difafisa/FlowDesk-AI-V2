"""Phase 6 T4 — test klasifikasi akar masalah (murni, tanpa I/O)."""
from flowdesk.evaluation.debug_cases import (
    classify_decision_miss, quality_flags, shared_miss_ids, analyze_variant)


def row(**over):
    base = {"id": "t1", "category": "cat", "decision": "abstained",
            "expected_decision": "answered", "hit@5": 1.0, "recall@5": 1.0,
            "groundedness": None, "correctness": None, "retried": False,
            "question": "q"}
    base.update(over)
    return base


def case(**over):
    base = {"id": "t1", "expected_decision": "answered"}
    base.update(over)
    return base


# --- klasifikasi decision-miss (spesifikasi PRD T4) -----------------------

def test_false_abstain_evidence_ada_gate_miss():
    # hit@5=1 tapi abstained -> threshold gate terlalu ketat (S1)
    assert classify_decision_miss(row(**{"hit@5": 1.0}), case()) == "gate_miss"


def test_false_abstain_evidence_tidak_ada_retrieval_miss():
    assert classify_decision_miss(row(**{"hit@5": 0.0}), case()) == "retrieval_miss"


def test_false_abstain_tanpa_baseline():
    assert (classify_decision_miss(row(**{"hit@5": None}), case())
            == "unknown_no_baseline")


def test_expected_answered_got_escalated_scope_miss():
    assert classify_decision_miss(row(decision="escalated"), case()) == "scope_miss"


def test_expected_abstained_got_answered_too_loose():
    assert (classify_decision_miss(row(decision="answered"),
                                   case(expected_decision="abstained"))
            == "gate_too_loose")


def test_expected_escalated_got_abstained_scope_miss():
    # pola ds-044: scope_check True padahal seharusnya escalate
    assert (classify_decision_miss(row(decision="abstained"),
                                   case(expected_decision="escalated"))
            == "scope_miss")


def test_expected_abstained_got_escalated_scope_miss():
    # pola llm-judge di kategori ambiguous: harusnya abstain, malah escalate
    assert (classify_decision_miss(row(decision="escalated"),
                                   case(expected_decision="abstained"))
            == "scope_miss")


# --- quality flags ---------------------------------------------------------

def test_quality_flags_groundedness_dan_correctness():
    r = row(groundedness=0.41, correctness="wrong")
    assert quality_flags(r) == ["low_groundedness(0.41)", "correctness_wrong"]
    assert quality_flags(row(groundedness=0.9)) == []


# --- shared miss & label changed -------------------------------------------

def test_shared_miss_ids_irisan():
    a = [{"id": "x"}, {"id": "y"}]
    b = [{"id": "y"}, {"id": "z"}]
    assert shared_miss_ids(a, b) == {"y"}


def test_analyze_variant_label_changed_menyesuaikan_label_kini():
    # ds-9: label lama escalated, label kini answered, decision answered
    # -> bukan miss lagi, tapi tercatat sebagai label_changed
    rows = [row(id="ds-9", decision="answered", expected_decision="escalated")]
    cases = {"ds-9": {"id": "ds-9", "expected_decision": "answered"}}
    out = analyze_variant(rows, cases)
    assert out["misses"] == []
    assert out["label_changed"] == [("ds-9", "escalated", "answered")]


def test_analyze_variant_kualitas_hanya_jika_keputusan_benar():
    rows = [row(id="q1", decision="answered", expected_decision="answered",
                groundedness=0.5)]
    cases = {"q1": {"id": "q1", "expected_decision": "answered"}}
    out = analyze_variant(rows, cases)
    assert out["misses"] == []
    assert out["quality"][0]["flags"] == ["low_groundedness(0.5)"]
