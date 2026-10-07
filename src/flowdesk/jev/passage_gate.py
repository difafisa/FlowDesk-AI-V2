"""PRD Phase 04 Tahap 3 — passage gate: nilai tiap chunk, bukan context gabungan.

Satu request Jev per chunk (3 Noul sekaligus) atas state {query, passage}.
Paralel via ThreadPoolExecutor kecil (endpoint punya rate limit).
Cache = state["scores"]: chunk yang sudah terskor tidak dinilai ulang saat
retry mengambil gelombang lebih lebar (K=10) — panggilan baru hanya untuk
chunk yang benar-benar baru.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict

from flowdesk.guardrails.config import GATE_WORKERS


@dataclass
class PassageScore:
    chunk_id: str
    is_relevant: float                  # P(passage membahas topik query)
    contains_answer_evidence: float     # P(passage memuat jawaban)
    contains_prompt_injection: float    # P(passage mencoba mengendalikan sistem)
    ok: bool = True                     # False = scoring gagal -> tidak layak
    error: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _score_one(jev, question: str, ch: dict) -> PassageScore:
    try:
        s = jev.score_chunk(question, ch["content"])
        return PassageScore(
            chunk_id=ch["chunk_id"],
            is_relevant=s["is_relevant"],
            contains_answer_evidence=s["contains_answer_evidence"],
            contains_prompt_injection=s["contains_prompt_injection"],
        )
    except Exception as e:      # timeout/5xx/parse -> dicatat tidak layak
        return PassageScore(
            chunk_id=ch["chunk_id"], is_relevant=0.0,
            contains_answer_evidence=0.0, contains_prompt_injection=0.0,
            ok=False, error=type(e).__name__)


def score_passages(jev, question: str, chunks: list[dict],
                   cache: dict | None = None,
                   workers: int = GATE_WORKERS) -> dict[str, dict]:
    """Return {chunk_id: score_dict} untuk chunk BELUM terskor saja.
    Chunk error tetap masuk hasil (ok=False) — tercatat, tidak layak."""
    cache = cache or {}
    todo = [ch for ch in chunks if ch["chunk_id"] not in cache]
    out: dict[str, dict] = {}
    if not todo:
        return out
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_score_one, jev, question, ch): ch for ch in todo}
        for fut in as_completed(futures):
            ps = fut.result()
            out[ps.chunk_id] = ps.to_dict()
    return out
