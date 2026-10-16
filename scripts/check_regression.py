"""BACKLOG S4 — regression check hasil eval vs baseline terkunci (Phase 7.6).

Baseline: run final Phase 5, 2026-10-13 (evaluation/results-jev.json,
51 kasus, generator nvidia/nemotron-3-ultra-550b-a55b, jev-latest).
Ambang = nilai baseline - margin (lihat THRESHOLDS) supaya noise wajar
tidak gagal, tapi regresi nyata ketahuan.

Pemakaian:
    python scripts/check_regression.py                          # file default
    python scripts/check_regression.py evaluation/results-X.json
Exit code: 0 = semua metrik lolos, 1 = ada regresi (siap CI).
"""
import json
import sys
from pathlib import Path

DEFAULT_RESULTS = (Path(__file__).resolve().parents[1]
                   / "evaluation" / "results-jev.json")
EXPECTED_N_CASES = 51      # dataset final Phase 5 (S5: verifikasi label)

# (key di 'aggregate', ambang, deskripsi) — ambang = baseline - margin.
THRESHOLDS = [
    ("decision_accuracy",   0.84, "decision accuracy (baseline 0.863)"),
    ("abstention_accuracy", 0.70, "abstention accuracy (baseline 0.75)"),
    ("answered_accuracy",   0.89, "answered accuracy (baseline 0.917)"),
    ("hit_rate_5",          0.85, "HitRate@5 - kontrol retrieval (baseline 0.87)"),
    ("recall_5",            0.75, "Recall@5 (baseline 0.793)"),
    ("groundedness_mean",   0.82, "groundedness mean (baseline 0.847)"),
]
CORRECTNESS_MIN = 30       # baseline: 32 correct

# Informasional (TIDAK menggagalkan):
# - escalation_accuracy: hanya n=2 kasus escalate (baseline 0.5) — terlalu
#   kecil untuk digate; pantau manual (S3 / ds-044).
# - avg_jev_calls, p50, p95: biaya & latency — dicatat, bukan digate.


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_RESULTS
    if not path.exists():
        print(f"FAIL: results tidak ditemukan: {path}")
        return 1

    data = json.loads(path.read_text(encoding="utf-8"))
    agg, meta = data.get("aggregate", {}), data.get("meta", {})
    failed: list[str] = []

    print(f"Run     : {meta.get('timestamp', '?')} "
          f"(generator: {meta.get('generator', '?')}, "
          f"jev: {meta.get('jev_model', '?')})")
    print(f"Results : {path.name}\n")

    n = agg.get("n_cases")
    if n != EXPECTED_N_CASES:
        print(f"WARN: n_cases={n} != {EXPECTED_N_CASES} — dataset berubah "
              f"(S5); perbandingan vs baseline bisa tidak sahih.\n")

    print(f"{'Metrik':<22}{'Nilai':>8}{'Ambang':>8}   Status")
    print("-" * 54)
    for key, threshold, _desc in THRESHOLDS:
        val = agg.get(key)
        if val is None:
            failed.append(key)
            print(f"{key:<22}{'—':>8}{threshold:>8.2f}   FAIL (metrik tidak ada)")
            continue
        ok = val >= threshold
        if not ok:
            failed.append(key)
        print(f"{key:<22}{val:>8.3f}{threshold:>8.2f}   {'PASS' if ok else 'FAIL'}")

    corr = (agg.get("correctness") or {}).get("correct")
    if corr is None:
        failed.append("correctness")
        print(f"{'correctness':<22}{'—':>8}{CORRECTNESS_MIN:>8}   FAIL (metrik tidak ada)")
    else:
        ok = corr >= CORRECTNESS_MIN
        if not ok:
            failed.append("correctness")
        print(f"{'correctness':<22}{corr:>8}{CORRECTNESS_MIN:>8}   {'PASS' if ok else 'FAIL'}")

    print("-" * 54)
    print(f"info: escalation_accuracy={agg.get('escalation_accuracy')} "
          f"(n kecil — tidak digate, lihat S3)")
    print(f"info: avg_jev_calls={agg.get('avg_jev_calls')}, "
          f"p50={agg.get('p50_latency')}s, p95={agg.get('p95_latency')}s")

    print()
    if failed:
        print("REGRESI TERDETEKSI:")
        for f in failed:
            print(f"  - {f}")
        return 1
    print("SEMUA METRIK LOLOS — tidak ada regresi vs baseline Phase 5.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
