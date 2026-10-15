"""Tahap 7.3 — tests/retrieval (INTEGRATION, PRD kategori retrieval).

Butuh PostgreSQL nyata + index terisi:
    docker compose up -d db
    python scripts/ingest.py

Auto-skip bila DB tidak terjangkau ATAU tabel chunks kosong —
`pytest tests/` tetap hijau di mesin tanpa Docker.
Exclude eksplisit:  pytest tests/ -m "not integration"

Catatan: Embedder memuat model e5-base (~beberapa detik, dari cache HF).
"""
import os

import pytest

DSN = os.getenv("FLOWDESK_PG_DSN",
                "postgresql://flowdesk:flowdesk@localhost:5432/flowdesk")

pytestmark = pytest.mark.integration


def _db_ready() -> tuple[bool, str]:
    try:
        import psycopg
        with psycopg.connect(DSN, connect_timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM chunks")
                n = cur.fetchone()[0]
    except Exception as exc:
        return False, (f"PostgreSQL tidak terjangkau ({type(exc).__name__}) — "
                       "jalankan: docker compose up -d db")
    if n == 0:
        return False, "tabel chunks kosong — jalankan: python scripts/ingest.py"
    return True, ""


@pytest.fixture(scope="module")
def retriever():
    ok, why = _db_ready()
    if not ok:
        pytest.skip(why)
    from flowdesk.embedding.embedder import Embedder
    from flowdesk.retrieval.retriever import Retriever
    from flowdesk.storage.pgvector_store import VectorStore
    return Retriever(VectorStore(DSN), Embedder())


def test_embedder_dim_matches_store(retriever):
    """Kontrak dim: e5-base = 768 == kolom pgvector vector(768).
    Guard anti mismatch model/kolom (docstring embedder pernah menyesatkan
    soal bge-m3/1024 — lihat backlog 7.6)."""
    assert retriever.embedder.dim == 768


def test_search_returns_k_with_full_metadata(retriever):
    rows = retriever.retrieve("Apakah paket Pro mendukung webhook?", k=5)
    assert len(rows) == 5
    for r in rows:
        assert {"chunk_id", "document", "content", "dist"} <= set(r)
        assert r["document"]                       # NOT NULL di DDL
        assert 0.0 <= r["dist"] <= 2.0             # cosine distance


def test_results_ordered_by_distance(retriever):
    rows = retriever.retrieve("kebijakan refund", k=5)
    dists = [r["dist"] for r in rows]
    assert dists == sorted(dists)


def test_semantic_hit_webhook(retriever):
    """Sanity semantik: query 'webhook' harus mengembalikan minimal satu
    chunk yang memuat kata itu — menangkap index kosong/salah-dim secara
    lebih dulu daripada eval penuh."""
    rows = retriever.retrieve("Apakah paket Pro mendukung webhook?", k=5)
    assert any("webhook" in r["content"].lower() for r in rows)


def test_k_limit_respected(retriever):
    assert len(retriever.retrieve("login", k=2)) <= 2
