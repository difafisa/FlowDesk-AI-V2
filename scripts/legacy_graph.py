"""PRD Phase 04 T8 — rekonstruksi graph lama (LLM-as-judge) untuk A/B benchmark.

Graph lama: satu node 'jev' menilai SELURUH context gabungan lewat LLM biasa
(prompt + JSON + regex parse) — persis implementasi placeholder sebelum
diganti Jev asli. Dipakai HANYA oleh run_phase4_benchmark.py (varian
'llm-judge'), bukan jalur produksi.

Penting untuk keadilan A/B: retrieval, dedupe per chunk_id, guardrails,
dan generator SAMA dengan varian lain — satu-satunya variabel yang beda
adalu siapa yang memutuskan (LLM prompt vs Jev System One).
"""
import json
import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from typing import TypedDict
from langgraph.graph import StateGraph, END

from flowdesk.guardrails.config import TOP_K, MAX_JEV_RETRIES, RETRY_TOP_K
from flowdesk.guardrails.input_validator import validate_input
from flowdesk.guardrails.injection_filter import check_injection
from flowdesk.rag.context_builder import build_context
from flowdesk.rag.dedupe import dedupe_chunks
from flowdesk.rag.generator import generate_answer
from flowdesk.rag.output_validator import validate_output

ABSTAIN_REPLY = ("Maaf, saya belum menemukan informasi yang cukup untuk "
                 "menjawab pertanyaan tersebut.")
ESCALATE_REPLY = "Saya akan meneruskan kasus ini ke tim support untuk diperiksa."
INJECTION_REPLY = "Maaf, saya tidak dapat membantu dengan permintaan tersebut."
LENGTH_REPLY = ("Pesan Anda terlalu panjang. Silakan kirim bagian error atau "
                "pertanyaan utamanya.")

# --- Prompt Jev palsu (versi lama, dipindahkan apa adanya) ---

JEV_SYSTEM_PROMPT = """You are Jev, the evidence-sufficiency judge for FlowDesk support.

Given a user question and numbered evidence blocks, decide ONE thing:
- "sufficient": the evidence directly answers the question
- "uncertain": partially relevant, but key information may be missing
- "insufficient": the evidence does not address the question at all

Rules:
- Judge ONLY whether the evidence suffices. Do NOT answer the question.
- Structured records (e.g. plan/price rows) ARE valid evidence for
  pricing/feature questions.
- Reply with JSON only, no other text:
  {"decision": "sufficient|uncertain|insufficient", "reason": "<max 25 words>"}"""


def jev_decide_legacy(llm, question: str, context: str) -> dict:
    """Judge lama: LLM biasa -> JSON -> regex parse. Parse gagal -> uncertain."""
    user_prompt = (f"Question:\n{question}\n\nEvidence blocks:\n{context}"
                   f"\n\nDecide sufficiency. JSON only.")
    raw = llm.generate(JEV_SYSTEM_PROMPT, user_prompt)
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(0))
            d = str(data.get("decision", "")).lower()
            if d in ("sufficient", "uncertain", "insufficient"):
                return {"decision": d, "reason": str(data.get("reason", ""))[:200],
                        "parse_ok": True}
        except json.JSONDecodeError:
            pass
    return {"decision": "uncertain", "reason": f"jev parse failed: {raw[:80]}",
            "parse_ok": False}


class LegacyState(TypedDict):
    question: str
    chunks: list
    context: str
    sources: list
    retries: int
    jev: dict
    answer: str
    status: str
    trace: list


def route_after_jev(state: LegacyState) -> str:
    d = state["jev"]["decision"]
    if d == "sufficient":
        return "generate"
    if d == "insufficient":
        return "escalate"
    return "retry_retrieve" if state["retries"] < MAX_JEV_RETRIES else "abstain"


