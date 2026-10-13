"""PRD Phase 6 T4/S1 — sweep threshold gate SECARA OFFLINE.

Baca results-jev.json (harus berisi gate_scores + completeness — patch
run_eval 2026-10-13), lalu simulasikan decide_sufficiency() (fungsi murni,
kode produksi yang sama) pada grid threshold. Tanpa panggilan API.

Metrik per kombinasi:
  rescued   : kasus expected=answered yang dulu abstain -> kini sufficient
  dangerous : kasus expected=abstained yang kini sufficient (mode berbahaya)
  regressed : kasus yang dulu answered -> kini tidak sufficient

Pemakaian:
  python src/flowdesk/evaluation/calibrate_thresholds.py
  python src/flowdesk/evaluation/calibrate_thresholds.py --step 0.05
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from flowdesk.jev.decision import decide_sufficiency

ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / "evaluation" / "results-jev.json"

BASE = {"injection_discard": 0.70, "relevant_min": 0.45,
        "evidence_min": 0.55}          # nilai produksi saat ini
BASE_COMPLETENESS = 0.75


def simulate(scores: dict, thresholds: dict, completeness: float | None,
             comp_threshold: float) -> str:
    """Simulasi keputusan wave-1: sufficient / uncertain / insufficient.

    Cukup utk kalibrasi arah: 'sufficient' = akan menjawab; lainnya tidak.
    """
    if not scores:
        return "insufficient"
    out = decide_sufficiency(scores, thresholds, unscored_left=0)
    d = out["decision"]
    if (d == "sufficient" and completeness is not None
            and completeness < comp_threshold):
        d = "uncertain"
    return d


def sweep(rows: list, evidence_grid: list, comp_grid: list) -> list[dict]:
    """Return hasil simulasi per kombinasi threshold."""
    report = []
    for ev in evidence_grid:
        for comp in comp_grid:
            th = {**BASE, "evidence_min": ev}
            rescued, dangerous, regressed = [], [], []
            for r in rows:
                scores = r.get("gate_scores")
                if not scores:
                    continue
                exp = r.get("expected_decision")
                sim = simulate(scores, th, r.get("completeness"), comp)
                was_answered = r.get("decision") == "answered"
                now_sufficient = sim == "sufficient"
                if exp == "answered" and not was_answered and now_sufficient:
                    rescued.append(r["id"])
                if exp == "abstained" and now_sufficient:
                    dangerous.append(r["id"])
                if was_answered and exp == "answered" and not now_sufficient:
                    regressed.append(r["id"])
            report.append({
                "evidence_min": ev, "completeness": comp,
                "rescued": rescued, "n_rescued": len(rescued),
                "dangerous": dangerous, "n_dangerous": len(dangerous),
                "regressed": regressed, "n_regressed": len(regressed)})
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", type=float, default=0.05,
                    help="step grid evidence_min (dari 0.55 turun ke 0.35)")
    args = ap.parse_args()

    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    rows = data.get("rows", [])
    with_scores = [r for r in rows if r.get("gate_scores")]
    if not with_scores:
        raise SystemExit(
            "results-jev.json belum berisi gate_scores — jalankan ulang "
            "run_eval.py setelah patch capture (2026-10-13).")

    ev_grid = sorted({round(0.55 - i * args.step, 2)
                      for i in range(int(0.20 / args.step) + 1)} |
                     {round(0.55 + i * args.step, 2)
                      for i in range(int(0.20 / args.step) + 1)})   # 0.35..0.75
    comp_grid = [0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60]

    report = sweep(rows, ev_grid, comp_grid)

    print(f"kasus dengan gate_scores: {len(with_scores)}/{len(rows)}")
    print(f"grid evidence_min: {ev_grid} | completeness: {comp_grid}\n")
    print(f"{'ev_min':>6} {'compl':>6} {'rescued':>8} {'danger':>7} "
          f"{'regr':>5}  rescued_ids")
    for rep in sorted(report, key=lambda x: (-x["n_rescued"],
                                             x["n_dangerous"])):
        print(f"{rep['evidence_min']:>6} {rep['completeness']:>6} "
              f"{rep['n_rescued']:>8} {rep['n_dangerous']:>7} "
              f"{rep['n_regressed']:>5}  {', '.join(rep['rescued']) or '-'}")

    print("\naturan pemilihan: n_rescued maksimal DENGAN n_dangerous = 0 "
          "dan n_regressed = 0; lalu konfirmasi via run_eval (1x run).")


if __name__ == "__main__":
    main()
