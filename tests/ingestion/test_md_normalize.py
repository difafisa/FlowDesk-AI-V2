"""Tahap 7.3 — tests/ingestion: normalisasi Markdown (PRD 2.2b).

Kontrak: normalize_md TIDAK mengubah struktur (heading/list/tabel apa adanya),
hanya merapikan whitespace: newline >=3 -> 2, trailing spaces per baris dihapus,
awal/akhir di-strip.
"""
import re
from pathlib import Path

from flowdesk.normalization.md_normalize import normalize_md


def test_collapses_excess_newlines(tmp_path):
    p = tmp_path / "doc.md"
    p.write_text("Intro\n\n\n\n\nBody", encoding="utf-8")
    assert normalize_md(p) == "Intro\n\nBody"


def test_strips_trailing_whitespace_and_ends(tmp_path):
    p = tmp_path / "doc.md"
    p.write_text("  baris dengan spasi belakang   \n\nparagraf\n\n", encoding="utf-8")
    out = normalize_md(p)
    # baris kosong tunggal = pemisah paragraf -> DIPERTAHANKAN;
    # yang dihapus hanya: spasi trailing tiap baris + awal/akhir string
    assert out == "baris dengan spasi belakang\n\nparagraf"
    assert not any(line != line.rstrip() for line in out.split("\n"))



def test_structure_of_real_doc_preserved():
    doc = (Path(__file__).resolve().parents[2] / "data" / "raw"
           / "api" / "webhooks.md")
    out = normalize_md(doc)
    assert re.search(r"(?m)^#{1,3} ", out)      # heading tetap terbaca
