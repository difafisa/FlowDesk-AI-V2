"""Orkestrasi Phase 2: normalize -> chunk -> embed -> pgvector.
Kontrak: field 'document' = path relatif dari data/raw (ekstensi asli)."""
import sys, json
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from flowdesk.normalization.pdf_normalize import normalize_pdf
from flowdesk.normalization.md_normalize import normalize_md
from flowdesk.normalization.structured_normalize import load_records
from flowdesk.chunking.structure_chunker import chunk_markdown, chunk_structured
from flowdesk.embedding.embedder import Embedder
from flowdesk.storage.pgvector_store import VectorStore

RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

def main():
    all_chunks = []

    # 1) PDF -> normalized md (cache di processed) -> chunks
    for pdf in sorted(RAW.glob("product/*.pdf")):
        md = normalize_pdf(pdf, PROCESSED / "product" / f"{pdf.stem}.md")
        all_chunks += chunk_markdown(md, document=pdf.relative_to(RAW).as_posix(),
                                     source_type="pdf")


    # 2) Markdown -> chunks
    for md_path in sorted(RAW.glob("*/*.md")):
        text = normalize_md(md_path)
        all_chunks += chunk_markdown(text, document=md_path.relative_to(RAW).as_posix())

    # 3) JSON/CSV -> structured chunks (1 record = 1 chunk)
    for sp in sorted(RAW.glob("structured/*")):
        if sp.suffix in (".json", ".csv"):
            all_chunks += chunk_structured(load_records(sp), source_name=sp.relative_to(RAW).as_posix())

    print(f"total chunks: {len(all_chunks)}")

    # 4) simpan snapshot untuk inspeksi manual (PRD 2.11)
    out = PROCESSED / "chunks.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c.__dict__, ensure_ascii=False) + "\n")
    print(f"snapshot -> {out}")

    # 5) embed + upsert
    embedder = Embedder()
    print(f"embedding dim: {embedder.dim}")
    store = VectorStore("postgresql://flowdesk:flowdesk@localhost:5432/flowdesk")
    rows = [{"chunk_id": c.chunk_id, "document": c.document, "section": c.section,
             "subsection": c.subsection, "page": c.page, "source_type": c.source_type,
             "content": c.content, "embedding": v}
            for c, v in zip(all_chunks, embedder.embed_passages([c.content for c in all_chunks]))]
    store.upsert_chunks(rows)
    print(f"upserted {len(rows)} chunks ke pgvector")

if __name__ == "__main__":
    main()
