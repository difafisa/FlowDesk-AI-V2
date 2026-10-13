"""Phase 6 T1+T2 — Export trace Flowdesk ke Langfuse (lapisan luar, fail-safe).

Prinsip desain (sesuai PRD):
- workflow.py TIDAK disentuh. Pemakaian:
      run_query = with_langfuse(run_workflow)                    # tanpa sesi
      run_query = with_langfuse(run_workflow, session_id="cli-x") # dengan sesi
      state = run_query(graph, question)
- Tanpa paket / tanpa key -> no-op murni; graph ASLI yang dipakai.
- Langfuse down / error apa pun -> dicatat di log, query TETAP sah.
- Satu run = satu trace; tiap entri state["trace"] jadi satu span.

T2 (pengayaan, tetap tanpa menyentuh workflow.py):
- Durasi tiap node NYATA: graph dipanggil lewat proxy _TimedGraph yang
  menjalankan invoke() via stream("values") — durasi antar yield = durasi node.
- Node generate diekspor sebagai observation bertipe "generation"
  (model + usage_details aproksimasi + answer_chars) -> panel Model usage terisi.
- Span retrieve terakhir membawa ringkasan chunk (chunk_id, document, page, dist).
- Span jev_gate membawa skor gate per chunk + chunk_errors (insiden seperti
  403 TypeSafe langsung terlihat akar masalahnya).
- tags=[status] + session_id via propagate_attributes (SDK v4).

Batasan yang disengaja: span tetap dibuat pasca-run (replay), jadi kolom
latensi di panel agregat ~0; durasi nyata terekam di field duration_s tiap
span (dan total_s di root).
"""
from __future__ import annotations

import logging
import os
import time
from contextlib import nullcontext
from typing import Callable

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://cloud.langfuse.com"


class _TimedGraph:
    """Proxy graph — invoke() dijalankan lewat stream("values") supaya durasi
    tiap node terukur, TANPA mengubah workflow.py.

    Asumsi (berlaku untuk graph Flowdesk): graph linear dan setiap node
    menambah tepat satu entri state["trace"] — entri baru antar dua yield
    konsisten dengan satu langkah node.
    """

    def __init__(self, graph):
        self._graph = graph
        self.timings: list[tuple[str, float]] = []   # [(node, durasi_s)]

    def invoke(self, init):
        try:
            it = self._graph.stream(init, stream_mode="values")
        except AttributeError:          # graph tanpa .stream -> jalur lama
            return self._graph.invoke(init)

        final = None
        seen = 0
        t_step = time.perf_counter()
        for value in it:
            final = value
            tr = value.get("trace", []) if isinstance(value, dict) else []
            if len(tr) > seen:
                now = time.perf_counter()
                for entry in tr[seen:]:
                    self.timings.append(
                        (str(entry.get("node", "?")), now - t_step))
                seen = len(tr)
                t_step = now
        if final is None:               # stream kosong -> fallback invoke
            final = self._graph.invoke(init)
        return final


def _pair_timings(entries: list, timings: list) -> list:
    """Pasangkan entri trace dengan durasi.

    Entri guardrail (input_validation, injection_filter) dibuat SEBELUM graph
    berjalan -> tidak punya durasi. Entri graph adalah N entri TERAKHIR,
    N = len(timings). Jika jumlah tidak konsisten, durasi diabaikan.
    """
    if not timings or len(timings) > len(entries):
        return [(e, None) for e in entries]
    head = len(entries) - len(timings)
    return ([(e, None) for e in entries[:head]]
            + [(e, d) for e, (_n, d) in zip(entries[head:], timings)])


