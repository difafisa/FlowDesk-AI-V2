"""Phase 7 — Skema request/response API (pydantic v2).

Konvensi: SEMUA outcome aplikasi (answered / abstained / escalated /
rejected / injection_blocked) dikembalikan sebagai HTTP 200 — itu hasil
valid dari pipeline, bukan error transport. Error HTTP hanya untuk
masalah infrastruktur (502 workflow gagal, 503 DB down).
"""
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AskRequest(BaseModel):
    # Tanpa min_length: input kosong tetap masuk workflow supaya ditolak
    # secara graceful oleh validate_input (PRD 3.1), bukan 422 dari API.
    question: str = Field(default="", max_length=100_000)
    # Grouping trace di panel Sessions Langfuse (opsional per conversasi)
    session_id: str | None = None
    # True -> sertakan jejak node (utk debugging, PRD Phase 6)
    debug: bool = False


class SourceOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    index: int
    document: str | None = None
    page: int | None = None
    chunk_id: str | None = None


class JevOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    decision: str | None = None
    reason: str | None = None
    in_scope: bool | None = None


class AskResponse(BaseModel):
    status: str                      # answered|abstained|escalated|rejected|injection_blocked
    answer: str
    sources: list[SourceOut] = Field(default_factory=list)
    jev: JevOut | None = None
    run_id: str | None = None        # trace id Langfuse (None bila nonaktif) -> utk /feedback
    latency_s: float
    retries: int = 0
    trace: list[dict[str, Any]] | None = None   # hanya bila debug=True


class FeedbackRequest(BaseModel):
    run_id: str | None = None        # None bila Langfuse nonaktif
    helpful: bool
    comment: str | None = None


class FeedbackResponse(BaseModel):
    saved: bool


class HealthResponse(BaseModel):
    status: str                      # ok | degraded
    db: bool
    llm_model: str | None
    langfuse: bool
