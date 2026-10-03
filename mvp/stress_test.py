"""
Stress test module for the Lease Review Assistant.
Runs multiple leases in parallel, measures throughput, counts threads,
and reports performance metrics.

Addresses feedback: "Can it handle a real due diligence pack of 20-30 leases?"
"""

import time
import threading
import concurrent.futures
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

from pypdf import PdfReader
from extractor import process_lease
from validator import validate_extraction
from portugal_law import get_cost_eur


@dataclass
class StressTestResult:
    filename: str
    success: bool
    duration_seconds: float
    thread_id: int
    error: Optional[str] = None
    total_flagged: int = 0
    high_risk: int = 0
    validation_passed: Optional[bool] = None
    cost_eur: float = 0.0


@dataclass
class StressTestReport:
    total_leases: int
    successful: int
    failed: int
    total_duration_seconds: float
    avg_duration_seconds: float
    min_duration_seconds: float
    max_duration_seconds: float
    max_threads_used: int
    total_cost_eur: float
    results: List[StressTestResult] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"Stress Test Report\n"
            f"{'='*40}\n"
            f"Total leases:     {self.total_leases}\n"
            f"Successful:       {self.successful}\n"
            f"Failed:           {self.failed}\n"
            f"Total time:       {self.total_duration_seconds:.1f}s\n"
            f"Avg per lease:    {self.avg_duration_seconds:.1f}s\n"
            f"Min / Max:        {self.min_duration_seconds:.1f}s / {self.max_duration_seconds:.1f}s\n"
            f"Max threads:      {self.max_threads_used}\n"
            f"Total cost:       €{self.total_cost_eur:.4f}\n"
        )


def _process_single_lease(args: tuple) -> StressTestResult:
    """Worker function for parallel execution."""
    pdf_path, index, run_validation = args
    thread_id = threading.get_ident()
    start = time.time()

    try:
        # read PDF
        reader = PdfReader(str(pdf_path))
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"

        if len(text.strip()) < 50:
            raise ValueError("PDF appears to be empty or unreadable")

        # extract
        result = process_lease(text, filename=pdf_path.name)
        summary = result.get("summary", {})
        cost = result.get("meta", {}).get("total_cost_eur", 0)

        # validate with Claude if requested
        validation_passed = None
        if run_validation:
            validation = validate_extraction(text, result)
            validation_passed = validation.get("validation_passed")
            cost += validation.get("cost_eur", 0)

        duration = time.time() - start

        return StressTestResult(
            filename=pdf_path.name,
            success=True,
            duration_seconds=round(duration, 2),
            thread_id=thread_id,
            total_flagged=summary.get("total_flagged_clauses", 0),
            high_risk=summary.get("high_risk_clauses", 0),
            validation_passed=validation_passed,
            cost_eur=round(cost, 4),
        )

    except Exception as e:
        duration = time.time() - start
        return StressTestResult(
            filename=pdf_path.name,
            success=False,
            duration_seconds=round(duration, 2),
            thread_id=thread_id,
            error=str(e),
        )


def run_stress_test(
    pdf_paths: List[Path],
    max_workers: int = 4,
    run_validation: bool = False,
) -> StressTestReport:
    """
    Run all leases in parallel using a thread pool.

    max_workers: number of parallel threads (API rate limits suggest 3-5)
    run_validation: whether to also run Claude validation on each lease

    Why ThreadPoolExecutor and not ProcessPoolExecutor:
    Our workload is I/O-bound (waiting for API responses), not CPU-bound.
    Threads are more efficient for I/O-bound tasks in Python and share
    memory space, making result collection simpler.
    """
    args = [(p, i, run_validation) for i, p in enumerate(pdf_paths)]
    results = []
    thread_ids = set()
    start_total = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_process_single_lease, a): a for a in args}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            thread_ids.add(result.thread_id)

    total_duration = time.time() - start_total
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    durations = [r.duration_seconds for r in successful] or [0]

    return StressTestReport(
        total_leases=len(pdf_paths),
        successful=len(successful),
        failed=len(failed),
        total_duration_seconds=round(total_duration, 2),
        avg_duration_seconds=round(sum(durations) / len(durations), 2),
        min_duration_seconds=round(min(durations), 2),
        max_duration_seconds=round(max(durations), 2),
        max_threads_used=len(thread_ids),
        total_cost_eur=round(sum(r.cost_eur for r in results), 4),
        results=results,
    )


def run_determinism_test(
    pdf_path: Path,
    runs: int = 3,
) -> dict:
    """
    Run the same lease through the pipeline N times and compare outputs.
    Verifies that temperature=0 produces deterministic results.
    Temperature is set to 0 in extractor.py so the model always produces
    the same output for the same input.
    """
    reader = PdfReader(str(pdf_path))
    text = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"

    results = []
    for i in range(runs):
        result = process_lease(text, filename=pdf_path.name)
        results.append(result.get("extracted_fields", {}))

    # compare all runs to the first
    reference = results[0]
    mismatches = []
    for run_idx, run_result in enumerate(results[1:], start=2):
        for field, value in reference.items():
            if run_result.get(field) != value:
                mismatches.append({
                    "run": run_idx,
                    "field": field,
                    "run_1_value": value,
                    "this_run_value": run_result.get(field),
                })

    return {
        "filename": pdf_path.name,
        "runs": runs,
        "deterministic": len(mismatches) == 0,
        "mismatches": mismatches,
        "summary": (
            f"All {runs} runs produced identical output."
            if not mismatches else
            f"{len(mismatches)} field(s) differed across runs."
        ),
    }
