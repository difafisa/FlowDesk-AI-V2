"""PRD Phase 04 — LangGraph workflow + Jev decision layer.

START -> guardrails -> retrieve -> rerank -> jev -> 
  sufficient    -> generate -> citation_validation -> END (answered)
  uncertain(+retry left) -> retry_retrieve -> jev (loop)
  uncertain(no retry left) -> abstain -> END
  insufficient  -> escalate -> END

Guardrail deterministic (input/injection) tetap kode biasa SEBELUM graph —
LangGraph mengatur branching keputusan, bukan validasi murah (PRD 3.7)."""
from typing import TypedDict
from langgraph.graph import StateGraph, END
from flowdesk.guardrails.config import TOP_K, MAX_JEV_RETRIES, RETRY_TOP_K
from flowdesk.guardrails.input_validator import validate_input
from flowdesk.guardrails.injection_filter import check_injection
from flowdesk.jev.client import JevClient
from flowdesk.rag.context_builder import build_context
from flowdesk.rag.generator import generate_answer
from flowdesk.rag.output_validator import validate_output
from flowdesk.rag.dedupe import dedupe_chunks


ABSTAIN_REPLY = ("Maaf, saya belum menemukan informasi yang cukup untuk "
                 "menjawab pertanyaan tersebut.")
ESCALATE_REPLY = "Saya akan meneruskan kasus ini ke tim support untuk diperiksa."
INJECTION_REPLY = "Maaf, saya tidak dapat membantu dengan permintaan tersebut."
LENGTH_REPLY = ("Pesan Anda terlalu panjang. Silakan kirim bagian error atau "
                "pertanyaan utamanya.")


class WorkflowState(TypedDict):
    question: str
    chunks: list          # hasil retrieval (list[dict])
    context: str
    sources: list
    retries: int
    jev: dict             # {"decision": ..., "reason": ..., "parse_ok": ...}
    answer: str
    status: str           # answered | abstained | escalated | rejected | injection_blocked
    trace: list           # jejak keputusan utk gate PRD & observability Phase 6


def route_after_jev(state: WorkflowState) -> str:
    """Router conditional edge: keputusan Jev -> nama node tujuan.
    Aturan (PRD Phase 04):
    - sufficient    -> generate
    - insufficient  -> escalate (tanpa retry: evidence memang tidak ada)
    - uncertain     -> retry bila masih ada jatah retry, selain itu abstain
    """
    d = state["jev"]["decision"]
    if d == "sufficient":
        return "generate"
    if d == "insufficient":
        return "escalate"
    return "retry_retrieve" if state["retries"] < MAX_JEV_RETRIES else "abstain"


def build_graph(llm, jev_client, retriever):
    """Kompilasi graph. Dependensi (llm/jev_client/retriever) diakses node
    lewat CLOSURE — bukan lewat state (LangGraph membuang key di luar
    skema WorkflowState; pelajaran dari KeyError '_retriever').
    jev_client: flowdesk.jev.client.JevClient (Jev asli, bukan LLM)."""

    def retrieve(state: WorkflowState) -> dict:
        k = RETRY_TOP_K if state["retries"] > 0 else TOP_K
        chunks = retriever.retrieve(state["question"], k=k)
        return {"chunks": chunks, "trace": state["trace"] + [
            {"node": "retrieve", "k": k, "n_chunks": len(chunks)}]}

    def rerank(state: WorkflowState) -> dict:
        """Dedupe per chunk_id (lihat flowdesk/rag/dedupe.py untuk rasional)."""
        unique = dedupe_chunks(state["chunks"])
        return {"chunks": unique, "trace": state["trace"] + [
            {"node": "rerank", "after_dedupe": len(unique)}]}


    def jev_node(state: WorkflowState) -> dict:
        context, sources = build_context(state["chunks"])
        d = jev_client.decide(state["question"], context)
        return {"context": context, "sources": sources,
                "jev": {"decision": d.decision, "reason": d.reason,
                        "parse_ok": d.parse_ok},
                "trace": state["trace"] + [
            {"node": "jev", "decision": d.decision, "reason": d.reason}]}

    def retry_retrieve(state: WorkflowState) -> dict:
        return {"retries": state["retries"] + 1, "trace": state["trace"] + [
            {"node": "retry", "attempt": state["retries"] + 1}]}

    def generate(state: WorkflowState) -> dict:
        raw = generate_answer(llm, state["question"], state["context"])
        out = validate_output(raw, state["sources"])
        status = "abstained" if out.is_abstain else "answered"
        return {"answer": out.answer, "status": status, "trace": state["trace"] + [
            {"node": "generate", "status": status,
             "invalid_citations": out.invalid_citations}]}

    def abstain(state: WorkflowState) -> dict:
        return {"answer": ABSTAIN_REPLY, "status": "abstained",
                "trace": state["trace"] + [{"node": "abstain"}]}

    def escalate(state: WorkflowState) -> dict:
        return {"answer": ESCALATE_REPLY, "status": "escalated",
                "trace": state["trace"] + [
            {"node": "escalate", "jev_reason": state["jev"].get("reason", "")}]}

    g = StateGraph(WorkflowState)
    g.add_node("retrieve", retrieve)
    g.add_node("rerank", rerank)
    g.add_node("jev", jev_node)
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


def run_workflow(graph, question: str) -> WorkflowState:
    """Entry point publik. Guardrail deterministic sebelum graph."""
    check = validate_input(question)
    if check.status == "rejected":
        return {"answer": "Input tidak valid atau terlalu panjang.",
                "status": "rejected", "trace": [{"node": "input_validation"}]}
    if check.status == "too_long_moderate":
        return {"answer": LENGTH_REPLY, "status": "rejected",
                "trace": [{"node": "input_validation", "reason": check.reason}]}
    if check_injection(question).flagged:
        return {"answer": INJECTION_REPLY, "status": "injection_blocked",
                "trace": [{"node": "injection_filter"}]}

    init: WorkflowState = {"question": question, "chunks": [], "context": "",
                           "sources": [], "retries": 0, "jev": {},
                           "answer": "", "status": "", "trace": []}
    return graph.invoke(init)



  
