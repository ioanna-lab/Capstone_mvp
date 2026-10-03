# Use Case Definition — AI Lease & Due Diligence Review Assistant
**Capstone Round 2 · Ironhack AI Consulting · Ioanna Renta**
**Date:** October 2026

---

## 1. Business Problem Statement

Commercial real estate developers in Southern Europe spend between 4 and 8 hours
manually abstracting each commercial lease before an acquisition can proceed. A
typical due diligence pack contains 10 to 30 leases. At 8 to 12 acquisitions per
year, this creates an annual cost of €128,000 to €192,000 in paralegal and lawyer
time — before accounting for deal delays, missed clause errors, and the risk of
proceeding without complete information.

The specific problem this system addresses is: **how do you extract structured,
legally accurate data from commercial lease documents quickly enough to accelerate
deal cycles, without introducing new risk through AI hallucination or opacity?**

Two past acquisitions by the target company (represented as "Chleo's company" in
this project) had material clause errors that were only discovered after signing.
Both involved missed break option conditions and misread rent step-up schedules —
exactly the fields where manual abstraction is most error-prone.

---

## 2. Company Profile

| Attribute | Detail |
|---|---|
| Industry | Commercial real estate — acquisition and development |
| Geography | Southern Europe, primary focus Portugal |
| Size | Mid-market, 200–1,000 staff |
| Annual deal volume | 8–12 commercial property acquisitions per year |
| Lease complexity | 10–30 leases per acquisition, mix of office, retail, warehouse |
| Current state | Fully manual lease abstraction, 4–8 hours per lease |
| Legal framework | Portuguese NRAU (Lei n.º 6/2006), Código Civil |
| Pain points | Deal cycle length, abstraction cost, clause error risk |

---

## 3. Proposed AI Solution and System Type

**System type:** AI-assisted document extraction and risk flagging with mandatory
human review. This is a human-in-the-loop system — the AI produces a structured
draft, a qualified lawyer reviews and signs off, and only the approved output
enters any financial or legal decision.

**What the system does:**

1. Accepts a commercial lease PDF as input
2. Extracts 16 standard fields (parties, dates, rent, break options, obligations)
   and 11 Portugal-specific fields (NIF numbers, Finanças registration, stamp duty,
   notice periods) using GPT-4o with Portuguese law context injected
3. Flags unusual or non-standard clauses against Portuguese legal standards (NRAU,
   Código Civil) with exact source citations (page number and clause reference)
4. Validates the extraction using Claude Haiku as a second model — disagreements
   are surfaced to the reviewer
5. Presents results in a structured Streamlit UI with a mandatory lawyer sign-off
   workflow
6. Persists all results to Supabase (PostgreSQL), syncs to Notion, and emails the
   reviewer
7. For a full portfolio, generates an acquisition proposal (BUY/REVIEW/PASS) with
   Portuguese tax calculations (IMT 6.5%, stamp duty 0.8%)

**Models used:**
- GPT-4o / gpt-4o-2024-11-20 (extraction and flagging)
- o1, o3, o3-mini (available for complex clause extraction)
- Claude Haiku (cross-model validation)
- text-embedding-3-small (RAG corpus embeddings)

---

## 4. Key Stakeholders and Interests

| Stakeholder | Interest | Concern |
|---|---|---|
| CEO (Chleo) | Faster deal cycles, cost reduction | AI transparency, hallucination risk |
| Legal team (lawyers) | Time savings on abstraction | Trust in AI output, liability |
| Investment committee | Accurate financial data | Clause errors affecting valuations |
| External counsel | Reduced repetitive work | Being replaced vs. augmented |
| IT / compliance | Data security, EU AI Act | Third-party data processing |
| Regulators (AT/Finanças) | Correct lease registration | AI-generated errors in legal filings |

---

## 5. Success Criteria

**SC1 — Time reduction (measurable):**
Due diligence cycle per acquisition reduces from 13 working days to 5 or fewer.
Lawyer review time per lease reduces from 4–8 hours to under 1 hour.
Target: ≥70% reduction in abstraction time, verified by time-tracking in pilot.

**SC2 — Extraction accuracy (measurable):**
Field extraction accuracy ≥90% on standard clauses, ≥80% on complex clauses,
measured against ground truth from 200 synthetic leases (ground_truth.csv) and
validated against real leases in the pilot.

**SC3 — Lawyer adoption:**
Legal team uses the system on ≥80% of leases in the pilot without re-doing
abstraction manually from scratch.

**SC4 — Zero undetected critical errors:**
No material clause errors (break options, rent figures, assignment restrictions)
pass through the system without being flagged or corrected in the sign-off step.

---

## 6. Out-of-Scope Boundaries

- The system does not produce legal advice or legal opinions
- The system does not make acquisition decisions autonomously
- The system does not process scanned/OCR-only documents in Round 2 (text-layer
  PDFs only)
- The system does not integrate with financial modelling tools in Round 2
- The system does not cover residential leases (commercial only)
- The system does not cover jurisdictions outside Portugal in Round 2

---

## 7. Evolution from Round 1

**Round 1** established the use case (lease review), built a working n8n POC,
defined the 5-criteria evaluation plan, created 6 charts, and presented to
teaching staff.

**Feedback received from teaching staff and colleagues:**
- Accuracy results unconvincing on small synthetic dataset — need 20–50+ real leases
- Biggest risk: hallucination on break options, rent terms, unusual clauses
- Prioritise: larger test set, field-level accuracy validation, lawyer trust
- Source citations must include page number and clause reference
- Add a feedback loop so the system learns from lawyer corrections

**What changed for Round 2:**
- Use case unchanged (lease review, Portuguese market)
- Geography explicitly localised to Portugal (NRAU, NIF, Finanças registration)
- Test corpus expanded from 5 synthetic leases to 200 Portuguese synthetic leases
  with ground truth CSV
- Source citations added (page number and clause reference on every field)
- Cross-model validation added (Claude Haiku validates GPT-4o output)
- Feedback loop added (lawyer corrections stored in Supabase, fed back as few-shot
  examples into future extraction prompts)
- Full Streamlit MVP built with 5 tabs, Supabase persistence, Notion sync, email
- Acquisition proposal generator added with Portuguese tax calculations
- Stress test with parallel threads added to demonstrate scale
- Portuguese law corpus loaded into Chroma RAG for grounded extraction
