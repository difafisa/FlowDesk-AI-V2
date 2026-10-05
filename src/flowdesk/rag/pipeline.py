"""Phase 3 pipeline: A validation -> retrieval -> C context -> D LLM -> E validation.
Sengaja fungsi berurutan TANPA LangGraph — orkestrasi graf + branching
(sufficient/uncertain/insufficient) = Phase 4 (PRD Phase 04)."""
from dataclasses import dataclass, field

from flowdesk.guardrails.input_validator import validate_input
from flowdesk.guardrails.injection_filter import check_injection
from flowdesk.guardrails.config import TOP_K
from flowdesk.rag.context_builder import build_context
from flowdesk.rag.generator import generate_answer
from flowdesk.rag.output_validator import validate_output

INJECTION_REPLY = "Maaf, saya tidak dapat membantu dengan permintaan tersebut."
LENGTH_REPLY = ("Pesan Anda terlalu panjang. Silakan kirim bagian error atau "
                "pertanyaan utamanya.")
ABSTAIN_REPLY = ("Maaf, saya belum menemukan informasi yang cukup untuk "
                 "menjawab pertanyaan tersebut.")


@dataclass
class PipelineResult:
    answer: str
    sources: list[dict] = field(default_factory=list)
    status: str = "answered"   # answered | abstained | rejected | injection_blocked


def run_pipeline(llm, retriever, question: str) -> PipelineResult:
    # --- Tahap A: input validation (3-tier, deterministic)
    check = validate_input(question)
    if check.status == "rejected":
        return PipelineResult("Input tidak valid atau terlalu panjang.", [], "rejected")
    if check.status == "too_long_moderate":
        return PipelineResult(LENGTH_REPLY, [], "rejected")

    # --- Tahap B: injection filter (dipisah dari length, PRD 3.2)
    if check_injection(question).flagged:
        return PipelineResult(INJECTION_REPLY, [], "injection_blocked")

    # --- Retrieval (aset teruji dari Phase 2)
    chunks = retriever.retrieve(question, k=TOP_K)
    if not chunks:
        return PipelineResult(ABSTAIN_REPLY, [], "abstained")

    # --- Tahap C: context + token budget
    context, sources = build_context(chunks)

    # --- Tahap D: grounded generation
    raw = generate_answer(llm, question, context)

    # --- Tahap E: output + citation validation
    out = validate_output(raw, sources)
    status = "abstained" if out.is_abstain else "answered"
    return PipelineResult(out.answer, sources, status)
