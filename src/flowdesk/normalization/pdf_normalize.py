"""PDF -> Normalized Markdown dengan filter watermark per-font."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import pdfplumber


WATERMARK_FONTS = {"DejaVuSans-Bold"}


@dataclass
class Line:
    page: int
    top: float
    text: str
    font: str
    size: float


@dataclass
class TableBlock:
    page: int
    top: float
    text: str


def _join_chars(chars: list) -> str:
    """Gabungkan chars menjadi teks baris dan sisipkan spasi berdasarkan gap horizontal."""
    out: list[str] = []
    prev_end = None

    for ch in chars:
        if prev_end is not None and ch["x0"] - prev_end > 1.5:
            out.append(" ")

        out.append(ch["text"])
        prev_end = ch["x1"]

    return "".join(out).strip()


def _cell_text(page, bbox) -> str:
    """Ambil teks dari satu cell tanpa watermark."""
    x0, top, x1, bottom = bbox

    chars = [
        c
        for c in page.chars
        if (
            c["fontname"].split("+")[-1] not in WATERMARK_FONTS
            and x0 <= (c["x0"] + c["x1"]) / 2 <= x1
            and top <= (c["top"] + c["bottom"]) / 2 <= bottom
        )
    ]

    chars.sort(key=lambda c: (round(c["top"]), c["x0"]))

    return _join_chars(chars)


def _extract_tables_markdown(page) -> tuple[list[TableBlock], list]:
    """
    Deteksi tabel dan ubah menjadi block [table]...[/table].

    Return:
        (
            table_blocks,
            table_bboxes
        )
    """

    blocks: list[TableBlock] = []
    bboxes: list = []

    for table in page.find_tables():
        rows = table.rows

        # Minimal header + 1 data row.
        if len(rows) < 2:
            continue

        header_cells = [cell for cell in rows[0].cells if cell]

        if not header_cells:
            continue

        headers = [_cell_text(page, cell) for cell in header_cells]

        table_lines: list[str] = []

        for row in rows[1:]:
            parts: list[str] = []

            for key_cell, val_cell in zip(header_cells, row.cells):
                if val_cell is None:
                    continue

                key = _cell_text(page, key_cell)
                val = _cell_text(page, val_cell)

                if not val:
                    continue

                if key:
                    parts.append(f"{key}: {val}")
                else:
                    parts.append(val)

            if parts:
                table_lines.append("; ".join(parts))

        if not table_lines:
            continue

        # Include header explicitly so the semantic relationship
        # between columns and values is preserved.
        header_text = "; ".join(
            header for header in headers if header
        )

        table_text_parts = ["[table]"]

        if header_text:
            table_text_parts.append(f"Columns: {header_text}")

        table_text_parts.extend(table_lines)
        table_text_parts.append("[/table]")

        table_text = "\n".join(table_text_parts)

        blocks.append(
            TableBlock(
                page=page.page_number,
                top=table.bbox[1],
                text=table_text,
            )
        )

        bboxes.append(table.bbox)

    return blocks, bboxes


def _extract_page_elements(page) -> list[Line | TableBlock]:
    """
    Extract text lines + table blocks dari satu halaman.

    Isi tabel tidak ikut diekstrak sebagai text biasa karena
    akan menyebabkan duplikasi.
    """

    table_blocks, table_bboxes = _extract_tables_markdown(page)

    def in_table(ch) -> bool:
        x = (ch["x0"] + ch["x1"]) / 2
        t = (ch["top"] + ch["bottom"]) / 2

        return any(
            bx0 <= x <= bx1
            and btop <= t <= bbottom
            for bx0, btop, bx1, bbottom in table_bboxes
        )

    buckets: dict[int, list] = defaultdict(list)

    for ch in page.chars:
        font = ch["fontname"].split("+")[-1]

        # Skip watermark dan chars yang berada di dalam tabel.
        if font in WATERMARK_FONTS or in_table(ch):
            continue

        buckets[round(ch["top"])].append(ch)

    elements: list[Line | TableBlock] = []

    # Text lines.
    for top, chars in buckets.items():
        chars.sort(key=lambda c: c["x0"])

        text = _join_chars(chars)

        if not text.strip():
            continue

        main = max(chars, key=lambda c: c["size"])

        font_name = main["fontname"].split("+")[-1]

        elements.append(
            Line(
                page=page.page_number,
                top=top,
                text=text,
                font=font_name,
                size=round(main["size"], 1),
            )
        )

    # Table blocks.
    elements.extend(table_blocks)

    # Pertahankan reading order berdasarkan posisi vertikal.
    elements.sort(key=lambda element: element.top)

    return elements


def _extract_clean_lines(pdf_path: Path) -> list[Line | TableBlock]:
    """
    Rekonstruksi isi PDF menjadi elemen text + table.

    Watermark dibuang berdasarkan font.
    """

    elements: list[Line | TableBlock] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_elements = _extract_page_elements(page)
            elements.extend(page_elements)

    return elements


def _to_markdown(elements: list[Line | TableBlock]) -> str:
    """
    Konversi elemen PDF menjadi normalized Markdown.

    Heading:
        Bold + size >= 15

    Table:
        [table]...[/table]

    Page:
        <!-- page=N -->
    """

    md: list[str] = []

    prev: Line | None = None
    para: list[str] = []

    heading_sizes = sorted(
        {
            element.size
            for element in elements
            if isinstance(element, Line)
            and "Bold" in element.font
            and element.size >= 15
        },
        reverse=True,
    )

    cur_page = None

    def flush():
        if para:
            md.append(" ".join(para))
            para.clear()

    for element in elements:

        # ---------------------------------------------------------
        # PAGE MARKER
        # ---------------------------------------------------------

        if element.page != cur_page:
            flush()

            cur_page = element.page

            md.append(f"<!-- page={element.page} -->")

            prev = None

        # ---------------------------------------------------------
        # TABLE
        # ---------------------------------------------------------

        if isinstance(element, TableBlock):
            flush()

            md.append(element.text)

            prev = None

            continue

        # ---------------------------------------------------------
        # TEXT LINE
        # ---------------------------------------------------------

        line = element

        is_heading = (
            "Bold" in line.font
            and line.size >= 15
            and len(line.text) < 120
        )

        if is_heading:
            flush()

            if line.size in heading_sizes:
                level = heading_sizes.index(line.size) + 1
            else:
                level = 1

            md.append(
                "#" * min(level, 3) + " " + line.text
            )

        elif (
            prev is not None
            and line.page == prev.page
            and line.top - prev.top < 2
            and line.font == prev.font
        ):
            para.append(line.text)

        else:
            flush()
            para.append(line.text)

        prev = line

    flush()

    return "\n\n".join(md)


def normalize_pdf(pdf_path: Path, out_path: Path) -> str:
    """
    PDF -> normalized Markdown.
    """

    elements = _extract_clean_lines(pdf_path)

    md = _to_markdown(elements)

    out_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    out_path.write_text(
        md,
        encoding="utf-8",
    )

    return md


if __name__ == "__main__":
    import sys

    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])

    md = normalize_pdf(src, dst)

    print(
        f"{src.name}: "
        f"{len(md)} chars -> {dst}"
    )