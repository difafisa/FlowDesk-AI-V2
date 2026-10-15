"""Hulu-fix 2026-10-13 — sibling merge H3 + tabel kecil utuh (ds-015/030/049)."""
from flowdesk.chunking.structure_chunker import (
    CHUNK_SIZE, TABLE_MERGE_TOKENS, chunk_markdown, chunk_structured,
    _approx_tokens,
)


MD_SIBLINGS = """# Ticket Management
## Supported Ticket Statuses
### Open
Use open when a ticket requires active attention.
### Pending
Use pending when waiting for information.
### Resolved
Use resolved when the request has been addressed.
### Closed
Use closed when no further support work is expected. Closing indicates the process finished.
"""


def test_h3_siblings_kecil_menjadi_satu_chunk():
    chunks = chunk_markdown(MD_SIBLINGS, "ticket.md")
    assert len(chunks) == 1
    for kata in ("Open", "Pending", "Resolved", "Closed"):
        assert kata in chunks[0].content
    assert _approx_tokens(chunks[0].content) <= CHUNK_SIZE * 1.15


def test_h3_tetap_terpotong_bila_melebihi_ukuran():
    md = "# T\n## S\n" + (
        "### Bagian A\n" + ("Kalimat panjang sekali ini. " * 200) +
        "### Bagian B\n" + ("Kalimat lain yang panjang. " * 200)
    )
    chunks = chunk_markdown(md, "t.md")
    assert len(chunks) >= 2


def test_tabel_kecil_menjadi_satu_chunk_utuh():
    records = [
        {"record_id": f"fc-{i:03d}", "data": row}
        for i, row in enumerate([
            {"feature": "Ticket Management", "free": "true",
             "pro": "true", "enterprise": "true"},
            {"feature": "Analytics", "free": "true",
             "pro": "true", "enterprise": "true"},
            {"feature": "Advanced Analytics", "free": "false",
             "pro": "true", "enterprise": "true"},
        ])
    ]
    chunks = chunk_structured(records, "structured/feature-comparison.csv")
    assert len(chunks) == 1
    c = chunks[0]
    assert c.chunk_id == "feature-comparison-table"
    assert c.subsection == "table"
    assert "Advanced Analytics" in c.content       # baris jawaban ikut ter-retrieve
    assert "Columns:" in c.content and "feature" in c.content
    assert _approx_tokens(c.content) <= TABLE_MERGE_TOKENS + 30


def test_tabel_besar_tetap_per_record():
    rows = [{"feature": f"Feature {i}", "free": "true", "pro": "true",
             "enterprise": "true"} for i in range(200)]
    records = [{"record_id": f"big-{i:03d}", "data": r}
               for i, r in enumerate(rows)]
    chunks = chunk_structured(records, "structured/big.csv")
    assert len(chunks) == 200
    assert all("-table" not in c.chunk_id for c in chunks)
