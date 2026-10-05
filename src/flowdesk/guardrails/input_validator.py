"""PRD 3.1 — Input validation deterministic.
Return (status, reason): status = ok | too_long_moderate | rejected.

Tiga tingkat sesuai PRD 3.1:
- normal           -> lanjut ke pipeline
- moderately long  -> minta user meringkas (opsi B; truncate berisiko memotong
                      informasi penting, summarize butuh LLM call ekstra = bukan MVP)
- extremely long   -> hard reject (opsi D; safety boundary untuk input ekstrem)"""
from dataclasses import dataclass

from flowdesk.guardrails.config import MAX_INPUT_TOKENS, HARD_INPUT_LIMIT
from flowdesk.guardrails.tokens import approx_tokens


@dataclass
class InputCheck:
    status: str        # "ok" | "too_long_moderate" | "rejected"
    reason: str = ""


def validate_input(user_input: str) -> InputCheck:
    # 1) empty / bukan string (mis. None dari layer UI)
    if not isinstance(user_input, str) or not user_input.strip():
        return InputCheck("rejected", "empty input")

    # 2) invalid format: control characters non-whitespace
    #    (indikasi copy-paste rusak / payload binary, PRD 3.1 "invalid input format")
    if any(ord(c) < 9 for c in user_input):
        return InputCheck("rejected", "invalid characters")

    n = approx_tokens(user_input)

    # 3) extreme -> hard reject (PRD 3.1 opsi D)
    if n > HARD_INPUT_LIMIT:
        return InputCheck("rejected", f"{n} tokens > hard limit {HARD_INPUT_LIMIT}")

    # 4) moderate -> minta user meringkas (PRD 3.1 opsi B)
    if n > MAX_INPUT_TOKENS:
        return InputCheck("too_long_moderate",
                          f"{n} tokens > {MAX_INPUT_TOKENS}")

    return InputCheck("ok")
