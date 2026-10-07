"""Tahap 2 — dedupe per chunk_id.
Dulu per dokumen: record CSV/structured berbagi satu nama dokumen,
sehingga record harga/rate-limit yang sah ikut terbuang (gate G2)."""
def dedupe_chunks(chunks: list[dict]) -> list[dict]:
    seen, unique = set(), []
    for ch in chunks:
        if ch["chunk_id"] not in seen:
            unique.append(ch)
            seen.add(ch["chunk_id"])
    return unique