def build_legacy_graph(llm, retriever):
    def retrieve(state: LegacyState) -> dict:
        k = RETRY_TOP_K if state["retries"] > 0 else TOP_K
        chunks = retriever.retrieve(state["question"], k=k)
        return {"chunks": chunks, "trace": state["trace"] + [
            {"node": "retrieve", "k": k, "n_chunks": len(chunks)}]}

    def rerank(state: LegacyState) -> dict:
        unique = dedupe_chunks(state["chunks"])     # sama dgn varian baru (fair)
        return {"chunks": unique, "trace": state["trace"] + [
            {"node": "rerank", "after_dedupe": len(unique)}]}

    def jev(state: LegacyState) -> dict:
        # Perbedaan inti A/B: context GABUNGAN dinilai LLM biasa,
        # bukan per-chunk oleh Jev.
        context, sources = build_context(state["chunks"])
        d = jev_decide_legacy(llm, state["question"], context)
        return {"context": context, "sources": sources, "jev": d,
                "trace": state["trace"] + [
            {"node": "jev", "decision": d["decision"], "reason": d["reason"]}]}

    def retry_retrieve(state: LegacyState) -> dict:
        return {"retries": state["retries"] + 1, "trace": state["trace"] + [
            {"node": "retry", "attempt": state["retries"] + 1}]}

    def generate(state: LegacyState) -> dict:
        raw = generate_answer(llm, state["question"], state["context"])
        out = validate_output(raw, state["sources"])
        status = ("abstained" if (out.is_abstain or not out.answer.strip())
                  else "answered")
        return {"answer": out.answer, "status": status, "trace": state["trace"] + [
            {"node": "generate", "status": status,
             "invalid_citations": out.invalid_citations}]}

    def abstain(state: LegacyState) -> dict:
        return {"answer": ABSTAIN_REPLY, "status": "abstained",
                "trace": state["trace"] + [{"node": "abstain"}]}

    def escalate(state: LegacyState) -> dict:
        return {"answer": ESCALATE_REPLY, "status": "escalated",
                "trace": state["trace"] + [{"node": "escalate"}]}

    g = StateGraph(LegacyState)
    g.add_node("retrieve", retrieve)
    g.add_node("rerank", rerank)
    g.add_node("jev", jev)
    g.add_node("retry_retrieve", retry_retrieve)
    g.add_node("generate", generate)
    g.add_node("abstain", abstain)
    g.add_node("escalate", escalate)
    g.set_entry_point("retrieve")
    g.add_edge("retrieve", "rerank")
    g.add_edge("rerank", "jev")
    g.add_conditional_edges("jev", route_after_jev,
                            {"generate": "generate", "escalate": "escalate",
                             "retry_retrieve": "retry_retrieve",
                             "abstain": "abstain"})
    g.add_edge("retry_retrieve", "retrieve")
    g.add_edge("generate", END)
    g.add_edge("abstain", END)
    g.add_edge("escalate", END)
    return g.compile()


def run_legacy(graph, question: str) -> dict:
    """Runner dengan bentuk return yang sama dengan run_workflow —
    supaya run_case() di benchmark bisa dipakai tanpa diubah."""
    check = validate_input(question)
    if check.status == "rejected":
        return {"answer": "Input tidak valid atau terlalu panjang.",
                "status": "rejected", "trace": [{"node": "input_validation"}],
                "sources": [], "jev": {}}
    if check.status == "too_long_moderate":
        return {"answer": LENGTH_REPLY, "status": "rejected",
                "trace": [{"node": "input_validation", "reason": check.reason}],
                "sources": [], "jev": {}}
    if check_injection(question).flagged:
        return {"answer": INJECTION_REPLY, "status": "injection_blocked",
                "trace": [{"node": "injection_filter"}],
                "sources": [], "jev": {}}

    init: LegacyState = {"question": question, "chunks": [], "context": "",
                         "sources": [], "retries": 0, "jev": {},
                         "answer": "", "status": "", "trace": []}
    return graph.invoke(init)
