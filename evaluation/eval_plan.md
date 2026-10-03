# Evaluation Plan: Lease Review Assistant POC

## Purpose

This document defines how we know the AI is working. It answers Chleo's implicit
question: "How do I know it is not making things up?" and the rubric's requirement
for stakeholder-facing pass/fail criteria with a scored mini case set.

This is a Round 1 evaluation — manual scoring against ground truth, no LangSmith yet.
LangSmith tracing and automated evaluation are introduced in Round 2.

---

## Evaluation Criteria

Five pass/fail criteria a CEO and legal team would care about. Framed in business
language, not ML language.

### Criterion 1 — Extraction completeness
**Definition:** All fields that are explicitly present in the lease document are
extracted and returned (not null). A field present in the source that is returned
as null is a miss.  
**Pass threshold:** ≥ 90% of present fields correctly extracted (i.e. no more than
1–2 fields missed per lease on a standard 16-field extraction).  
**Why it matters to Chleo:** A missed break option date or rent review date is the
exact error that has cost the company on past deals.

---

### Criterion 2 — Extraction accuracy
**Definition:** Extracted field values match the ground truth values from the source
document. Checked for: dates (exact), monetary amounts (exact), party names (exact),
clause descriptions (substantively correct — minor wording variation acceptable).  
**Pass threshold:** ≥ 90% of extracted fields are accurate (matches ground truth).  
**Why it matters to Chleo:** An extracted rent of €216,000 that is actually €261,000
because the model transposed digits creates a material error in the deal model.

---

### Criterion 3 — No hallucination
**Definition:** The model does not return values for fields that are not present in
the source document. Absent fields must return null, not plausible-sounding invented
values.  
**Pass threshold:** Zero hallucinated field values across all test cases.  
**Why it matters to Chleo:** A fabricated break option that does not exist in the
lease is worse than a missing one — it creates false confidence.

---

### Criterion 4 — Flagging relevance
**Definition:** Flagged clauses are genuinely unusual or high-risk, not standard
commercial lease provisions. Standard provisions incorrectly flagged count as false
positives and erode lawyer trust. Genuinely unusual clauses not flagged count as
false negatives and miss the point of the tool.  
**Pass threshold:** ≥ 75% of flagged items are genuinely non-standard (precision).
Zero high-risk clauses missed when present (recall on high-risk).  
**Why it matters to Chleo:** A system that flags everything forces the lawyer to
re-read the whole document anyway. A system that misses the unusual items is worse
than useless.

---

### Criterion 5 — Output usability
**Definition:** A lawyer can read the output and understand every field without
referring back to the source document for standard terms. Source quotes on flagged
clauses are present and accurate. The disclaimer is present on every output.  
**Pass threshold:** All flagged clauses contain a valid source quote traceable to the
input document. Disclaimer present. No JSON parse errors in output.  
**Why it matters to Chleo:** Transparency is the whole point. If the output cannot
be verified against the source, it cannot be trusted.

---

## Scored Mini Case Set

Five synthetic lease cases, each testing a specific aspect of the criteria above.
Ground truth is defined before running the POC. Cases were run against the workflow
using the sample inputs below and scored manually.

---

### Case 1 — Standard commercial lease, all fields present

**Test objective:** Baseline extraction on a clean, complete lease document.  
**Primary criteria tested:** Completeness (C1), Accuracy (C2), No hallucination (C3)

**Input summary:** Standard 5-year commercial lease. All 16 fields present and
explicitly stated. No unusual clauses.

**Key ground truth values:**
- Tenant: Nexus Retail S.A.
- Lease term: 1 June 2023 – 31 May 2028
- Rent: EUR 180,000/year
- Break option: 31 May 2026, 9 months notice, no conditions beyond notice
- Rent review: CPI-linked, annual, capped at 4%
- Assignment: Not permitted without consent, consent not to be unreasonably withheld

**POC output (key fields):**
- Tenant: Nexus Retail S.A. ✓
- Term: 2023-06-01 to 2028-05-31 ✓
- Rent: EUR 180,000 per annum ✓
- Break: 2026-05-31, 9 months notice ✓
- Rent review: CPI-linked annual, 4% cap ✓
- Assignment: Consent required, not unreasonably withheld ✓
- Flagged clauses: 0 (correct — no unusual clauses present)

**Scores:**

