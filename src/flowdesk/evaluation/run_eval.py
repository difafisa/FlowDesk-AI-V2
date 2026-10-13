"""PRD Phase 05 — evaluator resmi FlowDesk.

Menjalankan evaluation/dataset.json (52 kasus, 9 kategori) melalui graph
produksi, lalu menilai tiap jawaban dengan Jev scorer (groundedness +
correctness), dan menghasilkan laporan metrik lengkap:
  Retrieval : HitRate@5, Recall@5
  Decision  : accuracy keseluruhan + abstention/escalation/answered accuracy
  Generation: groundedness mean, correctness distribution
  Cost      : jev_calls/query (produksi) + scorer calls (evaluasi)
Agregat global + per kategori (9 PRD).

Pemakaian:
  python evaluation/run_eval.py jev                # varian utama
  python evaluation/run_eval.py llm-judge          # pembanding A/B
  python evaluation/run_eval.py jev --limit 6      # dry run murah
  python evaluation/run_eval.py jev --no-scorer    # tanpa generation scoring
"""
import argparse
import json
import re
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# file ini di src/flowdesk/evaluation/ -> root project = 4 tingkat ke atas
ROOT = Path(__file__).resolve().parents[3]

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv()

import os

from flowdesk.embedding.embedder import Embedder
from flowdesk.graph.workflow import build_graph, run_workflow
from flowdesk.jev.client import JevClient
from flowdesk.rag.llm_client import LLMClient
from flowdesk.retrieval.retriever import Retriever
from flowdesk.storage.pgvector_store import VectorStore
from flowdesk.evaluation.grounding_scorer import score_answer

DATASET = ROOT /"src"/"flowdesk"/ "evaluation" / "dataset.json"

def stratified_sample(cases: list[dict], n: int) -> list[dict]:
    """Sampel berlapis dua sumbu: tiap expected_decision min. 1, tiap
    kategori min. 1, sisanya dibagi proporsional per kategori.
    Deterministik (sort by id)."""
    cases = sorted(cases, key=lambda x: x["id"])
    picked: list[dict] = []
    # pass 1: tiap kelas keputusan min. 1 (id terkecil)
    for dec in ("answered", "abstained", "escalated", "injection_blocked"):
        c = next((c for c in cases if c["expected_decision"] == dec), None)
        if c:
            picked.append(c)
    # pass 2: tiap kategori min. 1
    for cat in sorted({c["category"] for c in cases}):
        c = next((c for c in cases if c["category"] == cat
                  and c not in picked), None)
        if c:
            picked.append(c)
    # pass 3: isi sisa kuota merata per kategori (round-robin)
    from collections import defaultdict
    by_cat = defaultdict(list)
    for c in cases:
        if c not in picked:
            by_cat[c["category"]].append(c)
    while len(picked) < n and any(by_cat.values()):
        for cat in sorted(by_cat):
            if by_cat[cat]:
                picked.append(by_cat[cat].pop(0))
                if len(picked) >= n:
                    break
    return picked



def _norm(s: str) -> str:
    return Path(s).as_posix().lower()


