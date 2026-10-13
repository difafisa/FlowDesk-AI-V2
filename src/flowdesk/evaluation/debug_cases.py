"""PRD Phase 6 T4 — debugging view: "retrieval salah atau Jev salah?"

Membaca results-*.json (output run_eval.py) + dataset.json (label TERKINI),
mengklasifikasikan tiap miss ke akar masalah, lalu menulis
evaluation/debug-cases.md + ringkasan console.

Klasifikasi (sesuai PRD T4):
  retrieval_miss    : hit@5 = 0                 -> evidence tidak ditemukan
  gate_miss         : hit@5 = 1 tapi abstained  -> gate terlalu ketat (S1)
  scope_miss        : jalur escalate/abstain keliru lewat scope/routing (S3)
  gate_too_loose    : menjawab padahal label abstain/escalate (gagal berbahaya)
  generation_miss   : keputusan benar tapi groundedness/correctness buruk
  shared_miss       : gagal di KEDUA varian     -> bukan salah judge (upstream)

Catatan: klasifikasi digabung dengan label dataset TERKINI (bukan label saat
run) — perubahan label (mis. relabel ds-006) tercatat di section label_changed.

Pemakaian:
  python src/flowdesk/evaluation/debug_cases.py              # kedua varian
  python src/flowdesk/evaluation/debug_cases.py --variant jev
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVAL_DIR = ROOT / "evaluation"
DATASET = ROOT / "src" / "flowdesk" / "evaluation" / "dataset.json"

LOW_GROUNDEDNESS = 0.70        # ambang sama dengan report run_eval

ACTION_BY_CAUSE = {
    "retrieval_miss": "perbaiki retrieval (reranker/chunking) atau verifikasi expected_sources",
    "gate_miss": "S1 — kalibrasi threshold (evidence_min 0.55->0.45, completeness 0.75->0.65)",
    "scope_miss": "S3 — kalibrasi scope_check / routing escalate",
    "gate_too_loose": "PERIKSA MANUAL — mode gagal berbahaya (menjawab tanpa dasar)",
    "generation_miss": "prompt generator / disiplin citation / pertimbangkan model lain",
    "unknown": "data tidak cukup — cek manual",
    "unknown_no_baseline": "kasus tanpa expected_sources — tambahkan baseline retrieval",
}


# --- klasifikasi murni (unit-testable, tanpa I/O) ------------------------

def classify_decision_miss(row: dict, case: dict) -> str:
    """Akar masalah untuk satu kasus decision-miss (decision != label kini)."""
    exp = case.get("expected_decision")
    got = row.get("decision")
    hit = row.get("hit@5")

    if exp == "answered":
        if got == "abstained":
            if hit == 0:
                return "retrieval_miss"
            if hit == 1:
                return "gate_miss"
            return "unknown_no_baseline" if hit is None else "gate_miss"
        if got == "escalated":
            return "scope_miss"
    if exp == "abstained":
        if got == "answered":
            return "gate_too_loose"
        if got == "escalated":
            return "scope_miss"
    if exp == "escalated":
        if got == "answered":
            return "gate_too_loose"
        if got == "abstained":
            return "scope_miss"
    return "unknown"


def quality_flags(row: dict) -> list[str]:
    """Masalah kualitas jawaban (dipakai saat keputusan SUDAH benar)."""
    flags = []
    g = row.get("groundedness")
    if g is not None and g < LOW_GROUNDEDNESS:
        flags.append(f"low_groundedness({g})")
    c = row.get("correctness")
    if c in ("wrong", "partial"):
        flags.append(f"correctness_{c}")
    return flags


def shared_miss_ids(misses_a: list, misses_b: list) -> set:
    """Kasus yang miss di KEDUA varian -> akar masalah di hulu, bukan judge."""
    return {m["id"] for m in misses_a} & {m["id"] for m in misses_b}


def analyze_variant(rows: list, cases: dict) -> dict:
    """Klasifikasi semua baris satu varian terhadap label dataset terkini."""
    misses, quality, label_changed = [], [], []
    for row in rows:
        case = cases.get(row["id"])
        if case is None:
            continue
        stored = row.get("expected_decision")
        current = case.get("expected_decision")
        if stored != current:
            label_changed.append((row["id"], stored, current))
        if current and row.get("decision") != current:
            misses.append({
                "id": row["id"], "category": row.get("category"),
                "expected": current, "got": row.get("decision"),
                "cause": classify_decision_miss(row, case),
                "hit@5": row.get("hit@5"), "recall@5": row.get("recall@5"),
                "groundedness": row.get("groundedness"),
                "correctness": row.get("correctness"),
                "retried": row.get("retried"),
                "question": str(row.get("question", ""))[:70],
            })
        elif row.get("decision") == "answered":
            flags = quality_flags(row)
            if flags:
                quality.append({"id": row["id"], "category": row.get("category"),
                                "flags": flags,
                                "question": str(row.get("question", ""))[:70]})
    misses.sort(key=lambda m: (m["cause"], m["id"]))
    quality.sort(key=lambda q: q["id"])
    return {"misses": misses, "quality": quality, "label_changed": label_changed}


# --- laporan --------------------------------------------------------------

def write_report(path: Path, variants: dict, shared: set) -> None:
    L = ["# Phase 6 T4 — Debugging view: akar masalah per miss", "",
         f"Dibuat: {datetime.now().isoformat(timespec='seconds')} — "
         "klasifikasi digabung dengan label dataset TERKINI", ""]

    if any(v["label_changed"] for v in variants.values()):
        L += ["## Label berubah sejak run (transparansi)", "",
              "| Case | Label saat run | Label kini |", "|---|---|---|"]
        seen = set()
        for v in variants.values():
            for cid, old, new in v["label_changed"]:
                if cid not in seen:
                    seen.add(cid)
                    L.append(f"| {cid} | {old} | {new} |")
        L.append("")

    for name, v in variants.items():
        meta = v["meta"]
        L += [f"## Varian {name} (run {meta.get('timestamp', '?')}, "
              f"generator {meta.get('generator', '?')})", ""]
        dist = Counter(m["cause"] for m in v["misses"])
        if dist:
            L += ["### Distribusi akar masalah", "",
                  "| Akar masalah | Jumlah | Tindakan yang disarankan |",
                  "|---|---:|---|"]
            for cause, n in dist.most_common():
                L.append(f"| {cause} | {n} | {ACTION_BY_CAUSE.get(cause, '')} |")
            L += ["", "### Detail miss", "",
                  "| Case | Kategori | Expected | Got | Akar | hit@5 | "
                  "groundedness | retried | Pertanyaan |",
                  "|---|---|---|---|---|---:|---:|---|---|"]
            for m in v["misses"]:
                L.append(
                    f"| {m['id']} | {m['category']} | {m['expected']} | "
                    f"{m['got']} | {m['cause']} | {m['hit@5'] if m['hit@5'] is not None else '-'} | "
                    f"{m['groundedness'] if m['groundedness'] is not None else '-'} | "
                    f"{'ya' if m['retried'] else 'tidak'} | {m['question']} |")
        else:
            L += ["### Tidak ada miss 🎉", ""]
        if v["quality"]:
            L += ["### Kualitas (keputusan benar, jawaban perlu perhatian)", ""]
            for q in v["quality"]:
                L.append(f"- **{q['id']}** ({q['category']}): "
                         f"{', '.join(q['flags'])} — {q['question']}")
        L.append("")

    if shared:
        L += ["## Shared miss — gagal di KEDUA varian (bukan salah judge)", ""]
        by_id = {m["id"]: m for v in variants.values() for m in v["misses"]}
        for cid in sorted(shared):
            m = by_id[cid]
            L.append(f"- **{cid}** ({m['category']}): expected {m['expected']} — "
                     f"lihat detail di tiap varian; akar masalah di hulu "
                     f"(retrieval/generator/label)")
        L.append("")

    L += ["## Catatan", "",
          "- rows eval tidak menyimpan jev reason/trace lengkap — untuk "
          "bedah per kasus, buka trace Langfuse (run_id) atau jalankan ulang "
          "kasus via ask.py (backlog S7).",
          "- Setelah kalibrasi S1, jalankan ulang run_eval + debug_cases untuk "
          "mengukur perbaikan (loop evaluasi).", ""]
    path.write_text("\n".join(L), encoding="utf-8")


# --- main -----------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["jev", "llm-judge", "both"],
                    default="both")
    args = ap.parse_args()

    cases = {c["id"]: c for c in
             json.loads(DATASET.read_text(encoding="utf-8"))}

    wanted = ["jev", "llm-judge"] if args.variant == "both" else [args.variant]
    variants = {}
    for name in wanted:
        p = EVAL_DIR / f"results-{name}.json"
        if not p.exists():
            print(f"(lewati {name}: {p.name} tidak ada)")
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        variants[name] = {"meta": data.get("meta", {}),
                          **analyze_variant(data.get("rows", []), cases)}

    if not variants:
        print("Tidak ada results-*.json yang bisa dibaca.")
        return

    shared = (shared_miss_ids(variants["jev"]["misses"],
                              variants["llm-judge"]["misses"])
              if len(variants) == 2 else set())

    for name, v in variants.items():
        dist = Counter(m["cause"] for m in v["misses"])
        print(f"\n=== {name} (run {v['meta'].get('timestamp', '?')}) ===")
        print(f"miss: {len(v['misses'])} | kualitas: {len(v['quality'])} | "
              f"label berubah: {len(v['label_changed'])}")
        for cause, n in dist.most_common():
            print(f"  {cause:20s} {n:3d}  -> {ACTION_BY_CAUSE.get(cause, '')}")
    if shared:
        print(f"\nshared miss (kedua varian): {len(shared)} -> "
              f"{', '.join(sorted(shared))}")

    out = EVAL_DIR / "debug-cases.md"
    write_report(out, variants, shared)
    print(f"\nlaporan -> {out}")


if __name__ == "__main__":
    main()
