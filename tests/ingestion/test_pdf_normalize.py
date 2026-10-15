"""Tahap 7.3 — tests/ingestion: PDF -> normalized Markdown (PRD 2.2a/2.3).

Mengunci kontrak yang dipakai downstream:
- marker halaman <!-- page=N -->  -> metadata 'page' chunk + citation
- heading #{1,3}                  -> metadata section/subsection chunk
- file output = nilai return      -> cache processed/ konsisten

CATATAN: assertion [table] sengaja TIDAK ada — terbukti dari chunks.jsonl
bahwa kelima PDF product saat ini tidak menghasilkan blok tabel terdeteksi.
"""
import re
from pathlib import Path

import pytest

from flowdesk.normalization.pdf_normalize import normalize_pdf

RAW = Path(__file__).resolve().parents[2] / "data" / "raw" / "product"
PDFS = sorted(RAW.glob("*.pdf"))


@pytest.fixture(scope="module")
def normalized(tmp_path_factory):
    """Normalisasi tiap PDF SEKALI per modul — pdfplumber mahal."""
    out_dir = tmp_path_factory.mktemp("pdf_norm")
    return {pdf.name: (normalize_pdf(pdf, out_dir / f"{pdf.stem}.md"),
                       out_dir / f"{pdf.stem}.md")
            for pdf in PDFS}


@pytest.mark.parametrize("pdf", PDFS, ids=lambda p: p.name)
def test_page_markers_and_headings(pdf, normalized):
    md, _ = normalized[pdf.name]
    assert md.strip()
    # marker halaman pertama selalu paling awal (emitted sebelum elemen lain)
    assert md.startswith("<!-- page=1 -->")
    pages = re.findall(r"<!-- page=(\d+) -->", md)
    assert len(pages) >= 1
    assert pages == sorted(pages, key=int)      # urut, tanpa duplikat aneh
    # heading terjaga -> sumber metadata section/subsection chunk
    assert re.search(r"(?m)^#{1,3} ", md), "heading hilang: metadata section ikut hilang"


@pytest.mark.parametrize("pdf", PDFS, ids=lambda p: p.name)
def test_output_file_matches_return(pdf, normalized):
    md, dst = normalized[pdf.name]
    assert dst.exists()
    assert dst.read_text(encoding="utf-8") == md


def test_at_least_one_multipage_doc(normalized):
    """Dokumen product adalah panduan multi-halaman; marker halaman > 1
    harus muncul minimal di satu dokumen (bukti marker bekerja, bukan kosmetik)."""
    assert any("<!-- page=2 -->" in md for md, _ in normalized.values())
