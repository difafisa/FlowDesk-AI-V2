"""PRD 3.4/3.5 — LLM client abstraction (protokol OpenAI-compatible).
Tukar provider hanya dengan mengubah init:
  OpenAI      : base_url="https://api.openai.com/v1",        model="gpt-4o-mini"
  OpenRouter  : base_url="https://openrouter.ai/api/v1",     model=<dari katalog>
  Ollama lokal: base_url="http://localhost:11434/v1",        model="llama3.1:8b"
API key TIDAK pernah di-hardcode — dibaca dari environment (.env)."""
import os
from openai import OpenAI
import time
import openai


from flowdesk.guardrails.config import MAX_OUTPUT_TOKENS


class LLMClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.openai.com/v1",
                 model: str = "gpt-4o-mini"):
        self.model = model                       # ← TAMBAHKAN baris ini
        self.client = OpenAI(api_key=api_key or os.environ["LLM_API_KEY"], base_url=base_url)


    def generate(self, system_prompt: str, user_prompt: str) -> str:
        last_err: Exception | None = None
        for attempt in range(4):                     # 1 percobaan + 3 retry
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=MAX_OUTPUT_TOKENS,    # PRD 3.5: output limit via LLM config
                    temperature=0.1,
                )
                return resp.choices[0].message.content or ""
            except (openai.RateLimitError,           # 429: kuota/rate limit
                    openai.InternalServerError,      # 503/500: server sibuk
                    openai.APIConnectionError) as e: # masalah jaringan
                last_err = e
                wait = 2 ** attempt * 15             # 15s, 30s, 60s
                print(f"    [retryable] tunggu {wait}s (attempt {attempt + 1}/4): "
                      f"{type(e).__name__}")
                time.sleep(wait)
        raise last_err                               # habis 4 percobaan -> gagal jujur

