"""Tahap 0 — test JevClient dengan fake inner client, tanpa API asli.
Kontrak: Jev Noul -> probabilitas (0..1) -> tiga zona di KODE:
  noul >= 0.75            -> sufficient
  0.35 < noul < 0.75      -> uncertain (-> retry)
  noul <= 0.35            -> insufficient
API gagal/timeout          -> uncertain, parse_ok=False (fallback aman)."""
import os

import pytest
from flowdesk.jev.client import JevClient, JevDecision


class FakeAnswer:
    """Meniru jawaban Noul dari SDK: satu angka probabilitas 'yes'."""
    def __init__(self, noul):
        self.noul = noul


class FakeResponse:
    def __init__(self, answer):
        self.answers = {"sufficiency": answer}


class FakeClient:
    def __init__(self, answer=None, error=None):
        self.answer, self.error = answer, error

    def system_one(self, **kwargs):
        if self.error:
            raise self.error
        return FakeResponse(self.answer)


# --- Tiga zona threshold ---

def test_high_noul_is_sufficient():
    c = JevClient(inner=FakeClient(FakeAnswer(0.90)))
    d = c.decide("q", "ctx")
    assert (d.decision, d.parse_ok) == ("sufficient", True)


def test_sufficient_boundary_inclusive():
    c = JevClient(inner=FakeClient(FakeAnswer(0.75)))   # tepat di >= threshold
    d = c.decide("q", "ctx")
    assert d.decision == "sufficient"


def test_middle_noul_is_uncertain():
    c = JevClient(inner=FakeClient(FakeAnswer(0.50)))
    d = c.decide("q", "ctx")
    assert d.decision == "uncertain"


def test_insufficient_boundary_inclusive():
    c = JevClient(inner=FakeClient(FakeAnswer(0.35)))   # tepat di <= threshold
    d = c.decide("q", "ctx")
    assert d.decision == "insufficient"


def test_low_noul_is_insufficient():
    c = JevClient(inner=FakeClient(FakeAnswer(0.15)))
    d = c.decide("q", "ctx")
    assert d.decision == "insufficient"


def test_reason_contains_noul_value():
    c = JevClient(inner=FakeClient(FakeAnswer(0.90)))
    d = c.decide("q", "ctx")
    assert "noul=0.90" in d.reason      # trace gate harus bisa jelaskan 'mengapa'


# --- Fallback aman (prinsip sama dengan decision.py) ---

def test_timeout_falls_back_to_uncertain():
    c = JevClient(inner=FakeClient(error=TimeoutError()))
    d = c.decide("q", "ctx")
    assert (d.decision, d.parse_ok) == ("uncertain", False)
    assert "Timeout" in d.reason


def test_connection_error_falls_back_to_uncertain():
    c = JevClient(inner=FakeClient(error=ConnectionError()))
    d = c.decide("q", "ctx")
    assert (d.decision, d.parse_ok) == ("uncertain", False)
    assert d.reason.startswith("jev api failed")


# --- Fail-fast konfigurasi ---

def test_missing_api_key_fails_fast():
    old = os.environ.pop("TYPESAFE_API_KEY", None)
    try:
        with pytest.raises(RuntimeError):
            JevClient()          # tanpa inner -> harus raise, bukan diam-diam
    finally:
        if old:
            os.environ["TYPESAFE_API_KEY"] = old

def test_model_comes_from_config_not_hardcode():
    """JEV_MODEL harus dibaca dari config — satu-satunya tempat
    nama model tertulis adalah guardrails/config.py (kalibrasi/eksperimen
    mengganti model lewat config, bukan edit wrapper)."""
    import inspect
    import flowdesk.jev.client as client_mod
    from flowdesk.guardrails.config import JEV_MODEL

    src = inspect.getsource(client_mod)
    assert 'jev-latest' not in src and 'jev-1.13' not in src, \
        "client.py meng-hardcode nama model — pindahkan ke JEV_MODEL di config"

    # dan pemanggilan system_one memakai nilai dari config
    captured = {}
    class SpyClient:
        def system_one(self, **kw):
            captured.update(kw)
            class A: noul = 0.90
            class R: answers = {"sufficiency": A()}
            return R()

    JevClient(inner=SpyClient()).decide("q", "ctx")
    assert captured["model"] == JEV_MODEL, \
        "system_one harus dipanggil dengan model=JEV_MODEL dari config"
