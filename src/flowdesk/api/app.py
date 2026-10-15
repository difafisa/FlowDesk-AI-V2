"""Phase 7 (PRD) — FastAPI backend: /ask, /feedback, /health.

Endpoint:
  POST /ask       -> satu query lewat workflow LangGraph+Jev
  POST /feedback  -> 👍/👎 ke Postgres + score Langfuse (fail-safe)
  GET  /health    -> status DB + komponen (untuk docker healthcheck)

Prinsip yang dijaga (selaras PRD 3.7):
- API tetap TIPIS: semua aturan bisnis (validasi input, injection filter,
  abstain/escalate) tetap di workflow — endpoint hanya transport.
- Tidak mengubah workflow.py / observability / rag — wiring murni dari
  luar, sama seperti scripts/ask.py.
- Testable: create_app(graph=..., feedback_store=...) mengikuti pola
  injeksi FakeLLM/FakeJev/FakeRetriever yang sudah dipakai tests/.

Catatan konkurensi (MVP, disengaja):
- VectorStore & FeedbackStore masing-masing memegang SATU koneksi psycopg
  (psycopg connection tidak thread-safe). Karena itu /ask dan /feedback
  diserialisasi dengan lock dan uvicorn dijalankan single-worker.
  Improvement post-MVP: connection pool (lihat BACKLOG).
"""
from __future__ import annotations

import logging
import os
import threading
import time
import uuid
from collections import OrderedDict
from contextlib import asynccontextmanager
from typing import Callable

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()   # baca .env di root — sama seperti scripts/ask.py

from flowdesk.api.schemas import (AskRequest, AskResponse, FeedbackRequest,
                                  FeedbackResponse, HealthResponse, JevOut,
                                  SourceOut)
from flowdesk.graph.workflow import build_graph, run_workflow
from flowdesk.observability.feedback import FeedbackStore
from flowdesk.observability.langfuse_export import with_langfuse

logger = logging.getLogger(__name__)

DEFAULT_DSN = "postgresql://flowdesk:flowdesk@localhost:5432/flowdesk"

_ask_lock = threading.Lock()      # satu koneksi pgvector di dalam graph
_fb_lock = threading.Lock()       # satu koneksi psycopg di FeedbackStore


def make_graph():
    """Wiring dependensi produksi — identik dengan scripts/ask.py, hanya
    DSN via env (FLOWDESK_PG_DSN). Import berat (torch/sentence-transformers)
    sengaja DI DALAM fungsi supaya `import flowdesk.api.app` tetap murah."""
    from flowdesk.embedding.embedder import Embedder
    from flowdesk.jev.client import JevClient
    from flowdesk.rag.llm_client import LLMClient
    from flowdesk.retrieval.retriever import Retriever
    from flowdesk.storage.pgvector_store import VectorStore

    llm = LLMClient(
        base_url=os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"),
        model=os.environ.get("LLM_MODEL", "gpt-4o-mini"),
    )
    store = VectorStore(os.getenv("FLOWDESK_PG_DSN", DEFAULT_DSN))
    return build_graph(llm, JevClient(), Retriever(store, Embedder()))


class _RunnerCache:
    """LRU kecil: satu wrapper with_langfuse per session_id.

    with_langfuse(runner, session_id) membuat LangfuseExporter (dan client
    Langfuse) per panggilan — tanpa cache, tiap request = satu client baru.
    Dibatasi 32 entri supaya resource terkendali tanpa menyentuh
    observability/langfuse_export.py.
    """

    def __init__(self, maxsize: int = 32):
        self._d: OrderedDict[str, Callable] = OrderedDict()
        self._max = maxsize
        self._lock = threading.Lock()

    def get(self, session_id: str | None) -> Callable:
        key = session_id or "default"
        with self._lock:
            if key in self._d:
                self._d.move_to_end(key)
                return self._d[key]
            runner = with_langfuse(run_workflow, session_id=session_id)
            self._d[key] = runner
            while len(self._d) > self._max:
                self._d.popitem(last=False)
            return runner


_runners = _RunnerCache()


def _db_ok() -> bool:
    """Koneksi baru ringan SELECT 1 — tidak lewat store mana pun."""
    try:
        import psycopg
        with psycopg.connect(os.getenv("FLOWDESK_PG_DSN", DEFAULT_DSN),
                             connect_timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True
    except Exception:
        return False


def _langfuse_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY", "").strip()
                and os.getenv("LANGFUSE_SECRET_KEY", "").strip())


