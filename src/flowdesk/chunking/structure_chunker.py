"""Structure-aware chunking: structure first, token limit second (PRD 2.4)."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path


CHUNK_SIZE = 700
OVERLAP = 70


@dataclass
class Chunk:
    chunk_id: str
    document: str
    section: str
    subsection: str
    page: int | None
    source_type: str
    content: str


def _approx_tokens(text: str) -> int:
    """Estimasi token deterministik & murah (multilingual, tanpa tokenizer eksternal).

    Heuristic:
    - ~4 karakter/token untuk Latin
    - karakter CJK dihitung ~1 token
    """
    words = len(re.findall(r"[A-Za-z0-9]+", text))
    cjk = len(re.findall(r"[\u4e00-\u9fff\u3040-\u30ff]", text))

    return words + cjk + (len(text) - words * 4) // 12


def parse_structure(md_text: str) -> list[dict]:
    """Parse markdown menjadi list section.

    Struktur hasil:
    [
        {
            "h1": "...",
            "h2": "...",
            "blocks": [
                {
                    "type": "para" | "h3" | "code" | "table",
                    "text": "...",
                    "page": 1
                }
            ]
        }
    ]

    Fenced code block dan table block diperlakukan sebagai
    satu blok atomik.
    """

    doc = {
        "h1": "",
        "h2": "",
        "blocks": [],
    }

    sections: list[dict] = []

    in_fence = False
    in_table = False
    cur_page = None

    for raw in md_text.split("\n"):
        line = raw.rstrip()

        # ---------------------------------------------------------
        # PAGE MARKER
        # ---------------------------------------------------------
        m = re.fullmatch(
            r"<!--\s*page=(\d+)\s*-->",
            line.strip(),
        )

        if m:
            cur_page = int(m.group(1))
            continue

        # ---------------------------------------------------------
        # TABLE BLOCK
        # ---------------------------------------------------------
        if line.strip() == "[table]":
            in_table = True

            doc["blocks"].append(
                {
                    "type": "table",
                    "text": "",
                    "page": cur_page,
                }
            )

            continue

        if line.strip() == "[/table]":
            in_table = False
            continue

        if in_table:
            doc["blocks"][-1]["text"] += (
                "\n" if doc["blocks"][-1]["text"] else ""
            ) + line

            continue

        # ---------------------------------------------------------
        # CODE BLOCK
        # ---------------------------------------------------------
        if line.startswith("```"):
            in_fence = not in_fence

            if in_fence:
                # Pembuka code fence
                doc["blocks"].append(
                    {
                        "type": "code",
                        "text": line,
                        "page": cur_page,
                    }
                )

            else:
                # Penutup code fence
                doc["blocks"][-1]["text"] += "\n" + line

            continue

        if in_fence:
            doc["blocks"][-1]["text"] += "\n" + line
            continue

        # ---------------------------------------------------------
        # HEADING 3
        # ---------------------------------------------------------
        if line.startswith("### "):
            doc["blocks"].append(
                {
                    "type": "h3",
                    "text": line[4:],
                    "page": cur_page,
                }
            )

        # ---------------------------------------------------------
        # HEADING 2
        # ---------------------------------------------------------
        elif line.startswith("## "):
            if doc["blocks"]:
                sections.append(doc)

            doc = {
                "h1": _last_h1(sections, doc),
                "h2": line[3:],
                "blocks": [],
            }

        # ---------------------------------------------------------
        # HEADING 1
        # ---------------------------------------------------------
        elif line.startswith("# "):
            if doc["blocks"]:
                sections.append(doc)

            doc = {
                "h1": line[2:],
                "h2": "",
                "blocks": [],
            }

        # ---------------------------------------------------------
        # NORMAL PARAGRAPH
        # ---------------------------------------------------------
        elif line.strip():
            doc["blocks"].append(
                {
                    "type": "para",
                    "text": line,
                    "page": cur_page,
                }
            )

    # Tambahkan section terakhir
    if doc["blocks"]:
        sections.append(doc)

    return sections


def _last_h1(sections: list[dict], current: dict) -> str:
    """Ambil H1 terakhir yang ditemukan."""

    for section in reversed(sections):
        if section["h1"]:
            return section["h1"]

    return current["h1"]


def _split_big_block(
    text: str,
    size: int,
    overlap: int,
) -> list[str]:
    """Pecah blok besar pada boundary kalimat.

    Tidak memotong di tengah kata.
    """

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    parts: list[str] = []
    cur = ""

    for sentence in sentences:
        if (
            _approx_tokens(cur) + _approx_tokens(sentence) > size
            and cur
        ):
            parts.append(cur)

            # Ambil bagian akhir sebagai overlap.
            cur = (
                " ".join(cur.split()[-overlap:])
                + " "
                + sentence
            )

        else:
            cur = (
                cur + " " + sentence
            ).strip()

    if cur:
        parts.append(cur)

    return parts


def chunk_markdown(
    md_text: str,
    document: str,
    page: int | None = None,
    source_type: str = "markdown",
) -> list[Chunk]:
    """Chunk markdown berdasarkan struktur terlebih dahulu."""

    chunks: list[Chunk] = []

    for sec in parse_structure(md_text):

        # Gabungkan blok dalam satu subsection.
        #
        # Table dan code block tetap dianggap sebagai satu blok
        # karena parse_structure() sudah menyimpannya sebagai
        # satu block.
        group: list[dict] = []
        group_tokens = 0
        group_page = None

        def flush_group():
            nonlocal group
            nonlocal group_tokens
            nonlocal group_page

            if not group:
                return

            content = "\n\n".join(
                block["text"]
                for block in group
            )

            _emit(
                chunks,
                content,
                document,
                sec,
                group_page if group_page is not None else page,
                source_type,
            )

            group = []
            group_tokens = 0
            group_page = None

        for block in sec["blocks"]:
            text = block["text"]
            tokens = _approx_tokens(text)

            # H3 menjadi boundary chunk.
            if block["type"] == "h3":
                flush_group()

                group = [block]
                group_tokens = tokens
                group_page = block.get("page")

            # Jika melewati batas chunk, flush chunk sebelumnya.
            elif group_tokens + tokens > CHUNK_SIZE and group:
                flush_group()

                group = [block]
                group_tokens = tokens
                group_page = block.get("page")

            else:
                if group_page is None:
                    group_page = block.get("page")

                group.append(block)
                group_tokens += tokens

        # Flush sisa block.
        flush_group()

    return chunks


def _emit(
    chunks: list,
    content: str,
    document: str,
    sec: dict,
    page,
    source_type: str = "markdown",
):
    """Emit final Chunk.

    Block atomik seperti code dan table tidak dipecah lagi.
    """

    fence = "```"

    has_atomic = (
    fence in content
    or "\n|" in content
    or content.lstrip().startswith("|")
    or content.lstrip().startswith("[table]")
)

    # Jika terlalu besar dan bukan atomic block,
    # pecah berdasarkan kalimat.
    if (
        _approx_tokens(content) > CHUNK_SIZE * 1.15
        and not has_atomic
    ):
        parts = _split_big_block(
            content,
            CHUNK_SIZE,
            OVERLAP,
        )

    else:
        parts = [content]

    for part in parts:

        # Contextualized content:
        # heading hierarchy ikut dimasukkan ke content.
        header = "\n".join(
            value
            for value in [
                (
                    f"Section: {sec['h1']}"
                    if sec["h1"]
                    else None
                ),
                (
                    f"Subsection: {sec['h2']}"
                    if sec["h2"]
                    else None
                ),
            ]
            if value
        )

        contextual = (
            header + "\n\n" + part
        ).strip()

        # Deterministic chunk ID.
        hash_input = (
            f"{document}|"
            f"{sec['h1']}|"
            f"{sec['h2']}|"
            f"{part[:80]}"
        )

        chunk_hash = hashlib.sha1(
            hash_input.encode()
        ).hexdigest()[:8]

        chunks.append(
            Chunk(
                chunk_id=(
                    f"{Path(document).stem}"
                    f"-{chunk_hash}"
                ),
                document=document,
                section=sec["h1"],
                subsection=sec["h2"],
                page=page,
                source_type=source_type,
                content=contextual,
            )
        )


def chunk_structured(
    records: list[dict],
    source_name: str,
) -> list[Chunk]:
    """Satu record structured = satu chunk (PRD 2.2c)."""

    from flowdesk.normalization.structured_normalize import (
        record_to_text,
    )

    return [
        Chunk(
            chunk_id=record["record_id"],
            document=source_name,
            section="structured",
            subsection=record["data"].get(
                "endpoint",
                "",
            ),
            page=None,
            source_type="structured",
            content=record_to_text(record),
        )
        for record in records
    ]


if __name__ == "__main__":
    import sys

    src = Path(sys.argv[1])

    md = src.read_text(
        encoding="utf-8"
    )

    out = [
        chunk.__dict__
        for chunk in chunk_markdown(
            md,
            src.name,
        )
    ]

    Path(sys.argv[2]).write_text(
        json.dumps(
            out,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    sizes = [
        len(chunk["content"].split())
        for chunk in out
    ]

    print(
        f"{len(out)} chunks; "
        f"contoh chunk_id: "
        f"{out[0]['chunk_id'] if out else 'N/A'}"
    )