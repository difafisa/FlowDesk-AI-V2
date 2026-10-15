"""Tahap 7.3 — tests/ingestion: CSV/JSON -> canonical structured records
(PRD 2.2b: structured data TIDAK dipaksa jadi Markdown).

Kontrak:
- record punya record_id stabil + source relatif dari data/
- dict asli UTUH di field 'data' (tidak dirusak — dasar chunk structured)
- record_to_text: flatten tipis utk embedding (underscore->spasi,
  nested dict digabung, list di-join "; ") — bukan dump JSON mentah
"""
from pathlib import Path

from flowdesk.normalization.structured_normalize import load_records, record_to_text

RAW = Path(__file__).resolve().parents[2] / "data" / "raw" / "structured"


def test_csv_records_canonical():
    recs = load_records(RAW / "pricing-plans.csv")
    assert len(recs) == 3                              # Free, Pro, Enterprise
    first = recs[0]
    assert first["record_id"] == "pricing-plans-000"
    assert first["source"] == "raw/structured/pricing-plans.csv"
    assert first["data"]["plan"] == "Free"             # dict asli utuh
    assert recs[1]["data"]["plan"] == "Pro"
    assert recs[2]["data"]["api_rate_limit"] == "300 requests per minute"


def test_json_records_nested_flatten():
    recs = load_records(RAW / "api-endpoints.json")
    assert recs and all("endpoint" in r["data"] for r in recs)
    text = record_to_text(recs[0])
    assert "endpoint: /auth/me" in text
    # nested dict -> key digabung; underscore -> spasi (bukan JSON dump)
    assert "example response account id: acct_12345" in text


def test_record_to_text_edges(tmp_path):
    p = tmp_path / "edge.json"
    p.write_text('[{"a": 1, "b": {"c": [1, 2], "d_e": "x"}}]', encoding="utf-8")
    text = record_to_text(load_records(p)[0])
    assert "a: 1" in text
    assert "b c: 1; 2" in text                         # list -> "; " join
    assert "d e: x" in text                            # underscore -> spasi


def test_single_object_json_wrapped(tmp_path):
    p = tmp_path / "single.json"
    p.write_text('{"k": "v"}', encoding="utf-8")
    recs = load_records(p)
    assert len(recs) == 1 and recs[0]["data"] == {"k": "v"}


def test_unknown_suffix_returns_empty(tmp_path):
    p = tmp_path / "note.txt"
    p.write_text("apa pun", encoding="utf-8")
    assert load_records(p) == []
