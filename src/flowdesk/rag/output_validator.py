"""PRD 3.6 — Output & citation validation (deterministic Python, bukan LLM).
- Citation [n] harus merujuk evidence yang benar-benar diberikan ke LLM.
- Citation yang mengacu ke sumber tidak ada = hallucinated citation -> dibuang,
  jumlahnya dicatat (metrik kualitas generation utk Phase 5).
- Jawaban abstain dikenali dan diteruskan apa adanya."""
import re
from dataclasses import dataclass, field

ABSTAIN_MARKER = "belum menemukan informasi yang cukup"


@dataclass
class OutputCheck:
    valid: bool
    answer: str                     # jawaban final (mungkin sudah dibersihkan)
    invalid_citations: list[int] = field(default_factory=list)
    is_abstain: bool = False
    has_citation: bool = False


def validate_output(raw_answer: str, sources: list[dict]) -> OutputCheck:
    # 1) abstain yang jujur -> teruskan tanpa disentuh
    if ABSTAIN_MARKER in raw_answer.lower():
        return OutputCheck(valid=True, answer=raw_answer, is_abstain=True)

    valid_idx = {s["index"] for s in sources}
    cited = [int(n) for n in re.findall(r"\[(\d+)\]", raw_answer)]

    # 2) citation halusinasi -> buang markernya, catat nomornya
    invalid = sorted({n for n in cited if n not in valid_idx})
    cleaned = raw_answer
    for n in invalid:
        cleaned = cleaned.replace(f"[{n}]", "")

    return OutputCheck(
        valid=not invalid,
        answer=cleaned,
        invalid_citations=invalid,
        has_citation=bool(set(cited) & valid_idx),
    )
