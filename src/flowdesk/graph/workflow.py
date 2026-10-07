"""PRD Phase 04 — LangGraph workflow + Jev passage gate (Tahap 3-4).

START -> guardrails (di luar graph) -> retrieve -> rerank -> jev_gate -> jev_decide ->
  sufficient    -> generate -> END (answered)
  insufficient  -> scope_check: in_scope -> abstain | out_of_scope -> escalate -> END
  uncertain     -> retry (K lebih besar; chunk terskor tidak dinilai ulang) | abstain
  need_more     -> retry (gelombang berikutnya) | abstain

Tahap 3: jev_gate menilai TIAP CHUNK (3 Noul/chunk, paralel, cache antar
gelombang lewat state["scores"]).
Tahap 4: keputusan murni fungsi kode (decide_sufficiency) — router lama
dipertahankan, hanya ditambah cabang need_more dan in_scope.
Guardrail deterministic tetap kode biasa SEBELUM graph (PRD 3.7).
"""
from typing import TypedDict
from langgraph.graph import StateGraph, END

from flowdesk.guardrails.config import (TOP_K, MAX_JEV_RETRIES, RETRY_TOP_K,
                                        JEV_GATE_THRESHOLDS, JEV_THRESHOLDS)
from flowdesk.guardrails.input_validator import validate_input
from flowdesk.guardrails.injection_filter import check_injection
from flowdesk.jev.client import JevClient
from flowdesk.jev.decision import decide_sufficiency
from flowdesk.jev.passage_gate import score_passages
from flowdesk.rag.context_builder import build_context
from flowdesk.rag.dedupe import dedupe_chunks
from flowdesk.rag.generator import generate_answer
from flowdesk.rag.output_validator import validate_output
from flowdesk.rag.citation_verifier import verify_citations


ABSTAIN_REPLY = ("Maaf, saya belum menemukan informasi yang cukup untuk "
                 "menjawab pertanyaan tersebut.")
ESCALATE_REPLY = "Saya akan meneruskan kasus ini ke tim support untuk diperiksa."
INJECTION_REPLY = "Maaf, saya tidak dapat membantu dengan permintaan tersebut."
LENGTH_REPLY = ("Pesan Anda terlalu panjang. Silakan kirim bagian error atau "
                "pertanyaan utamanya.")


class WorkflowState(TypedDict):
    question: str
    chunks: list          # hasil retrieval (list[dict])
    scores: dict          # {chunk_id: skor passage gate} — cache antar gelombang
    context: str
    sources: list
    retries: int
    jev: dict             # {"decision", "reason", "parse_ok", "in_scope"}
    answer: str
    status: str           # answered | abstained | escalated | rejected | injection_blocked
    trace: list           # jejak keputusan utk gate PRD & observability Phase 6


def route_after_jev(state: WorkflowState) -> str:
    """Router conditional edge — aturan lama dipertahankan, ditambah:
    - need_more: masih ada chunk belum terskor -> gelombang berikutnya
    - insufficient + scope_check (T4b): topik produk valid -> abstain,
      di luar lingkup -> escalate."""
    d = state["jev"]["decision"]
    if d == "sufficient":
        return "generate"
    if d == "insufficient":
        return "abstain" if state["jev"].get("in_scope", True) else "escalate"
    # uncertain / need_more -> coba gelombang berikutnya bila masih ada jatah
    return "retry_retrieve" if state["retries"] < MAX_JEV_RETRIES else "abstain"