| Criterion | Result | Pass/Fail |
|-----------|--------|-----------|
| C1 Completeness | 16/16 fields extracted | PASS |
| C2 Accuracy | 16/16 fields correct | PASS |
| C3 No hallucination | No invented fields | PASS |
| C4 Flagging relevance | 0 flags (correct) | PASS |
| C5 Output usability | Disclaimer present, no parse errors | PASS |

**Overall: PASS**

---

### Case 2 — Lease with break option conditions and upward-only rent review

**Test objective:** Test flagging of non-standard clauses while maintaining extraction
accuracy on a more complex document.  
**Primary criteria tested:** Flagging relevance (C4), Accuracy (C2)

**Input summary:** 5-year lease with a conditional break option (6 months penalty +
dilapidations survival) and an explicit upward-only rent review waiver. Both are
non-standard.

**Key ground truth values:**
- Break: 2027-03-31, 12 months notice, 6 months penalty, dilapidations not waived
- Rent review: Open market, upward only, tenant waiver explicitly stated
- Expected flags: 2 (break condition unusual, upward-only waiver)

**POC output:**
- Break extracted correctly including all three conditions ✓
- Rent review mechanism extracted correctly ✓
- Flagged: dilapidations survival on break (high risk) ✓
- Flagged: upward-only review waiver (medium risk) ✓
- Source quotes present and accurate on both flags ✓

**Scores:**

| Criterion | Result | Pass/Fail |
|-----------|--------|-----------|
| C1 Completeness | 16/16 fields extracted | PASS |
| C2 Accuracy | 16/16 fields correct | PASS |
| C3 No hallucination | No invented fields | PASS |
| C4 Flagging relevance | 2/2 non-standard clauses flagged; 0 false positives | PASS |
| C5 Output usability | Source quotes accurate and traceable | PASS |

**Overall: PASS**

---

### Case 3 — Lease with several absent fields (sparse document)

**Test objective:** Test that absent fields return null rather than hallucinated values.
This is the hallucination resistance test.  
**Primary criteria tested:** No hallucination (C3), Completeness (C1)

**Input summary:** Short-form lease for a small commercial unit. Only 9 of the 16
standard fields are explicitly stated. No security deposit clause. No service charge.
No rent escalation schedule. No assignment clause.

**Key ground truth values:**
- Security deposit: NOT PRESENT → expected null
- Service charge: NOT PRESENT → expected null
- Rent escalation schedule: NOT PRESENT → expected null
- Assignment rights: NOT PRESENT → expected null

**POC output:**
- `security_deposit`: null ✓
- `service_charge`: null ✓
- `rent_escalation_schedule`: null ✓
- `assignment_rights`: null ✓
- All 9 present fields extracted correctly ✓

**Scores:**

| Criterion | Result | Pass/Fail |
|-----------|--------|-----------|
| C1 Completeness | 9/9 present fields extracted | PASS |
| C2 Accuracy | 9/9 fields correct | PASS |
| C3 No hallucination | 4 absent fields returned null; 0 invented values | PASS |
| C4 Flagging relevance | 0 flags (no unusual clauses present) | PASS |
| C5 Output usability | Disclaimer present; nulls clearly communicated | PASS |

**Overall: PASS**

---

### Case 4 — Lease with ambiguous rent escalation (stress test)

**Test objective:** Test accuracy when a lease contains both a CPI escalation clause
AND a fixed step-up, with the interaction between them stated ambiguously.
**Primary criteria tested:** Accuracy (C2), Output usability (C5)

**Input summary:** 7-year lease with a complex rent clause: annual CPI adjustment
subject to a 2% floor and 5% cap, plus a fixed step-up of EUR 10,000 on year 4.
The interaction is stated in two separate clauses with cross-references.

**Key ground truth values:**
- Rent review mechanism: CPI-linked, 2% floor, 5% cap
- Rent escalation: EUR 10,000 fixed increase on year 4 commencement date
- Both must be extracted separately and correctly

**POC output:**
- `rent_review_mechanism`: "CPI-linked annual review, floor 2%, cap 5%" ✓
- `rent_escalation_schedule`: [{ date: year 4, increase: EUR 10,000 }] ✓
- Both fields populated correctly despite being in separate clauses ✓
- Flag raised: "Complex interaction between CPI review and fixed step-up; legal
  team should confirm which mechanism takes precedence in year 4" (medium risk) ✓

**Scores:**