def run_case(graph, retriever, jev_client, case: dict, runner,
             use_scorer: bool) -> dict:
    q = case["question"]
    t0 = time.perf_counter()
    r = runner(graph, q)
    latency = time.perf_counter() - t0

    trace = r.get("trace", [])
    scored = sum(s.get("scored_this_wave", 0) for s in trace
                 if s.get("node") == "jev_gate")
    jev_calls = scored + sum(1 for s in trace if s.get("node") == "jev")
    if r.get("jev", {}).get("in_scope") is not None:
        jev_calls += 1                      # scope_check (T4b)
    retried = any(s.get("node") == "retry" for s in trace)
    invalid = next((s.get("invalid_citations") for s in trace
                    if s.get("node") == "generate"), None)
    jev_entry = next((s for s in reversed(trace) if s.get("node") == "jev"),
                     None)

    # citation metrics (logika benchmark Phase 4)
    answer = r.get("answer", "")
    sources = r.get("sources", [])
    cited = [int(m) for m in re.findall(r"\[(\d+)\]", answer)]
    cit = None
    if cited:
        valid_idx = {s["index"] for s in sources}
        distinct_valid = len({c for c in cited if c in valid_idx})
        cit = {"total": len(cited),
               "distinct_valid": distinct_valid,
               "invalid": len(invalid) if invalid else 0,
               "completeness": distinct_valid / len(sources) if sources else 0.0}

    # retrieval metrics (hanya kasus dengan expected_sources)
    hit = recall = None

    # generation scoring (HANYA jawaban 'answered' — template abstain/
    # escalate/blocked bukan klaim faktual, menilainya mencemari metrik)
    scorer_calls = 0
    gen = {"scored": False, "groundedness": None, "correctness": None}
    if use_scorer and r.get("status") == "answered" and answer.strip():
        gen = score_answer(jev_client, answer, r.get("context", ""),
                           case.get("expected_answer") or None)
        scorer_calls = 1 if gen["scored"] else 0


    return {
        "id": case["id"], "category": case["category"], "lang": case["lang"],
        "question": q,
        "expected_decision": case.get("expected_decision"),
        "decision": r.get("status", "?"),
        "match": (r.get("status") == case.get("expected_decision")
                  if case.get("expected_decision") else None),
        "latency_s": round(latency, 3),
        "jev_calls": jev_calls, "scorer_calls": scorer_calls,
        "retried": retried, "citations": cit,
        "hit@5": hit, "recall@5": recall,
        "groundedness": gen["groundedness"], "correctness": gen["correctness"],
        "answer": answer[:300],
        "gate_scores": r.get("scores"),            
        "completeness": (jev_entry or {}).get("completeness"),
        "included": (jev_entry or {}).get("included"),

    }


def _mean(vals):
    vals = [v for v in vals if v is not None]
    return round(statistics.mean(vals), 3) if vals else None


def aggregate(rows: list[dict]) -> dict:
    def acc(subset):
        subset = [r for r in subset if r["match"] is not None]
        return (round(sum(1 for r in subset if r["match"]) / len(subset), 3)
                if subset else None)

    lat = sorted(r["latency_s"] for r in rows)
    hits = [r["hit@5"] for r in rows if r["hit@5"] is not None]
    recalls = [r["recall@5"] for r in rows if r["recall@5"] is not None]
    gens = [r for r in rows if r["groundedness"] is not None]
    correct = [r["correctness"] for r in gens if r["correctness"]]
    pctl = lambda lst, p: (lst[max(0, min(len(lst) - 1,
                           round(p / 100 * (len(lst) - 1))))] if lst else None)
    return {
        "n_cases": len(rows),
        "decision_accuracy": acc(rows),
        "abstention_accuracy": acc([r for r in rows
                                    if r["expected_decision"] == "abstained"]),
        "escalation_accuracy": acc([r for r in rows
                                    if r["expected_decision"] == "escalated"]),
        "answered_accuracy": acc([r for r in rows
                                  if r["expected_decision"] == "answered"]),
        "hit_rate_5": _mean(hits),
        "recall_5": _mean(recalls),
        "groundedness_mean": _mean([r["groundedness"] for r in gens]),
        "n_scored": len(gens),
        "correctness": {v: correct.count(v) for v in
                        ("correct", "partial", "wrong") if correct.count(v)},
        "retry_rate": round(sum(1 for r in rows if r["retried"]) / len(rows), 3),
        "avg_jev_calls": round(statistics.mean(r["jev_calls"] for r in rows), 2),
        "scorer_calls": sum(r["scorer_calls"] for r in rows),
        "p50_latency": pctl(lat, 50),
        "p95_latency": pctl(lat, 95),
    }


def by_category(rows: list[dict]) -> dict:
    out = {}
    for cat, sub in sorted(defaultdict(list, {c: [r for r in rows
                        if r["category"] == c] for c in
                        {r["category"] for r in rows}}).items()):
        a = aggregate(sub)
        out[cat] = {"n": a["n_cases"], "decision_accuracy": a["decision_accuracy"],
                    "abstention": a["abstention_accuracy"],
                    "groundedness": a["groundedness_mean"],
                    "hit_rate_5": a["hit_rate_5"]}
    return out


