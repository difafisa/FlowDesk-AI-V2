"""Tahap 3 — score_passages dengan fake jev (tanpa API asli):
cache mencegah panggilan ulang, chunk error tercatat tidak layak."""
from flowdesk.jev.passage_gate import score_passages


class FakeJev:
    """score_chunk dipetakan dari penanda di content: 'mark-1' -> skor 1, dst."""
    def __init__(self, fail_markers=()):
        self.fail_markers = fail_markers
        self.calls = []

    def score_chunk(self, question, passage):
        self.calls.append(passage)
        for m in self.fail_markers:
            if m in passage:
                raise ConnectionError("boom")
        if "mark-1" in passage:
            return {"is_relevant": 0.9, "contains_answer_evidence": 0.9,
                    "contains_prompt_injection": 0.05}
        return {"is_relevant": 0.2, "contains_answer_evidence": 0.1,
                "contains_prompt_injection": 0.0}


def _chunks(*marks):
    return [{"chunk_id": f"id-{m}", "document": "d", "content": f"teks {m}"}
            for m in marks]


def test_scores_all_chunks():
    jev = FakeJev()
    out = score_passages(jev, "q", _chunks("mark-1", "mark-2"))
    assert set(out) == {"id-mark-1", "id-mark-2"}
    assert out["id-mark-1"]["is_relevant"] == 0.9
    assert out["id-mark-1"]["ok"] is True


def test_cache_skips_already_scored():
    jev = FakeJev()
    cache = {"id-mark-1": {"is_relevant": 0.9, "contains_answer_evidence": 0.9,
                           "contains_prompt_injection": 0.05, "ok": True}}
    out = score_passages(jev, "q", _chunks("mark-1", "mark-2"), cache=cache)
    assert set(out) == {"id-mark-2"}              # hanya yang baru
    assert len(jev.calls) == 1                    # mark-1 tidak dinilai ulang


def test_all_cached_means_no_calls():
    jev = FakeJev()
    cache = {"id-mark-1": {"ok": True}}
    out = score_passages(jev, "q", _chunks("mark-1"), cache=cache)
    assert out == {} and jev.calls == []


def test_error_chunk_recorded_not_eligible():
    jev = FakeJev(fail_markers=("mark-1",))
    out = score_passages(jev, "q", _chunks("mark-1", "mark-2"))
    assert out["id-mark-1"]["ok"] is False
    assert out["id-mark-1"]["error"] == "ConnectionError"
    assert out["id-mark-1"]["is_relevant"] == 0.0   # tidak layak by default
