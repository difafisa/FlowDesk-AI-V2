# Phase 4 — Baseline vs Passage Gate

## Objective

Membandingkan sistem RAG baseline dengan passage-level
evidence gate pada dataset yang sama.

## Dataset

- Cases: 6 gate cases (G1-G6)
- Dataset: Phase 4 gate benchmark
- Same questions and expected labels
- Same retrieval/index
- Same generator model (deepseek/deepseek-v4.1-flash)
- Same top-K (5)

## Results

| Metric | Baseline | New Gate | Δ |
|---|---:|---:|---:|
| Decision accuracy | 100% | 83% | -17% |
| Recall@5 | ... | ... | ... |
| HitRate@5 | ... | ... | ... |
| Citation correctness | 100% | 100% | +0% |
| Citation completeness | 100% | 100% | +0% |
| Retry rate | 17% | 17% | +0% |
| Avg Jev calls/query | 1 | 6.333 | +5.333 |
| P50 latency | 2.107 | 3.606 | +1.499 |
| P95 latency | 34.423 | 64.376 | +29.953 |

## Decision Comparison

| Case | Expected | Baseline | New Gate |
|---|---|---|---|
| G1 | answered | answered | answered |
| G2 | answered | answered | answered |
| G3 | abstained | abstained | abstained |
| G4 | escalated | escalated | escalated |
| G5 | escalated | escalated | abstained |
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