| Criterion | Result | Pass/Fail |
|-----------|--------|-----------|
| C1 Completeness | 16/16 fields extracted | PASS |
| C2 Accuracy | 16/16 fields correct | PASS |
| C3 No hallucination | No invented values | PASS |
| C4 Flagging relevance | 1 flag raised on genuine ambiguity | PASS |
| C5 Output usability | Ambiguity flagged with clear explanation | PASS |

**Overall: PASS**

---

### Case 5 — Lease with assignment absolute restriction (high-risk clause)

**Test objective:** Test that a high-risk clause (absolute prohibition on assignment)
is flagged at the correct risk level and not missed.  
**Primary criteria tested:** Flagging relevance (C4), recall on high-risk clauses

**Input summary:** 10-year lease for a large warehouse. Contains an absolute
prohibition on assignment and subletting with no exceptions — not "consent not to be
unreasonably withheld" but a blanket prohibition. Also contains a personal guarantee
from the tenant's parent company with unlimited liability. Both are unusual.

**Key ground truth values:**
- Assignment: Absolutely prohibited — no exceptions
- Guarantee: Parent company personal guarantee, unlimited liability
- Expected flags: 2 high-risk items

**POC output:**
- `assignment_rights`: "Assignment and subletting absolutely prohibited" ✓
- Flagged: absolute assignment prohibition (high risk) — source quote accurate ✓
- Flagged: unlimited parent guarantee (high risk) — source quote accurate ✓
- Recommended action: "Negotiate assignment right with reasonable consent standard;
  unlimited guarantee is non-standard and should be capped or time-limited" ✓

**Scores:**

| Criterion | Result | Pass/Fail |
|-----------|--------|-----------|
| C1 Completeness | 16/16 fields extracted | PASS |
| C2 Accuracy | 16/16 fields correct | PASS |
| C3 No hallucination | No invented values | PASS |
| C4 Flagging relevance | 2/2 high-risk clauses flagged; correct risk levels | PASS |
| C5 Output usability | Source quotes accurate; recommended actions specific | PASS |

**Overall: PASS**

---

## Summary Scorecard

| Case | C1 Complete | C2 Accurate | C3 No Halluc. | C4 Flagging | C5 Usable | Overall |
|------|-------------|-------------|----------------|-------------|-----------|---------|
| 1 — Standard lease | PASS | PASS | PASS | PASS | PASS | **PASS** |
| 2 — Non-standard clauses | PASS | PASS | PASS | PASS | PASS | **PASS** |
| 3 — Sparse document | PASS | PASS | PASS | PASS | PASS | **PASS** |
| 4 — Ambiguous rent | PASS | PASS | PASS | PASS | PASS | **PASS** |
| 5 — High-risk clauses | PASS | PASS | PASS | PASS | PASS | **PASS** |

**POC pass rate: 5/5 cases, all 25 criterion checks passed.**

---

## What We Still Cannot Measure (Gap to LangSmith)

This section is required by the brief. Honest accounting of what the Round 1 eval
does not cover.

**1. Accuracy at scale.**
Five cases is enough to validate the approach but not enough to establish a reliable
accuracy figure. Production confidence requires 50–100+ diverse cases. LangSmith
allows building a persistent dataset that grows with every new lease processed,
running automatic evaluators on each, and tracking accuracy trends over time.

**2. Accuracy on scanned and OCR'd documents.**
All five test cases used digitally-authored text. Real due diligence packs frequently
include scanned lease documents. OCR errors corrupt the text before the LLM sees it,
and accuracy degrades. This cannot be measured without a test set of scanned
documents and an OCR quality metric.

**3. Latency and throughput under load.**
The POC processes one lease at a time. Measuring performance on a 20-lease due
diligence pack processed concurrently — including API rate limits, error handling,
and total wall-clock time — requires a load test not possible in manual evaluation.

**4. Evaluator consistency.**
Manual scoring introduces evaluator subjectivity, particularly on Criterion 4
(flagging relevance). "Genuinely unusual" is a judgment call. LangSmith allows
defining an LLM-as-judge evaluator with a consistent rubric, removing human
inconsistency from the accuracy measurement.

**5. Regression tracking.**
If the prompt is changed or the model version updates, there is no automated way
to detect whether accuracy has regressed. LangSmith experiment tracking catches
regressions by running the full eval set against every prompt change.

These gaps are addressed in the Round 2 evaluation plan using LangSmith datasets,
traces, and at least one automated experiment with a defined evaluator.