def build_graph(llm, jev_client, retriever):
    """Kompilasi graph. Dependensi diakses node lewat CLOSURE — bukan lewat
    state (LangGraph membuang key di luar skema WorkflowState; pelajaran
    dari KeyError '_retriever'). jev_client: JevClient (Jev asli)."""

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

    def jev_gate(state: WorkflowState) -> dict:
        """Tahap 3 — nilai tiap chunk (3 Noul/chunk, paralel).
        state["scores"] adalah cache antar gelombang: chunk yang sudah
        terskor tidak memicu panggilan ulang saat retry K lebih besar."""
        new = score_passages(jev_client, state["question"], state["chunks"],
                             cache=state["scores"])
        merged = {**state["scores"], **new}
        return {"scores": merged, "trace": state["trace"] + [
            {"node": "jev_gate", "scored_this_wave": len(new),
             "total_scored": len(merged)}]}

    def jev_decide(state: WorkflowState) -> dict:
        """Tahap 4 — keputusan murni di kode dari skor; scope_check (1 Noul)
        hanya saat insufficient, jadi tanpa biaya di jalur normal."""
        unscored = len(state["chunks"]) - len(state["scores"])
        out = decide_sufficiency(state["scores"], JEV_GATE_THRESHOLDS, unscored)
        d = out["decision"]

        in_scope = None
        if d == "insufficient":
            in_scope = jev_client.scope_check(state["question"])

        included_ids = set(out["included"])
        included = [ch for ch in state["chunks"] if ch["chunk_id"] in included_ids]
        context, sources = build_context(included)
        completeness = None
        if out["included"]:
            completeness = jev_client.check_completeness(
                state["question"], context)
            if completeness < JEV_THRESHOLDS["noul_sufficient"]:
                d = "uncertain"     # evidence terpilih belum lengkap -> retry/abstain

        reason = (f"included={len(out['included'])}, "
                  f"relevant_only={len(out['relevant_only'])}, "
                  f"discarded={len(out['discarded'])} "
                  f"({out['discard_reasons']})"
                  + (f", in_scope={in_scope}" if in_scope is not None else ""))
        return {"context": context, "sources": sources,
                "jev": {"decision": d, "reason": reason, "parse_ok": True,
                        "in_scope": in_scope},
                "trace": state["trace"] + [
            {"node": "jev", "decision": d, "reason": reason,
             "included": out["included"],
             "discarded": out["discard_reasons"]}]}

    def retry_retrieve(state: WorkflowState) -> dict:
        return {"retries": state["retries"] + 1, "trace": state["trace"] + [
            {"node": "retry", "attempt": state["retries"] + 1}]}

    def generate(state: WorkflowState) -> dict:
        raw = generate_answer(llm, state["question"], state["context"])
        out = validate_output(raw, state["sources"])
        if out.is_abstain or not out.answer.strip():
            return {"answer": out.answer or "", "status": "abstained",
                    "trace": state["trace"] + [
                {"node": "generate", "status": "abstained",
                 "invalid_citations": out.invalid_citations}]}

        content_by_index = {}
        for s in state["sources"]:
            ch = next((c for c in state["chunks"]
                       if c["chunk_id"] == s["chunk_id"]), None)
            if ch:
                content_by_index[s["index"]] = ch["content"]

        check = verify_citations(jev_client, out.answer,
                                 state["sources"], content_by_index)
        if check.contradicted:
            # generator membuat klaim yang bertentangan dengan sumbernya ->
            # jangan tampilkan; abstain dengan alasan tercatat
            return {"answer": ABSTAIN_REPLY, "status": "abstained",
                    "trace": state["trace"] + [
                {"node": "generate", "status": "abstained",
                 "reason": f"citation contradicted: {check.contradicted}"}]}

        status = "answered"
        return {"answer": check.verified_answer, "status": status,
                "trace": state["trace"] + [
            {"node": "generate", "status": status,
             "invalid_citations": out.invalid_citations,
             "citation_dropped": check.dropped_markers,
             "needs_review": check.needs_review}]}


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
    g.add_node("jev_gate", jev_gate)
    g.add_node("jev_decide", jev_decide)
    g.add_node("retry_retrieve", retry_retrieve)
    g.add_node("generate", generate)
    g.add_node("abstain", abstain)
    g.add_node("escalate", escalate)

    g.set_entry_point("retrieve")
    g.add_edge("retrieve", "rerank")
    g.add_edge("rerank", "jev_gate")
    g.add_edge("jev_gate", "jev_decide")
    g.add_conditional_edges("jev_decide", route_after_jev,
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

    init: WorkflowState = {"question": question, "chunks": [], "scores": {},
                           "context": "", "sources": [], "retries": 0,
                           "jev": {}, "answer": "", "status": "", "trace": []}
    return graph.invoke(init)
