"""Phase 6 T1+T2 — test export Langfuse (fake client v4, tanpa jaringan)."""
from flowdesk.observability.langfuse_export import (
    LangfuseExporter, with_langfuse, _TimedGraph, _pair_timings)


def make_state(trace=None, **over):
    state = {
        "question": "Berapa rate limit API Pro?", "answer": "42 req/menit",
        "status": "answered", "retries": 0,
        "context": "[1] Pro plan: 60 requests per minute.",
        "chunks": [
            {"chunk_id": "rate-1", "document": "api/rate-limits.md", "page": 3,
             "content": "Pro plan: 60 requests per minute.", "dist": 0.22},
            {"chunk_id": "rate-2", "document": "api/rate-limits.md", "page": 4,
             "content": "Billing cycle details.", "dist": 0.31},
        ],
        "scores": {
            "rate-1": {"is_relevant": 0.91, "contains_answer_evidence": 0.88,
                       "contains_prompt_injection": 0.02, "ok": True},
            "rate-2": {"is_relevant": 0.1, "contains_answer_evidence": 0.1,
                       "contains_prompt_injection": 0.0, "ok": False,
                       "error": "ReadTimeout"},
        },
        "trace": trace if trace is not None else [
            {"node": "retrieve", "k": 5, "n_chunks": 2},
            {"node": "jev_gate", "scored_this_wave": 2, "total_scored": 2},
            {"node": "generate", "status": "answered", "invalid_citations": []},
        ],
    }
    state.update(over)
    return state


class FakeSpan:
    """Meniru API observation langfuse v4; rekam hierarki tanpa jaringan."""
    tree = []    # (parent_name, name, as_type)
    spans = []   # semua span ever dibuat (untuk inspeksi output/model)

    def __init__(self, name, parent_name=None, as_type="span",
                 model=None, usage_details=None, metadata=None):
        self.name, self.parent_name = name, parent_name
        self.as_type, self.model, self.usage = as_type, model, usage_details
        self.metadata, self.output = metadata, None
        self.trace_id = f"tid-{name}"
        FakeSpan.tree.append((parent_name, name, as_type))
        FakeSpan.spans.append(self)

    def start_observation(self, name, as_type="span", model=None,
                          usage_details=None, **kw):
        return FakeSpan(name, parent_name=self.name, as_type=as_type,
                        model=model, usage_details=usage_details)

    def update(self, **kw):
        if "output" in kw:
            self.output = kw["output"]
        return self

    def end(self, **kw):
        return self


class FakeLangfuse:
    """Meniru client langfuse v4 (hanya bagian yang dipakai exporter)."""
    def __init__(self):
        self.flushed = False

    def start_observation(self, name, as_type="span", **kw):
        return FakeSpan(name, as_type=as_type, metadata=kw.get("metadata"))

    def flush(self):
        self.flushed = True


def _bare_exporter():
    return LangfuseExporter.__new__(LangfuseExporter)


def _reset_fakes():
    FakeSpan.tree = []
    FakeSpan.spans = []


# --- kriteria PRD: tanpa key -> no-op -----------------------------------

def test_noop_tanpa_key(monkeypatch):
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    ex = LangfuseExporter()
    assert ex.enabled is False
    assert ex.export_run(make_state()) is None


def test_wrapper_tanpa_key_hasil_dan_graph_tidak_berubah(monkeypatch):
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    g0 = object()
    captured = {}

    def runner(g, q):
        captured["graph"] = g
        return make_state()

    state = with_langfuse(runner)(g0, "q")
    assert captured["graph"] is g0       # tanpa key: graph asli, tanpa proxy
    assert state["status"] == "answered"
    assert "run_id" not in state


# --- kriteria PRD: span tersusun berjenjang -----------------------------

def test_export_membuat_span_berjenjang():
    _reset_fakes()
    root = FakeSpan("flowdesk.query")
    _reset_fakes()
    ex = _bare_exporter()
    ex._replay_trace(root, _pair_timings(make_state()["trace"], []),
                     make_state())
    assert [n for _, n, _ in FakeSpan.tree] == [
        "retrieve", "jev_gate", "generate"]
    assert all(p == "flowdesk.query" for p, _, _ in FakeSpan.tree)


def test_node_berulang_dapat_sufiks():
    _reset_fakes()
    root = FakeSpan("flowdesk.query")
    _reset_fakes()
    trace = [{"node": "retrieve", "k": 5}, {"node": "retry", "attempt": 1},
             {"node": "retrieve", "k": 10}]
    _bare_exporter()._replay_trace(root, _pair_timings(trace, []),
                                   make_state())
    assert [n for _, n, _ in FakeSpan.tree] == [
        "retrieve", "retry", "retrieve#2"]


# --- T2: durasi, generation, ringkasan chunk + gate ---------------------

def test_pair_timings_guardrail_tanpa_durasi():
    entries = [{"node": "input_validation"}, {"node": "retrieve"},
               {"node": "generate"}]
    timings = [("retrieve", 0.1), ("generate", 0.2)]
    paired = _pair_timings(entries, timings)
    assert paired[0][1] is None          # guardrail: di luar graph
    assert paired[1][1] == 0.1
    assert paired[2][1] == 0.2