class LangfuseExporter:
    """Mengirim satu run workflow sebagai satu trace Langfuse."""

    def __init__(self) -> None:
        self._lf = None
        self._disabled_reason = ""
        self._init()

    # -- setup ---------------------------------------------------------

    def _init(self) -> None:
        try:
            from langfuse import Langfuse  # import lokal: paket opsional
        except ImportError:
            self._disabled_reason = "paket 'langfuse' tidak terpasang"
            return

        public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip()
        secret_key = os.getenv("LANGFUSE_SECRET_KEY", "").strip()
        if not public_key or not secret_key:
            self._disabled_reason = "LANGFUSE_PUBLIC_KEY/SECRET_KEY tidak diset"
            return

        # v4: LANGFUSE_BASE_URL (resmi); LANGFUSE_HOST hanya fallback lama.
        base_url = (os.getenv("LANGFUSE_BASE_URL", "").strip()
                    or os.getenv("LANGFUSE_HOST", "").strip()
                    or DEFAULT_BASE_URL)
        try:
            self._lf = Langfuse(public_key=public_key,
                                secret_key=secret_key, base_url=base_url)
        except Exception as exc:
            self._disabled_reason = f"inisialisasi gagal: {exc}"

    @property
    def enabled(self) -> bool:
        return self._lf is not None

    # -- API utama -------------------------------------------------------

    def export_run(self, state: dict, timings: list | None = None,
                   session_id: str | None = None,
                   total_s: float | None = None) -> str | None:
        """Export satu state hasil run_workflow sebagai satu trace.

        Return trace id Langfuse (jadi 'run_id' untuk feedback T3),
        atau None bila nonaktif/gagal — TIDAK pernah melempar exception.
        """
        if not self.enabled:
            return None
        try:
            return self._export(state, timings or [], session_id, total_s)
        except Exception:
            logger.exception("Export Langfuse gagal — diabaikan, run tetap sah")
            return None

    def _export(self, state: dict, timings: list, session_id, total_s):
        lf = self._lf
        status = str(state.get("status", "") or "unknown")
        meta = {"status": status, "retries": state.get("retries", 0)}
        if total_s is not None:
            meta["total_s"] = round(total_s, 3)

        try:
            from langfuse import propagate_attributes
            ctx = propagate_attributes(tags=[status], session_id=session_id,
                                       trace_name="flowdesk.query")
        except ImportError:    # SDK sangat lama — ekspor tetap jalan tanpa tags
            ctx = nullcontext()

        with ctx:
            root = lf.start_observation(
                name="flowdesk.query", as_type="span",
                input=state.get("question", ""), metadata=meta)
            try:
                self._replay_trace(
                    root, _pair_timings(state.get("trace", []), timings), state)
                root.update(output=state.get("answer", ""))
            finally:
                root.end()

        lf.flush()
        return root.trace_id

    def _replay_trace(self, root, paired: list, state: dict) -> None:
        """Tiap entri trace -> satu span di bawah root.

        Node berulang (retry) dapat sufiks #2, #3. Entri tidak dimutasi.
        """
        seen: dict = {}
        entries = [e for e, _ in paired]
        last_retrieve = max(
            (i for i, e in enumerate(entries) if e.get("node") == "retrieve"),
            default=None)

        for idx, (entry, dur) in enumerate(paired):
            node = str(entry.get("node", "unknown"))
            seen[node] = seen.get(node, 0) + 1
            name = node if seen[node] == 1 else f"{node}#{seen[node]}"
            payload = {k: v for k, v in entry.items() if k != "node"}
            if dur is not None:
                payload["duration_s"] = round(dur, 3)

            if idx == last_retrieve:
                payload["chunks"] = self._chunk_summaries(state)
            level = None

            if node == "jev_gate":
                gate = self._gate_summary(state)
                if gate:
                    payload["gate"] = gate
                    if gate["chunk_errors"]:
                        level = "ERROR"   # insiden API Jev terlihat merah di dashboard

            if node == "generate":
                payload["answer_chars"] = len(str(state.get("answer", "")))
                payload["tokens_approx"] = True
                span = root.start_observation(
                    name=name, as_type="generation", model=self._model_name(),
                    usage_details=self._usage_details(state), level=level)
            else:
                span = root.start_observation(name=name, as_type="span",
                                              level=level)

            span.update(output=payload)
            span.end()

    # -- ringkasan data (dari state akhir; workflow.py tak disentuh) -----

    def _model_name(self) -> str:
        return os.getenv("LLM_MODEL", "gpt-4o-mini")

    def _usage_details(self, state: dict) -> dict:
        """Token aproksimasi — LLMClient belum mengembalikan usage asli."""
        from flowdesk.guardrails.tokens import approx_tokens
        inp = int(approx_tokens(
            f"{state.get('question', '')}\n{state.get('context', '')}"))
        out = int(approx_tokens(state.get("answer", "")))
        return {"input": inp, "output": out, "total": inp + out}

    def _chunk_summaries(self, state: dict) -> list:
        """Ringkasan chunk gelombang terakhir — cukup untuk debugging.

        - retrieval_score = 1 - dist (cosine similarity: makin besar makin
          relevan); dist mentah tetap disertakan utk debugging pgvector.
        - content_preview: potongan awal content (default 200 char), bukan
          isi penuh — cukup menilai relevansi tanpa membanjiri trace.
          Kontrol via env:
            LANGFUSE_CHUNK_CONTENT = preview (default) | full | none
            LANGFUSE_PREVIEW_CHARS = 200
        """
        mode = os.getenv("LANGFUSE_CHUNK_CONTENT", "preview").strip().lower()
        n = int(os.getenv("LANGFUSE_PREVIEW_CHARS", "200"))
        out = []
        for c in state.get("chunks", []):
            d = c.get("dist")
            item = {"chunk_id": c.get("chunk_id"),
                    "document": c.get("document"),
                    "page": c.get("page"),
                    "dist": round(d, 4) if isinstance(d, (int, float))
                    else None}
            if isinstance(d, (int, float)):
                item["retrieval_score"] = round(1.0 - d, 4)
            if mode == "full":
                item["content"] = c.get("content")
            elif mode != "none":
                text = str(c.get("content") or "").strip().replace("\n", " ")
                item["content_preview"] = (text[:n] + "…") if len(text) > n \
                    else text
            out.append(item)
        return out


    def _gate_summary(self, state: dict) -> dict | None:
        """Skor gate per chunk + chunk yang gagal dinilai (error)."""
        scores = state.get("scores") or {}
        ok, errs = {}, {}
        for cid, s in scores.items():
            if not s.get("ok", True):
                errs[cid] = s.get("error", "?")
            else:
                ok[cid] = {"r": round(s.get("is_relevant", 0.0), 2),
                           "e": round(s.get("contains_answer_evidence", 0.0), 2),
                           "inj": round(s.get("contains_prompt_injection", 0.0), 2)}
        if not ok and not errs:
            return None
        return {"scores": ok, "chunk_errors": errs}


def with_langfuse(runner: Callable, session_id: str | None = None):
    """Bungkus run_workflow (runner berformat (graph, question) -> state).

    - Tanpa key/paket: hasil PERSIS sama — graph asli dipakai, tanpa proxy.
    - Dengan key: state ditambah key 'run_id' (trace id Langfuse).
    - session_id: grup beberapa query jadi satu sesi di panel Sessions.
    """
    exporter = LangfuseExporter()
    if not exporter.enabled and exporter._disabled_reason:
        logger.info("Langfuse export nonaktif: %s", exporter._disabled_reason)

    def wrapped(graph, question: str):
        if not exporter.enabled:
            return runner(graph, question)
        timed = _TimedGraph(graph)
        t0 = time.perf_counter()
        state = runner(timed, question)
        total_s = time.perf_counter() - t0
        run_id = exporter.export_run(state, timings=timed.timings,
                                     session_id=session_id, total_s=total_s)
        if run_id:
            state = dict(state)
            state["run_id"] = run_id
        return state

    return wrapped
