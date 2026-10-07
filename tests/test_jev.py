"""Tests Jev routing di graph (deterministic, tanpa API call).
Test jev_decide (Jev-LLM lama) dihapus bersama kodenya —
keputusan sekarang lewat JevClient (tests/test_jev_client.py)."""
from flowdesk.graph.workflow import route_after_jev

def test_routing_sufficient_generate():
    assert route_after_jev({"jev": {"decision": "sufficient"}, "retries": 0}) == "generate"

def test_routing_uncertain_retries_then_abstains():
    assert route_after_jev({"jev": {"decision": "uncertain"}, "retries": 0}) == "retry_retrieve"
    assert route_after_jev({"jev": {"decision": "uncertain"}, "retries": 1}) == "abstain"

def test_routing_insufficient_escalates():
    assert route_after_jev({"jev": {"decision": "insufficient"}, "retries": 0}) == "escalate"