def test_pair_timings_jumlah_tidak_konsisten_aman():
    paired = _pair_timings([{"node": "retrieve"}],
                           [("retrieve", 0.1), ("generate", 0.2)])
    assert paired == [({"node": "retrieve"}, None)]


def test_timedgraph_mengukur_durasi_per_node():
    class FakeGraph:
        def __init__(self, states):
            self.states = states

        def stream(self, init, stream_mode="values"):
            for s in self.states:
                yield s

    g = FakeGraph([
        {"trace": [{"node": "retrieve", "k": 5}]},
        {"trace": [{"node": "retrieve", "k": 5},
                   {"node": "generate", "status": "answered"}]},
    ])
    tg = _TimedGraph(g)
    final = tg.invoke({"trace": []})
    assert final["trace"][-1]["node"] == "generate"   # state akhir utuh
    assert [n for n, _ in tg.timings] == ["retrieve", "generate"]
    assert all(d >= 0 for _, d in tg.timings)


def test_generate_menjadi_generation_dengan_model_dan_usage(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "test-model")
    _reset_fakes()
    ex = _bare_exporter()
    ex._lf = FakeLangfuse()
    timings = [("retrieve", 0.1), ("jev_gate", 0.05), ("generate", 0.4)]
    run_id = ex.export_run(make_state(), timings=timings, total_s=0.55)

    assert run_id == "tid-flowdesk.query"
    gens = [s for s in FakeSpan.spans if s.as_type == "generation"]
    assert len(gens) == 1
    g = gens[0]
    assert g.model == "test-model"
    assert g.usage["total"] == g.usage["input"] + g.usage["output"]
    assert g.usage["input"] > 0 and g.usage["output"] > 0
    assert g.output["duration_s"] == 0.4
    assert g.output["answer_chars"] == len("42 req/menit")
    assert FakeSpan.spans[0].metadata["total_s"] == 0.55   # root metadata


def test_ringkasan_chunk_hanya_di_retrieve_terakhir_dan_gate_tercatat():
    _reset_fakes()
    ex = _bare_exporter()
    ex._lf = FakeLangfuse()
    trace = [{"node": "retrieve", "k": 5},
             {"node": "retry", "attempt": 1},
             {"node": "retrieve", "k": 10},
             {"node": "jev_gate", "scored_this_wave": 2, "total_scored": 2},
             {"node": "jev", "decision": "sufficient"},
             {"node": "generate", "status": "answered"}]
    timings = [("retrieve", 0.1), ("retry", 0.01), ("retrieve", 0.2),
               ("jev_gate", 0.9), ("jev", 0.05), ("generate", 0.4)]
    ex.export_run(make_state(trace=trace), timings=timings)

    spans = {s.name: s for s in FakeSpan.spans
             if s.parent_name == "flowdesk.query"}
    assert "chunks" not in spans["retrieve"].output
    chunks = spans["retrieve#2"].output["chunks"]
    assert chunks[0]["chunk_id"] == "rate-1"
    assert chunks[0]["document"] == "api/rate-limits.md"
    assert chunks[0]["dist"] == 0.22
    assert chunks[0]["retrieval_score"] == round(1 - 0.22, 4)   # 0.78
    assert chunks[0]["content_preview"].startswith("Pro plan: 60 requests")
    gate = spans["jev_gate"].output["gate"]
    assert gate["scores"]["rate-1"] == {"r": 0.91, "e": 0.88, "inj": 0.02}
    assert gate["chunk_errors"] == {"rate-2": "ReadTimeout"}


# --- kriteria PRD: fail-safe + run_id ------------------------------------

def test_export_error_tidak_melempar():
    ex = _bare_exporter()
    ex._lf = object()  # dianggap aktif
    ex._export = lambda *a, **kw: (_ for _ in ()).throw(
        RuntimeError("langfuse down"))
    assert ex.export_run(make_state()) is None


def test_wrapper_menambah_run_id(monkeypatch):
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    monkeypatch.setattr(LangfuseExporter, "_init",
                        lambda self: setattr(self, "_lf", object()))
    monkeypatch.setattr(LangfuseExporter, "export_run",
                        lambda self, state, **kw: "trace-abc")
    state = with_langfuse(lambda g, q: make_state())(object(), "q")
    assert state["run_id"] == "trace-abc"

def test_chunk_content_mode_none_dan_full(monkeypatch):
    ex = _bare_exporter()
    st = make_state()
    monkeypatch.setenv("LANGFUSE_CHUNK_CONTENT", "none")
    assert "content_preview" not in ex._chunk_summaries(st)[0]
    monkeypatch.setenv("LANGFUSE_CHUNK_CONTENT", "full")
    assert ex._chunk_summaries(st)[0]["content"] == "Pro plan: 60 requests per minute."
    monkeypatch.setenv("LANGFUSE_CHUNK_CONTENT", "preview")
    monkeypatch.setenv("LANGFUSE_PREVIEW_CHARS", "5")
    assert ex._chunk_summaries(st)[0]["content_preview"] == "Pro p…"


