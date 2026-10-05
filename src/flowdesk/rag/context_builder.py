"""PRD 3.3 — Context assembly dengan token budget.
Top-K chunks -> blok evidence bernomor [1]..[n] -> sisipkan selama muat
dalam CONTEXT_TOKEN_BUDGET. Blok yang tidak muat DIBUANG UTUH (bukan
dipotong) — potongan setengah menghasilkan evidence yang menyesatkan."""
from flowdesk.guardrails.config import CONTEXT_TOKEN_BUDGET
from flowdesk.guardrails.tokens import approx_tokens


def build_context(chunks: list[dict]) -> tuple[str, list[dict]]:
    """Return (context_text, sources).

    sources berisi metadata tiap blok yang BENAR-BENAR masuk context —
    dipakai Tahap E untuk memvalidasi citation, dan oleh pipeline untuk
    menampilkan sumber jawaban ke user."""
    parts: list[str] = []
    sources: list[dict] = []
    used = 0

    for i, ch in enumerate(chunks, 1):
        page = ch.get("page")
        header = f"[{i}] (source: {ch['document']}" + (f", p.{page}" if page else "") + ")"
        block = header + "\n" + ch["content"]
        t = approx_tokens(block)

        # Budget penuh dan sudah ada minimal 1 blok -> berhenti.
        # (Kalau blok PERTAMA saja sudah melebihi budget, ia tetap masuk —
        #  jawaban tanpa context lebih buruk daripada context sedikit kelebihan.)
        if used + t > CONTEXT_TOKEN_BUDGET and parts:
            break
        parts.append(block)
        sources.append({"index": i, "document": ch["document"],
                        "page": page, "chunk_id": ch["chunk_id"]})
        used += t

    return "\n\n".join(parts), sources
