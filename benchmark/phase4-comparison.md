# Phase 4 — Baseline vs Passage Gate

## Objective

Membandingkan sistem RAG baseline dengan passage-level
evidence gate pada dataset yang sama.

## Dataset

- Cases: 36 gate cases (G1-G6)
- Dataset: Phase 4 gate benchmark
- Same questions and expected labels
- Same retrieval/index
- Same generator model (deepseek/deepseek-v4.1-flash)
- Same top-K (5)

## Results

| Metric | Baseline | New Gate | Δ |
|---|---:|---:|---:|
| Decision accuracy | 81% | 78% | -3% |
| Recall@5 | 0.900 | 0.900 | +0.000 |
| HitRate@5 | 93% | 93% | +0% |
| Citation correctness | 100% | 100% | +0% |
| Citation completeness | 92% | 90% | -2% |
| Retry rate | 33% | 33% | +0% |
| Avg Jev calls/query | 7.889 | 7.889 | +0.000 |
| P50 latency | 3.300 | 3.472 | +0.172 |
| P95 latency | 6.989 | 5.640 | -1.349 |

## Decision Comparison

| Case | Expected | Baseline | New Gate |
|---|---|---|---|
| ret-001 | answered | answered | answered |
| ret-002 | answered | answered | answered |
| ret-003 | abstained | abstained | abstained |
| ret-004 | answered | answered | answered |
| ret-005 | answered | answered | answered |
| ret-006 | escalated | answered | answered |
| ret-007 | answered | answered | answered |
| ret-008 | answered | answered | answered |
| ret-009 | answered | answered | answered |
| ret-010 | answered | answered | answered |
| ret-011 | answered | answered | answered |
| ret-012 | answered | answered | answered |
| ret-013 | answered | abstained | abstained |
| ret-014 | answered | answered | answered |
| ret-015 | answered | abstained | abstained |
| ret-016 | answered | abstained | abstained |
| ret-017 | answered | answered | answered |
| ret-018 | abstained | abstained | abstained |
| ret-019 | answered | answered | answered |
| ret-020 | answered | answered | answered |
| ret-021 | answered | abstained | abstained |
| ret-022 | answered | answered | answered |
| ret-023 | abstained | abstained | abstained |
| ret-024 | answered | answered | abstained |
| ret-025 | answered | answered | answered |
| ret-026 | abstained | abstained | abstained |
| ret-027 | answered | answered | answered |
| ret-028 | answered | answered | answered |
| ret-029 | answered | abstained | abstained |
| ret-030 | answered | abstained | abstained |
| G1 | answered | answered | answered |
| G2 | answered | answered | answered |
| G3 | abstained | abstained | abstained |
| G4 | escalated | escalated | escalated |
| G5 | abstained | abstained | abstained |
| G6 | injection_blocked | injection_blocked | injection_blocked |

## Findings

### Improved
- (isi manual)

### Regressions
- (isi manual)

### Trade-offs
- (isi manual)

## Conclusion

The passage-level gate ...

