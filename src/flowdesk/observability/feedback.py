"""Phase 6 T3 — Feedback loop (Helpful / Not Helpful).

Alur: user memberi rating setelah jawaban -> (a) disimpan ke Postgres
(tabel feedback), (b) dikirim sebagai score Langfuse ke trace yang sama
(run_id dari T1). Keduanya fail-safe: error apa pun dicatat di log,
tidak pernah mengganggu jalur utama.

Pemakaian:
    store = FeedbackStore()
    store.submit(run_id="abc...", helpful=True, comment="jelas")

Injeksi utk test: FeedbackStore(conn=..., langfuse=...) mengikuti pola
JevClient(inner=...) — test tanpa DB/jaringan.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

DEFAULT_DSN = "postgresql://flowdesk:flowdesk@localhost:5432/flowdesk"

DDL = """
CREATE TABLE IF NOT EXISTS feedback (
    id         BIGSERIAL PRIMARY KEY,
    run_id     TEXT           NOT NULL,
    rating     TEXT           NOT NULL CHECK (rating IN ('helpful', 'nothelpful')),
    comment    TEXT,
    created_at TIMESTAMPTZ    NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS feedback_run_id_idx ON feedback (run_id);
"""


class FeedbackStore:
    """Simpan feedback ke Postgres + kirim score ke Langfuse (best-effort)."""

    def __init__(self, dsn: str | None = None, conn=None, langfuse=None):
        self._owns_conn = False
        if conn is not None:                 # injeksi utk test
            self.conn = conn
        else:
            import psycopg                   # import lokal: opsional saat test
            self.conn = psycopg.connect(dsn or os.getenv("FEEDBACK_PG_DSN",
                                                         DEFAULT_DSN))
            self._owns_conn = True
        self.conn.execute(DDL)
        if self._owns_conn:
            self.conn.commit()
        self._lf = langfuse if langfuse is not None else self._init_langfuse()

    # -- setup -----------------------------------------------------------

    def _init_langfuse(self):
        """Client Langfuse atau None (tanpa key/paket -> feedback tetap
        tersimpan di Postgres, hanya score yang tidak dikirim)."""
        try:
            from langfuse import Langfuse
        except ImportError:
            return None
        pk = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip()
        sk = os.getenv("LANGFUSE_SECRET_KEY", "").strip()
        if not pk or not sk:
            return None
        base = (os.getenv("LANGFUSE_BASE_URL", "").strip()
                or os.getenv("LANGFUSE_HOST", "").strip()
                or "https://cloud.langfuse.com")
        try:
            return Langfuse(public_key=pk, secret_key=sk, base_url=base)
        except Exception:
            return None

    # -- API utama ---------------------------------------------------------

    def submit(self, run_id: str | None, helpful: bool,
               comment: str | None = None) -> bool:
        """Catat satu feedback. Return True bila tersimpan di Postgres.

        Score Langfuse best-effort: gagal kirim tidak menggagalkan penyimpanan.
        """
        rating = "helpful" if helpful else "nothelpful"
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO feedback (run_id, rating, comment) "
                    "VALUES (%s, %s, %s)",
                    (run_id, rating, comment))
            if self._owns_conn:
                self.conn.commit()
        except Exception:
            logger.exception("Feedback gagal disimpan ke Postgres")
            return False

        self._score_langfuse(run_id, helpful, comment)
        return True

    def _score_langfuse(self, run_id: str | None, helpful: bool,
                        comment: str | None) -> None:
        if self._lf is None or not run_id:
            return
        try:
            self._lf.create_score(
                name="user_feedback",
                value=1.0 if helpful else 0.0,
                data_type="NUMERIC",
                trace_id=run_id,
                comment=comment,
                timestamp=datetime.now(timezone.utc),
            )
            self._lf.flush()
        except Exception:
            logger.exception("Score feedback gagal dikirim ke Langfuse "
                             "(feedback tetap tersimpan di Postgres)")

    # -- kueri kecil utk debugging/analytics -------------------------------

    def summary(self) -> dict:
        """Distribusi rating + 5 feedback terbaru."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT rating, COUNT(*) FROM feedback GROUP BY rating")
            counts = dict(cur.fetchall())
            cur.execute("SELECT run_id, rating, comment, created_at "
                        "FROM feedback ORDER BY created_at DESC LIMIT 5")
            recent = cur.fetchall()
        return {"helpful": counts.get("helpful", 0),
                "nothelpful": counts.get("nothelpful", 0),
                "recent": recent}
