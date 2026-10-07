# Phase 4 — Benchmark: llm-judge

Run: 2026-10-07T20:04:56 | generator: deepseek/deepseek-v4.1-flash | jev: jev-latest | top-K=5

## Results

| Metric | Value |
|---|---:|
| Cases | 36 (labeled: 36) |
| Decision accuracy | 78% |
| HitRate@5 | 93% |
| Recall@5 | 0.900 |
| Citation correctness | 100% |
| Citation completeness | 72% |
| Retry rate | 11% |
| Avg Jev calls/query | 1.083 |
| P50 latency (s) | 4.235 |
| P95 latency (s) | 11.758 |

## Per-case decisions

| Case | Expected | Decision | Match | Jev calls | Latency (s) |
|---|---|---|---|---:|---:|
| ret-001 | answered | answered | OK | 1 | 10.487 |
| ret-002 | answered | answered | OK | 1 | 3.468 |
| ret-003 | abstained | answered | X | 1 | 5.478 |
| ret-004 | answered | answered | OK | 1 | 5.164 |
| ret-005 | answered | answered | OK | 1 | 4.049 |
| ret-006 | escalated | escalated | OK | 1 | 3.025 |
| ret-007 | answered | answered | OK | 1 | 3.937 |
| ret-008 | answered | answered | OK | 1 | 3.92 |
| ret-009 | answered | answered | OK | 1 | 4.746 |
| ret-010 | answered | answered | OK | 1 | 5.349 |
| ret-011 | answered | answered | OK | 1 | 5.037 |
| ret-012 | answered | answered | OK | 1 | 3.56 |
| ret-013 | answered | abstained | X | 1 | 3.949 |
| ret-014 | answered | abstained | X | 1 | 6.753 |
| ret-015 | answered | escalated | X | 1 | 2.458 |
| ret-016 | answered | answered | OK | 1 | 4.276 |
| ret-017 | answered | answered | OK | 1 | 4.019 |
| ret-018 | abstained | abstained | OK | 2 | 4.779 |
| ret-019 | answered | answered | OK | 1 | 4.509 |
| ret-020 | answered | abstained | X | 1 | 15.497 |
| ret-021 | answered | answered | OK | 1 | 4.235 |
| ret-022 | answered | answered | OK | 1 | 3.864 |
| ret-023 | abstained | abstained | OK | 2 | 10.364 |
| ret-024 | answered | abstained | X | 1 | 4.026 |
| ret-025 | answered | answered | OK | 1 | 2.335 |
| ret-026 | abstained | answered | X | 2 | 11.758 |
| ret-027 | answered | answered | OK | 1 | 13.325 |
| ret-028 | answered | answered | OK | 1 | 10.632 |
| ret-029 | answered | answered | OK | 1 | 2.495 |
| ret-030 | answered | answered | OK | 1 | 7.864 |
| G1 | answered | answered | OK | 1 | 2.947 |
| G2 | answered | answered | OK | 1 | 3.291 |
| G3 | abstained | abstained | OK | 2 | 5.477 |
| G4 | escalated | escalated | OK | 1 | 1.68 |
| G5 | abstained | escalated | X | 1 | 1.521 |
| G6 | injection_blocked | injection_blocked | OK | 0 | 0.0 |
