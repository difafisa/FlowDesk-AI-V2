"""Penyimpanan chunk + embedding di PostgreSQL pgvector."""
import psycopg
from pgvector.psycopg import register_vector


DDL = """
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS chunks (
    chunk_id    TEXT PRIMARY KEY,
    document    TEXT NOT NULL,
    section     TEXT,
    subsection  TEXT,
    page        INT,
    source_type TEXT NOT NULL,
    content     TEXT NOT NULL,
    embedding   vector(768) NOT NULL        -- bge-m3 = 1024 (e5-base = 768)
);
CREATE INDEX IF NOT EXISTS chunks_hnsw
    ON chunks USING hnsw (embedding vector_cosine_ops);
"""

class VectorStore:
    def __init__(self, dsn: str):
        self.conn = psycopg.connect(dsn)
        self.conn.execute(DDL)
        register_vector(self.conn)

    def upsert_chunks(self, rows: list[dict]):
        with self.conn.cursor() as cur:
            for r in rows:
                cur.execute("""
                    INSERT INTO chunks (chunk_id, document, section, subsection,
                                        page, source_type, content, embedding)
                    VALUES (%(chunk_id)s, %(document)s, %(section)s, %(subsection)s,
                            %(page)s, %(source_type)s, %(content)s, %(embedding)s)
                    ON CONFLICT (chunk_id) DO UPDATE SET embedding = EXCLUDED.embedding,
                        content = EXCLUDED.content
                """, r)
        self.conn.commit()

    def search(self, query_vec, k: int = 5) -> list[dict]:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT chunk_id, document, section, subsection, page,
                       source_type, content, embedding <=> %s::vector AS dist
                FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s
            """, (query_vec, query_vec, k))
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]



