"""Estimator token deterministic (PRD 3.1: jangan pakai LLM untuk menghitung token).
Heuristik multilingual: ~4 char/token untuk Latin, 1 token per karakter CJK.
Konsisten dengan heuristik chunker Phase 2 (satu definisi 'token' se-pipeline).
Upgrade path nanti: ganti dengan tokenizer HF dari model LLM yang dipakai,
tanpa mengubah pemanggil — signature-nya sama."""
import re

def approx_tokens(text: str) -> int:
    words = len(re.findall(r"[A-Za-z0-9]+", text))
    cjk = len(re.findall(r"[\u4e00-\u9fff\u3040-\u30ff]", text))
    return words + cjk + max(0, (len(text) - words * 4) // 12)
