"""Tests routing Tahap 4 (deterministic, tanpa API call)."""
from flowdesk.graph.workflow import route_after_jev

def test_routing_sufficient_generate():
    assert route_after_jev({"jev": {"decision": "sufficient"}, "retries": 0}) == "generate"

def test_routing_uncertain_retries_then_abstains():
    assert route_after_jev({"jev": {"decision": "uncertain"}, "retries": 0}) == "retry_retrieve"
    assert route_after_jev({"jev": {"decision": "uncertain"}, "retries": 1}) == "abstain"

def test_routing_need_more_retries_then_abstains():
    assert route_after_jev({"jev": {"decision": "need_more"}, "retries": 0}) == "retry_retrieve"
    assert route_after_jev({"jev": {"decision": "need_more"}, "retries": 1}) == "abstain"

def test_routing_insufficient_in_scope_abstains():
    # topik produk valid, KB yang tidak punya -> abstain (bukan bebankan manusia)
    assert route_after_jev({"jev": {"decision": "insufficient", "in_scope": True},
                            "retries": 0}) == "abstain"

def test_routing_insufficient_out_of_scope_escalates():
    assert route_after_jev({"jev": {"decision": "insufficient", "in_scope": False},
                            "retries": 0}) == "escalate"

def test_routing_insufficient_default_in_scope_safe():
    # kalau scope_check gagal dipanggil, default aman = abstain
    assert route_after_jev({"jev": {"decision": "insufficient"}, "retries": 0}) == "abstain"
