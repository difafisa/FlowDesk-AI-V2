"""Tahap 2 — dedupe per chunk_id.
Regresi temuan G2: record structured/CSV berbagi satu nama dokumen;
dedupe per dokumen membuang record yang sah (bukti: trace diag G2,
rate-limits '5. Pro Plan' ter-DROP)."""
from flowdesk.rag.dedupe import dedupe_chunks


def test_keeps_multiple_records_from_same_document():
    chunks = [{"chunk_id": f"pricing-plans-{i:03d}", "document": "structured/pricing-plans.csv",
               "content": f"plan record {i}"} for i in range(3)]
    assert len(dedupe_chunks(chunks)) == 3      # semua record selamat


def test_removes_literal_duplicate_chunk():
    chunks = [{"chunk_id": "pricing-plans-001", "document": "x", "content": "a"},
              {"chunk_id": "pricing-plans-001", "document": "x", "content": "a"}]
    assert len(dedupe_chunks(chunks)) == 1


def test_empty_input():
    assert dedupe_chunks([]) == []


def test_preserves_order():
    chunks = [{"chunk_id": "b", "document": "d", "content": "x"},
              {"chunk_id": "a", "document": "d", "content": "y"}]
    assert [c["chunk_id"] for c in dedupe_chunks(chunks)] == ["b", "a"]
