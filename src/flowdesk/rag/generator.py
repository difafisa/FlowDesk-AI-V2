"""PRD 3.4 — Grounded generation.
LLM HANYA boleh menjawab dari context yang diberikan. Evidence tidak cukup
-> abstain dengan kalimat standar (DO NOT invent an answer).
Catatan: di Phase 3 abstain ini 'soft guard' via prompt; di Phase 4, Jev
menambah keputusan eksplisit SEBELUM LLM dipanggil (hard guard + hemat biaya)."""

from flowdesk.rag.llm_client import LLMClient

# Marker abstain HARUS sama dengan ABSTAIN_MARKER di output_validator.py
# supaya Tahap E mengenalinya secara deterministic.
SYSTEM_PROMPT = """You are FlowDesk's customer support assistant.

Rules:
1. Answer ONLY using the numbered context blocks provided by the user.
2. Cite sources after every factual claim using the block numbers, e.g. [1] or [2][3].
3. If the context does not contain enough information to answer, reply exactly:
   "Maaf, saya belum menemukan informasi yang cukup untuk menjawab pertanyaan tersebut."
4. Never use outside knowledge. Never invent features, prices, or limits.
5. Answer in the same language as the user's question.
6. Be concise and actionable — this is customer support, not an essay."""


def generate_answer(llm: LLMClient, question: str, context: str) -> str:
    user_prompt = (
        f"Question:\n{question}\n\n"
        f"Context blocks:\n{context}\n\n"
        "Answer using the rules above."
    )
    return llm.generate(SYSTEM_PROMPT, user_prompt)
