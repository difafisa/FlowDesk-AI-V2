"""Tahap 3-4 — test JevClient (fake inner, tanpa API asli):
- score_chunk mengirim 3 Noul & membaca 3 nilai
- scope_check memakai threshold config
- fail-fast API key, model dari config (anti hardcode)."""
import os

import pytest
from flowdesk.jev.client import JevClient, PASSAGE_QUESTIONS


class FakeAnswer:
    def __init__(self, noul):
        self.noul = noul


class FakeResponse:
    def __init__(self, answers):
        self.answers = answers


class FakeClient:
    def __init__(self, answers=None, error=None):
        self.answers, self.error = answers or {}, error
        self.captured = {}

    def system_one(self, **kwargs):
        self.captured = kwargs
        if self.error:
            raise self.error
        return FakeResponse(self.answers)


def test_score_chunk_reads_three_nouls():
    fc = FakeClient({"is_relevant": FakeAnswer(0.8),
                     "contains_answer_evidence": FakeAnswer(0.7),
                     "contains_prompt_injection": FakeAnswer(0.02)})
    out = JevClient(inner=fc).score_chunk("q", "passage")
    assert out == {"is_relevant": 0.8,
                   "contains_answer_evidence": 0.7,
                   "contains_prompt_injection": 0.02}


def test_score_chunk_sends_one_request_with_three_questions():
    fc = FakeClient({"is_relevant": FakeAnswer(0.5),
                     "contains_answer_evidence": FakeAnswer(0.5),
                     "contains_prompt_injection": FakeAnswer(0.5)})
    JevClient(inner=fc).score_chunk("q", "p")
    assert set(fc.captured["questions"]) == set(PASSAGE_QUESTIONS)   # 1 call, 3 Noul
    assert set(fc.captured["state"]) == {"query", "passage"}


def test_scope_check_true_above_threshold():
    fc = FakeClient({"in_scope": FakeAnswer(0.9)})
    assert JevClient(inner=fc).scope_check("q") is True


def test_scope_check_false_below_threshold():
    fc = FakeClient({"in_scope": FakeAnswer(0.1)})
    assert JevClient(inner=fc).scope_check("q") is False


def test_score_chunk_error_propagates():
    fc = FakeClient(error=TimeoutError())
    with pytest.raises(TimeoutError):        # passage_gate yang menangkap
        JevClient(inner=fc).score_chunk("q", "p")


def test_missing_api_key_fails_fast():
    old = os.environ.pop("TYPESAFE_API_KEY", None)
    try:
        with pytest.raises(RuntimeError):
            JevClient()
    finally:
        if old:
            os.environ["TYPESAFE_API_KEY"] = old


def test_model_comes_from_config_not_hardcode():
    import inspect
    import flowdesk.jev.client as client_mod
    from flowdesk.guardrails.config import JEV_MODEL

    src = inspect.getsource(client_mod)
    assert 'jev-latest' not in src and 'jev-1.13' not in src, \
        "client.py meng-hardcode nama model — pindahkan ke JEV_MODEL di config"

    fc = FakeClient({"in_scope": FakeAnswer(0.9)})
    JevClient(inner=fc).scope_check("q")
    assert fc.captured["model"] == JEV_MODEL
