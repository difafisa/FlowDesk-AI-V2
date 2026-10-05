"""Mini-benchmark Phase 3: 30 pertanyaan test set melalui run_pipeline.
Mengukur baseline RAG+LLM (SEBELUM Jev) — pembanding untuk Phase 4/5.
Jalankan dari root:  python scripts/run_rag_benchmark.py
Laporan -> benchmark/phase3-rag-baseline.txt
"""
import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dotenv import load_dotenv
load_dotenv()   # hapus jika tidak pakai python-dotenv

from flowdesk.embedding.embedder import Embedder
from flowdesk.rag.llm_client import LLMClient
from flowdesk.rag.output_validator import ABSTAIN_MARKER
from flowdesk.rag.pipeline import run_pipeline
from flowdesk.retrieval.retriever import Retriever
from flowdesk.storage.pgvector_store import VectorStore

TESTSET = os.path.join(os.path.dirname(__file__), "..", "src",
                       "flowdesk", "evaluation", "retrieval_testset.json")


def main():
    cases = json.loads(open(TESTSET, encoding="utf-8").read())
    print(f"load model + DB... ({len(cases)} test cases)")

    llm = LLMClient(
        base_url=os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"),
        model=os.environ.get("LLM_MODEL", "gpt-4o-mini"),
    )
    store = VectorStore("postgresql://flowdesk:flowdesk@localhost:5432/flowdesk")
    retriever = Retriever(store, Embedder())

    # resume: muat hasil parsial jika ada (benchmark crash-safe)
    out_path = os.path.join(os.path.dirname(__file__), "..", "benchmark",
                            "phase3-rag-baseline.txt")
    done: dict[str, dict] = {}
    if os.path.exists(out_path):
        for line in open(out_path, encoding="utf-8"):
            if line.startswith("RESULT\t"):
                parts = line.rstrip("\n").split("\t")
                done[parts[1]] = parts   # key = id kasus

    rows = []
    for c in cases:
        if c["id"] in done:                      # sudah selesai sebelumnya -> skip
            parts = done[c["id"]]
            print(f"{c['id']} [cached]")
            rows.append({"id": parts[1], "lang": parts[2], "status": parts[3],
                         "sec": float(parts[4]), "n_sources": int(parts[5]),
                         "n_cited": int(parts[6]), "answer": parts[7]})
            continue
        t0 = time.monotonic()
        r = run_pipeline(llm, retriever, c["question"])
        dt = time.monotonic() - t0
        time.sleep(13)   # free tier: ~5 req/menit
        cited = sum(1 for i in range(1, 10) if f"[{i}]" in r.answer)
        print(f"{c['id']} [{r.status}] {dt:.1f}s cited={cited}")
        # append hasil seketika -> crash berikutnya tidak kehilangan apa pun
        with open(out_path, "a", encoding="utf-8") as f:
            f.write("RESULT\t" + "\t".join([
                c["id"], c["lang"], r.status, f"{dt:.1f}", str(len(r.sources)),
                str(cited), r.answer.replace("\n", " ")[:110]]) + "\n")
        rows.append({"id": c["id"], "lang": c["lang"], "status": r.status,
                     "sec": round(dt, 1), "n_sources": len(r.sources),
                     "n_cited": cited,
                     "answer": r.answer.replace("\n", " ")[:110]})


    # ---- ringkasan agregat ----
    n = len(rows)
    by_status = {}
    for r in rows:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    answered = [r for r in rows if r["status"] == "answered"]
    with_cit = [r for r in answered if r["n_cited"] > 0]
    avg_lat = sum(r["sec"] for r in rows) / n
    avg_lat_ans = (sum(r["sec"] for r in answered) / len(answered)) if answered else 0

    lines = [
        f"Phase 3 RAG baseline (RAG+LLM, SEBELUM Jev) — {datetime.now():%Y-%m-%d %H:%M}",
        f"model LLM: {llm.model} | embedding: e5-base | top-K=5 | 30 test cases",
        "=" * 70,
        f"status     : {by_status}",
        f"answered dgn citation : {len(with_cit)}/{len(answered)} "
        f"({(len(with_cit)/len(answered)*100 if answered else 0):.0f}% dari answered)",
        f"latensi rata2 (semua) : {avg_lat:.1f}s",
        f"latensi rata2 (answered, termasuk LLM): {avg_lat_ans:.1f}s",
        "=" * 70,
    ]
    lines += [f"{r['id']:8s} [{r['status']:18s}] {r['sec']:5.1f}s "
              f"src={r['n_sources']} cited={r['n_cited']}  {r['answer']}"
              for r in rows]

    report = "\n".join(lines)
    print("\n" + "\n".join(lines[:8]))
    out = os.path.join(os.path.dirname(__file__), "..", "benchmark",
                       "phase3-rag-baseline.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print(f"laporan lengkap -> {os.path.abspath(out)}")


if __name__ == "__main__":
    main()
