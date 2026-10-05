"""PRD 3.2 — Basic prompt injection defense (deterministic, murah, terukur).
MVP: deteksi pola eksplisit. Bukan solver sempurna — vektor canggih (encoding,
bahasa campuran) memang lolos; lapisan grounding di system prompt + LLM/Jev
classifier = improvement setelah baseline ada (sesuai PRD 3.2)."""
import re
from dataclasses import dataclass

# Daftar hidup: ditambah seiring pengujian & kasus nyata
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"reveal\s+(your\s+)?(system\s+)?(prompt|instructions)",
    r"print\s+(your\s+)?(system\s+)?(prompt|instructions)",
    r"you\s+are\s+now\s+(a|an)\s+",               # persona hijack
    r"act\s+as\s+(if\s+you\s+(are|were)\s+)?a",   # role hijack
    r"\bsystem\s*:\s*",                            # fake system-role di teks user
]


@dataclass
class InjectionCheck:
    flagged: bool
    matched: str = ""


def check_injection(user_input: str) -> InjectionCheck:
    lowered = user_input.lower()
    for pat in INJECTION_PATTERNS:
        m = re.search(pat, lowered)
        if m:
            return InjectionCheck(flagged=True, matched=m.group(0))
    return InjectionCheck(flagged=False)
