"""
Terminal stress test — runs 10 leases in parallel from disk.
Bypasses the 5-file UI upload limit for a proper scale test.

Usage:
    cd mvp
    python3 run_stress_test.py --leases 10 --threads 4
"""

import os
import sys
import time
import json
import random
import argparse
import threading
import concurrent.futures
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from pypdf import PdfReader
from extractor import process_lease


def load_lease_text(pdf_path: Path) -> str:
    """Extract text from a PDF file."""
    reader = PdfReader(str(pdf_path))
    text = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    return text.strip()


def process_one(args):
    """Worker function for parallel execution."""
    pdf_path, idx = args
    tid = threading.get_ident()
    start = time.time()
    try:
        text = load_lease_text(pdf_path)
        if len(text) < 100:
            raise ValueError("PDF appears empty or unreadable")
        result = process_lease(text, filename=pdf_path.name)
        duration = round(time.time() - start, 2)
        summary = result.get("summary", {})
        return {
            "idx": idx,
            "filename": pdf_path.name,
            "success": True,
            "duration_s": duration,
            "thread_id": tid,
            "total_flagged": summary.get("total_flagged_clauses", 0),
            "high_risk": summary.get("high_risk_clauses", 0),
            "recommendation": summary.get("review_recommendation", ""),
            "error": None,
        }
    except Exception as e:
        return {
            "idx": idx,
            "filename": pdf_path.name,
            "success": False,
            "duration_s": round(time.time() - start, 2),
            "thread_id": tid,
            "total_flagged": 0,
            "high_risk": 0,
            "recommendation": "",
            "error": str(e)[:100],
        }


def run(n_leases: int = 10, n_threads: int = 4):
    # find synthetic leases
    corpus_dir = Path("data/leases/synthetic")
    if not corpus_dir.exists():
        print("ERROR: data/leases/synthetic/ not found. Run generate_corpus.py first.")
        sys.exit(1)

    all_pdfs = sorted(corpus_dir.glob("PT_*.pdf"))
    if len(all_pdfs) < n_leases:
        print(f"Only {len(all_pdfs)} PDFs found, using all of them.")
        n_leases = len(all_pdfs)

    # pick a diverse sample
    selected = random.sample(all_pdfs, n_leases)

    print(f"\n{'='*60}")
    print(f"LEASE REVIEW ASSISTANT — STRESS TEST")
    print(f"{'='*60}")
    print(f"Leases:  {n_leases}")
    print(f"Threads: {n_threads}")
    print(f"Est. cost: €{n_leases * 0.025:.3f}")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}\n")

    args_list = [(pdf, i) for i, pdf in enumerate(selected)]
    results = []
    start_total = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
        futures = {executor.submit(process_one, a): a for a in args_list}
        for future in concurrent.futures.as_completed(futures):
            r = future.result()
            results.append(r)
            status = "✅" if r["success"] else "❌"
            print(
                f"{status} [{r['idx']+1}/{n_leases}] {r['filename'][:40]:<40} "
                f"{r['duration_s']:5.1f}s  "
                f"flags:{r['total_flagged']}  high:{r['high_risk']}"
            )

    total_time = round(time.time() - start_total, 2)
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    unique_threads = len({r["thread_id"] for r in results})
    durations = [r["duration_s"] for r in successful] or [0]
    sequential_time = sum(durations)
    speedup = round(sequential_time / total_time, 2) if total_time > 0 else 1

    print(f"\n{'='*60}")
    print(f"RESULTS")
    print(f"{'='*60}")
    print(f"Completed:        {len(successful)}/{n_leases}")
    print(f"Failed:           {len(failed)}")
    print(f"Total time:       {total_time}s")
    print(f"Sequential would: {sequential_time:.1f}s")
    print(f"Speedup:          {speedup}x")
    print(f"Avg per lease:    {sum(durations)/len(durations):.1f}s")
    print(f"Min / Max:        {min(durations):.1f}s / {max(durations):.1f}s")
    print(f"Threads used:     {unique_threads}")
    print(f"Est. cost:        €{len(successful)*0.025:.3f}")
    print(f"{'='*60}\n")

    if failed:
        print("FAILED:")
        for r in failed:
            print(f"  {r['filename']}: {r['error']}")

    # save results
    out_path = Path("results") / f"stress_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({
            "config": {"n_leases": n_leases, "n_threads": n_threads},
            "summary": {
                "completed": len(successful),
                "failed": len(failed),
                "total_time_s": total_time,
                "sequential_time_s": sequential_time,
                "speedup": speedup,
                "avg_duration_s": round(sum(durations)/len(durations), 2),
                "threads_used": unique_threads,
                "est_cost_eur": round(len(successful)*0.025, 3),
            },
            "results": results,
        }, f, indent=2)
    print(f"Results saved to: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stress test the lease extraction pipeline")
    parser.add_argument("--leases", type=int, default=10, help="Number of leases to process")
    parser.add_argument("--threads", type=int, default=4, help="Number of parallel threads")
    args = parser.parse_args()
    run(args.leases, args.threads)
