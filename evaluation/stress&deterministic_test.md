# Stress Test & Determinism Documentation
**AI Lease & Due Diligence Review Assistant — Portugal**
**Capstone Round 2 · Ironhack AI Consulting · Ioanna Renta**

---

## Why Stress Testing Matters

The feedback from Round 1 presentation was clear: "performance across 20, 30 or
50 real documents remains untested." A system that works on one lease at a time
is not production-ready. A real due diligence pack contains 10-30 leases and the
legal team needs them all processed before a deal closes.

Stress testing answers two questions:

1. Can the system process multiple leases simultaneously without errors?
2. Does it produce the same output for the same input every time (determinism)?

---

## Two Ways to Run the Stress Test

### Option A -- Via the Streamlit UI (up to 5 leases)

1. Upload up to 5 lease PDFs in the sidebar
2. Go to the **Stress Test** tab
3. Set the parallel threads slider (1-5)
4. Click **Run stress test**
5. Results appear as a table showing filename, success, duration, flags, and errors

**Limitation:** The UI caps uploads at 5 files. Use Option B for larger tests.

### Option B -- Via the terminal (10+ leases, no upload limit)

This runs leases directly from disk, bypassing the UI upload limit entirely.

```bash
cd mvp
python3 run_stress_test.py --leases 10 --threads 4
```

**Parameters:**
- `--leases N` -- number of leases to process (default: 10, max: 200)
- `--threads N` -- number of parallel threads (default: 4, recommended: 3-5)

**Requirements:** The synthetic corpus must exist at `data/leases/synthetic/`.
If it does not, run `python3 generate_corpus.py` first.

**Example output:**
```
============================================================
LEASE REVIEW ASSISTANT — STRESS TEST
============================================================
Leases:  10
Threads: 4
Est. cost: €0.250
Started: 14:23:05
============================================================

✅ [1/10] PT_0001_office_Porto.pdf              21.3s  flags:0  high:0
✅ [2/10] PT_0076_break_option_Lisboa.pdf       23.1s  flags:3  high:2
✅ [3/10] PT_0186_compliance_issue_Porto.pdf    22.8s  flags:2  high:2
✅ [4/10] PT_0031_retail_Lisboa.pdf             45.2s  flags:1  high:0
...

============================================================
RESULTS
============================================================
Completed:        10/10
Failed:           0
Total time:       67.4s
Sequential would: 287.3s
Speedup:          4.3x
Avg per lease:    28.7s
Min / Max:        21.3s / 72.1s
Threads used:     4
Est. cost:        €0.250
============================================================
```

**Results are saved automatically** to `results/stress_test_YYYYMMDD_HHMMSS.json`.

---

## How Parallelisation Works

The stress test uses Python's `ThreadPoolExecutor`. Each thread processes one
lease independently and simultaneously. The number of threads controls how many
leases run at the same time.

**Why threads, not processes:**
Our workload is I/O-bound -- most of the time is spent waiting for API responses
from OpenAI and Anthropic, not doing computation. Python threads are more efficient
for I/O-bound tasks and share memory, making result collection simpler.

**Speedup calculation:**
If 10 leases each take 30 seconds sequentially = 300 seconds total.
With 4 threads running simultaneously = roughly 75-90 seconds total.
Speedup = 300 / 75 = 4x.

The actual speedup depends on API response time variability -- some leases have
complex clauses that take longer to process.

**Rate limit consideration:**
OpenAI's API has rate limits. With 4+ threads hitting the API simultaneously,
you may occasionally see rate limit errors. If this happens, reduce `--threads`
to 2 or 3. The results file records any errors for review.

---

## Determinism Check

### What It Tests

Temperature=0 is set on all models (GPT-4o and Claude Haiku). This means the
model always produces the same output for the same input -- no randomness. The
determinism check verifies this is actually working.

**Why this matters for legal work:** A system that gives different answers on
different runs cannot be trusted for due diligence. If the extraction of a break
option date changes between runs, the lawyer cannot rely on the output.

### Running the Determinism Check

**Via the UI:**
1. Go to the **Stress Test** tab
2. Scroll to the **Determinism check** section
3. Select any uploaded lease
4. Click **Run determinism check (3 runs)**

The system processes the same lease 3 times and compares every extracted field
across all 3 runs. Any differences are shown in a table.

**Expected result:**
```
✅ All 3 runs produced identical output.
   Determinism confirmed — temperature=0 is working correctly.
```

**Actual finding from capstone run:**
Structured fields (dates, rent amounts, NIF numbers, break option dates) are
fully deterministic across all 3 runs. Free-text narrative fields (obligation
lists, descriptions) show minor phrasing variation at the punctuation and synonym
level -- e.g. "Não permitido" vs "Proibido" (synonyms), trailing period present
or absent.

This is expected behaviour. Temperature=0 eliminates reasoning randomness but
slight tokenisation variations can produce minor surface-level differences in
long text outputs. For legal review purposes, all material values (dates, numbers,
parties, financial terms) are deterministic. Free-text fields are verified by the
lawyer during sign-off regardless.

**Via the terminal:**
```bash
cd mvp
python3 -c "
from pypdf import PdfReader
from extractor import process_lease

reader = PdfReader('data/leases/synthetic/PT_0001_office_Porto.pdf')
text = ''.join(p.extract_text() or '' for p in reader.pages)

results = [process_lease(text, filename='PT_0001').get('extracted_fields', {})
           for _ in range(3)]

ref = results[0]
mismatches = [
    {'field': k, 'run1': v, 'run2': results[1].get(k), 'run3': results[2].get(k)}
    for k, v in ref.items()
    if results[1].get(k) != v or results[2].get(k) != v
]
print('Mismatches:', len(mismatches))
if not mismatches:
    print('DETERMINISTIC: all 3 runs identical')
else:
    for m in mismatches:
        print(m)
"
```

---

## Results Interpretation

| Metric | What it means | Good value |
|---|---|---|
| Completed / total | Leases successfully processed | 100% |
| Speedup | Parallel vs sequential time ratio | ≥3x with 4 threads |
| Avg per lease | Mean processing time | 20-60s (depends on complexity) |
| Threads used | Actual parallel execution confirmed | = threads set |
| Est. cost | Total API cost for this run | €0.02-0.04 per lease |
| Determinism | Same output on repeated runs | All 3 runs identical |

---

## Stress Test Results (Capstone Run)

**UI test (4 leases, 3 threads):**
- 4/4 completed
- Total: 85.9s (sequential would be ~180s)
- Speedup: ~2.1x
- Threads used: 3
- Cost: €0.100
- All leases flagged high-risk clauses correctly

**Screenshot:** See `evaluation/stress_test_results.png`

---

## Notes for Production

In production with 30 leases per deal:

| Config | Estimated time | Estimated cost |
|---|---|---|
| 1 thread (sequential) | ~30 min | €0.75 |
| 3 threads | ~12 min | €0.75 |
| 5 threads | ~8 min | €0.75 |

Cost is the same regardless of thread count -- parallelisation reduces time, not
API usage. The cost per lease is fixed at ~€0.025.

Rate limit monitoring is built into the extractor -- errors are caught and
reported in the results table without crashing the whole run.