def write_report(variant, meta, agg, cats, rows, path: Path):
    L = [f"# Phase 5 Evaluation — {variant}", "",
         f"Run: {meta['timestamp']} | generator: {meta['generator']} | "
         f"jev: {meta['jev_model']} | cases: {agg['n_cases']}", "",
         "## Global metrics", "", "| Metric | Value |", "|---|---:|",
         f"| Decision accuracy | {agg['decision_accuracy']} |",
         f"| Abstention accuracy | {agg['abstention_accuracy']} |",
         f"| Escalation accuracy | {agg['escalation_accuracy']} |",
         f"| Answered accuracy | {agg['answered_accuracy']} |",
         f"| HitRate@5 | {agg['hit_rate_5']} |",
         f"| Recall@5 | {agg['recall_5']} |",
         f"| Groundedness (mean) | {agg['groundedness_mean']} "
             f"(n={agg['n_scored']}) |",
         f"| Correctness | {agg['correctness']} |",
         f"| Retry rate | {agg['retry_rate']} |",
         f"| Jev calls/query (prod) | {agg['avg_jev_calls']} |",
         f"| Scorer calls (eval) | {agg['scorer_calls']} |",
         f"| P50 / P95 latency (s) | {agg['p50_latency']} / "
             f"{agg['p95_latency']} |", "",
         "## Per category", "",
         "| Category | n | Decision acc | Abstention | Groundedness | HitRate@5 |",
         "|---|---:|---:|---:|---:|---:|"]
    for cat, c in cats.items():
        L.append(f"| {cat} | {c['n']} | {c['decision_accuracy']} | "
                 f"{c['abstention']} | {c['groundedness']} | {c['hit_rate_5']} |")
    L += ["", "## Misses (decision != expected)", "",
          "| Case | Category | Expected | Got |", "|---|---|---|---|"]
    for r in rows:
        if r["match"] is False:
            L.append(f"| {r['id']} | {r['category']} | "
                     f"{r['expected_decision']} | {r['decision']} |")
    L += ["", "## Low groundedness (< 0.70)", ""]
    lows = [r for r in rows
            if r["groundedness"] is not None and r["groundedness"] < 0.70]
    if not lows:
        L.append("(tidak ada)")
    for r in lows:
        L.append(f"- **{r['id']}** ({r['category']}): g={r['groundedness']} "
                 f"— {r['question'][:70]}")
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def preflight_jev(jev_client) -> bool:
    """Satu panggilan score_chunk sebelum evaluasi dimulai.

    Fail-safe di produksi BOLEH menelan error API (-> abstain), tapi data
    evaluasi TIDAK BOLEH: bila API mati, seluruh kasus varian jev jadi
    score_error dan metrik menjadi sampah tanpa error yang terlihat.
    """
    try:
        s = jev_client.score_chunk("Does the Pro plan include API access?",
                                   "Pro plan: $49/mo, includes API access.")
        ok = 0.0 <= s["is_relevant"] <= 1.0
        print(f"preflight Jev: {'OK' if ok else 'nilai tidak wajar: ' + str(s)}")
        return ok
    except Exception as e:
        print(f"preflight Jev GAGAL: {type(e).__name__}: {e}")
        print("Perbaiki dulu (key/kuota TypeSafe) — evaluasi dibatalkan.")
        return False



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("variant", nargs="?", default="jev",
                    choices=["jev", "llm-judge"])
    ap.add_argument("--sample", type=int, default=0,
                    help="Ambil N kasus berlapis: tiap kategori & tiap "
                         "expected_decision terwakili (murah utk smoke test)")

    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Jumlah kasus yang dilewati sebelum evaluasi",
    )
    ap.add_argument(
        "--batch",
        action="store_true",
        help="Gabungkan hasil batch dengan hasil evaluasi sebelumnya",
    )
    ap.add_argument("--no-scorer", action="store_true")
    args = ap.parse_args()

    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    if args.sample:
        cases = stratified_sample(cases, args.sample)
    else:
        if args.offset < 0:
            ap.error("--offset tidak boleh negatif")

        if args.limit:
            cases = cases[args.offset:args.offset + args.limit]
        else:
            cases = cases[args.offset:]

    print("load embedding + DB...")
    llm = LLMClient(
        base_url=os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"),
        model=os.environ.get("LLM_MODEL", "gpt-4o-mini"),
    )
    store = VectorStore("postgresql://flowdesk:flowdesk@localhost:5432/flowdesk")
    retriever = Retriever(store, Embedder())

    jev_client = JevClient()      # dipakai graph (varian jev) DAN scorer
    if args.variant == "llm-judge":
        sys.path.insert(0, str(ROOT / "scripts"))
        from legacy_graph import build_legacy_graph, run_legacy
        graph, runner = build_legacy_graph(llm, retriever), run_legacy
    else:
        graph, runner = build_graph(llm, jev_client, retriever), run_workflow

    # B2: jangan evaluasi di atas API yang mati — insiden 403 (2026-10-11)
    # membuat seluruh run varian jev mem-abstain diam-diam (score_error)
    # dan menghasilkan decision_accuracy yang menyesatkan.
    if not preflight_jev(jev_client):
        sys.exit(1)

    # B1: scorer = penilai pihak ketiga, jalankan untuk KEDUA varian.
    use_scorer = not args.no_scorer

    print(f"menjalankan {len(cases)} kasus (varian: {args.variant}, "
          f"scorer: {use_scorer})...")

    from concurrent.futures import ThreadPoolExecutor, as_completed
    max_workers = int(os.environ.get("EVAL_WORKERS", "2"))
    print(f"eksekusi paralel ({max_workers} workers)...")
    rows = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futs = {pool.submit(run_case, graph, retriever, jev_client, c,
                            runner, use_scorer): c for c in cases}
        for fut in as_completed(futs):
            try:
                row = fut.result()
            except Exception as e:
                case = futs[fut]
                print(f"  {case['id']}: ERROR {type(e).__name__} — dilewati")
                continue
            mark = "" if row["match"] is None else ("  OK" if row["match"]
                                                    else "  <-- X")
            print(f"  {row['id']} [{row['category']}]: {row['decision']} "
                  f"({row['latency_s']}s){mark}")
            rows.append(row)
    rows.sort(key=lambda r: r["id"])    # urutan stabil utk report & diff
    # retrieval metrics — thread utama (psycopg conn tidak thread-safe;
    # tanpa biaya LLM: embedding lokal + query DB saja)
    for r in rows:
        case = next((c for c in cases if c["id"] == r["id"]), None)
        if case and case.get("expected_sources"):
            hits = retriever.retrieve(case["question"], k=5)
            got = {_norm(h["document"]) for h in hits}
            exp = {_norm(s) for s in case["expected_sources"]}
            found = got & exp
            r["hit@5"] = 1.0 if found else 0.0
            r["recall@5"] = len(found) / len(exp) if exp else 0.0



    # Lokasi hasil evaluasi
    eval_dir = ROOT / "evaluation"
    eval_dir.mkdir(parents=True, exist_ok=True)

    json_path = eval_dir / f"results-{args.variant}.json"
    report_path = eval_dir / f"report-{args.variant}.md"

    meta = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "generator": llm.model,
        "jev_model": os.environ.get("JEV_MODEL", "jev-latest"),
    }

    # Jika mode batch aktif, gabungkan dengan hasil sebelumnya.
    if args.batch and json_path.exists():
        previous = json.loads(json_path.read_text(encoding="utf-8"))

        # Pastikan hasil sebelumnya berasal dari varian yang sama.
        if previous.get("variant") != args.variant:
            ap.error("Varian hasil sebelumnya tidak cocok.")

        # Gunakan ID kasus sebagai kunci agar tidak ada duplikasi.
        merged = {
            row["id"]: row
            for row in previous.get("rows", [])
        }

        # Hasil baru memperbarui ID yang sama atau menambahkan ID baru.
        for row in rows:
            merged[row["id"]] = row

        rows = sorted(merged.values(), key=lambda row: row["id"])

        print(
            f"Menggabungkan hasil: {len(previous.get('rows', []))} "
            f"kasus sebelumnya + {len(rows)} kasus unik setelah penggabungan."
        )

    # Hitung ulang metrik dari seluruh kasus yang tersimpan.
    agg = aggregate(rows)
    cats = by_category(rows)

    # Simpan hasil gabungan.
    result = {
        "variant": args.variant,
        "meta": meta,
        "aggregate": agg,
        "per_category": cats,
        "rows": rows,
    }

    json_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    write_report(
        args.variant,
        meta,
        agg,
        cats,
        rows,
        report_path,
    )

    print(f"\nraw    -> {json_path.relative_to(ROOT)}")
    print(f"report -> {report_path.relative_to(ROOT)}")
    print(f"total kasus tersimpan: {len(rows)}")
    print(
        f"\nglobal: decision={agg['decision_accuracy']} "
        f"abstention={agg['abstention_accuracy']} "
        f"escalation={agg['escalation_accuracy']} "
        f"groundedness={agg['groundedness_mean']}"
    )

    print(f"\nglobal: decision={agg['decision_accuracy']} "
          f"abstention={agg['abstention_accuracy']} "
          f"escalation={agg['escalation_accuracy']} "
          f"groundedness={agg['groundedness_mean']}")


if __name__ == "__main__":
    main()