def create_app(graph=None, feedback_store=None) -> FastAPI:
    """Factory app. graph/feedback_store bisa di-inject untuk test."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Graph + Embedder (model torch) dibangun SEKALI per proses —
        # memuatnya per-request akan membuang puluhan detik tiap query.
        app.state.graph = graph if graph is not None else make_graph()
        if feedback_store is not None:
            app.state.feedback = feedback_store
        else:
            try:
                app.state.feedback = FeedbackStore()
            except Exception:
                logger.exception("FeedbackStore gagal init (DB down?) "
                                 "— /feedback akan 503")
                app.state.feedback = None
        logger.info("FlowDesk API siap (llm=%s, langfuse=%s)",
                    os.getenv("LLM_MODEL", "-"), _langfuse_enabled())
        yield

    app = FastAPI(title="FlowDesk v2 — AI Support Assistant",
                  version="0.2.0", lifespan=lifespan)

    # Dev: frontend lokal di port apa pun. (Bila frontend diserve oleh app
    # ini sendiri via mount di bawah, CORS tidak terpakai — tetap aman.)
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        allow_methods=["*"], allow_headers=["*"])

    # ------------------------------------------------------------------ /ask
    @app.post("/ask", response_model=AskResponse)
    def ask(req: AskRequest) -> AskResponse:
        runner = _runners.get(req.session_id)
        t0 = time.perf_counter()
        try:
            with _ask_lock:            # lihat catatan konkurensi (docstring)
                state = runner(app.state.graph, req.question)
        except Exception:
            logger.exception("Workflow gagal memproses query")
            raise HTTPException(status_code=502,
                                detail="workflow error (lihat log server)")

        jev = state.get("jev") or {}
        return AskResponse(
            status=state.get("status") or "unknown",
            answer=state.get("answer", ""),
            sources=[SourceOut(**s) for s in state.get("sources", [])],
            jev=JevOut(**jev) if jev else None,
            run_id=state.get("run_id"),
            latency_s=round(time.perf_counter() - t0, 3),
            retries=state.get("retries", 0) or 0,
            trace=state.get("trace") if req.debug else None,
        )

    # ------------------------------------------------------------- /feedback
    @app.post("/feedback", response_model=FeedbackResponse)
    def feedback(req: FeedbackRequest) -> FeedbackResponse:
        store = app.state.feedback
        if store is None:
            raise HTTPException(status_code=503,
                                detail="feedback store tidak tersedia "
                                       "(DB down?)")
        # Kolom feedback.run_id NOT NULL. Saat Langfuse nonaktif client tidak
        # punya run_id -> pakai id lokal agar baris tetap tersimpan.
        # (Score Langfuse otomatis dilewati karena client-nya None.)
        run_id = req.run_id or f"local-{uuid.uuid4().hex[:12]}"
        with _fb_lock:
            ok = store.submit(run_id, helpful=req.helpful, comment=req.comment)
        if not ok:
            raise HTTPException(status_code=500,
                                detail="feedback gagal disimpan (lihat log)")
        return FeedbackResponse(saved=True)

    # --------------------------------------------------------------- /health
    @app.get("/health", response_model=HealthResponse)
    def health(response: Response) -> HealthResponse:
        db = _db_ok()
        if not db:
            response.status_code = 503
        return HealthResponse(status="ok" if db else "degraded", db=db,
                              llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
                              langfuse=_langfuse_enabled())

    # Frontend: serve UI dari folder frontend di root proyek.
    # app.py berada di <root>/src/flowdesk/api/app.py, jadi parents[3] = root:
    # parents[0]=api, [1]=flowdesk, [2]=src, [3]=root.
    # (Patch lama: 3x os.path.dirname hanya sampai src/ -> mencari
    #  src/frontend yang tidak ada -> GET / 404.)
    from pathlib import Path
    default_frontend = str(Path(__file__).resolve().parents[3] / "frontend")


    frontend_dir = os.getenv("FLOWDESK_FRONTEND_DIR") or default_frontend

    if os.path.isdir(frontend_dir):
        app.mount(
            "/",
            StaticFiles(directory=frontend_dir, html=True),
            name="frontend",
        )
        logger.info("Frontend berhasil di-mount: %s", frontend_dir)
    else:
        logger.warning("Folder frontend tidak ditemukan: %s", frontend_dir)

    return app

app = create_app()
