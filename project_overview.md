# Project Overview — AI Lease & Due Diligence Review Assistant
**Ironhack AI Consulting Programme · Capstone Project**
**Student:** Ioanna Renta · October 2026

---

## The Problem

Commercial real estate developers in Southern Europe spend 4 to 8 hours manually
abstracting each lease before an acquisition can proceed. A typical due diligence
pack contains 10 to 30 leases. At 8 to 12 acquisitions per year, this costs
€128,000 to €192,000 annually in lawyer and paralegal time -- before accounting
for deal delays and the risk of clause errors.

Two past acquisitions by the target company had material clause errors discovered
only after signing. Both involved missed break option conditions and misread rent
step-up schedules -- the fields most prone to manual abstraction errors.

The client (referred to as "Chleo") had one central concern: "AI is not
transparent -- how do I know it is not making things up?" This concern shaped
every design decision in the system.

---

## The Solution

An AI-assisted lease review system that extracts structured data from commercial
lease PDFs, flags non-standard clauses, and presents the results to a qualified
lawyer for review and sign-off. The AI does not make decisions -- it produces a
draft that a lawyer verifies.

**Key design principles:**

1. **Human-in-the-loop is mandatory, not optional.** No output can be used in
   any legal or financial decision without a lawyer completing the sign-off
   workflow. This is also what keeps the system in the Limited Risk category
   under the EU AI Act.

2. **Every claim cites its source.** Every extracted field shows the page number
   and clause reference where it was found. The lawyer can verify any value in
   seconds rather than re-reading the whole document.

3. **Cross-model validation builds trust.** GPT-4o extracts the fields. Claude
   Haiku independently validates the extraction. Disagreements are surfaced to
   the lawyer. Two models, two perspectives, one validated output.

4. **Portugal-specific, not generic.** The system is grounded in Portuguese law:
   NRAU (Lei n.º 6/2006), NIF numbers, Finanças registration obligations, stamp
   duty rules, and specific notice period requirements. Generic SaaS tools do not
   have this localisation.

---

## What Was Built

### Round 1 -- Proof of Concept

A working n8n workflow demonstrating end-to-end lease extraction using
GPT-4o-mini. Tested on 5 synthetic leases, scored against 5 pass/fail criteria,
all 5 cases passed. Presented to teaching staff. Decision: proceed to Round 2
and deepen Portugal localisation.

**Round 1 deliverables:** sector research, 6 charts, n8n POC, eval plan, cost
and timeline analysis, 12-slide presentation, executive one-pager.

### Round 2 -- Full MVP

A complete standalone web application built in Python with Streamlit. The system
runs on Render without any local setup. Features:

**Core AI pipeline:**
- GPT-4o (or o1/o3/o3-mini/o1-pro) extracts 16 standard + 11 Portugal-specific
  fields with page and clause citations
- Claude Haiku independently validates the extraction and produces an agreement
  score
- Both models grounded in Portuguese law via NRAU legal context injected into
  every prompt
- Feedback loop: lawyer corrections stored in Supabase and fed back as few-shot
  examples into future extractions

**Application features (5 tabs):**
- Extract & Review: upload lease, run extraction, review fields and flags,
  correct errors, complete mandatory lawyer sign-off
- Query Portfolio: ask any question across all uploaded leases using RAG
- Acquisition Proposal: generate a BUY/REVIEW/PASS recommendation with
  Portuguese tax calculations (IMT 6.5%, stamp duty 0.8%)
- Review History: all past reviews, cost tracking, model usage
- Stress Test: parallel processing of multiple leases, determinism verification

**Infrastructure:**
- Supabase (PostgreSQL, EU-hosted): all reviews, evaluations, costs, proposals
- Notion: one page per review, portfolio database
- Gmail SMTP: email notification with JSON attachment
- LangSmith: tracing on every extraction and validation call
- Chroma: in-memory RAG vector store over uploaded leases
- Render: standalone hosting, no local server needed

**Test corpus:**
- 200 synthetic Portuguese commercial leases generated with known ground truth
- Distribution across 10 categories: standard office/retail/warehouse, break
  option issues, unusual rent review, assignment restrictions, missing fields,
  short-term, high-risk combinations, compliance issues
- Ground truth CSV with 31 fields per lease for LangSmith evaluation

---

## Evidence the System Works

**Extraction accuracy:** Fields extracted correctly from Portuguese synthetic
leases including tenant name, NIF numbers, rent amounts, break option dates,
Finanças registration clauses, and stamp duty attribution.

**Flagging accuracy:** High-risk clauses correctly identified including absolute
assignment prohibitions, dilapidations survival on break, stamp duty incorrectly
attributed to tenant, and notice periods below statutory minimum.

**Cross-model validation:** Claude Haiku agreement scores of 75-90% on clean
standard leases, lower on complex leases with ambiguous clauses -- which is the
correct behaviour for a validation layer.

**Stress test:** 4 leases processed in parallel on 3 threads in 85.9 seconds.
Sequential processing would take approximately 180 seconds. Speedup: 2.1x.
Cost: €0.025 per lease.

**Determinism:** Structured fields (dates, numbers, NIF) are fully deterministic
across 3 identical runs. Free-text fields show minor phrasing variation at
punctuation level -- all material values are stable.

**Acquisition proposal:** 4 warehouse leases aggregated into a REVIEW
recommendation with IMT (€552,500) and stamp duty (€68,000) correctly calculated
on an €8.5M asking price.

**LangSmith tracing:** Live traces visible in the `lease-review-mvp` project,
dataset created with examples from the synthetic corpus.

---

## Compliance Summary

**EU AI Act:** Limited Risk. The system produces drafts for human review -- it
does not make autonomous decisions. The mandatory sign-off workflow is the design
choice that maintains this classification. See `compliance/eu_ai_act_compliance.md`.

**GDPR:** Processing under legitimate interest for commercial due diligence.
Supabase hosted in EU (Ireland). OpenAI zero data retention option available.
DPAs required with OpenAI and Anthropic before production. See
`compliance/gdpr_documentation.md`.

**Portuguese law:** System grounded in NRAU Lei n.º 6/2006, Código Civil Arts
1022-1120. Portugal-specific fields and risk flags aligned with current legal
obligations.

---

## Business Case in One Page

| Metric | Value |
|---|---|
| Annual abstraction cost (current) | €128,000 -- €192,000 |
| Total build cost | €43,000 -- €70,000 |
| Annual run cost | €8,000 -- €15,000 |
| 12-month ROI | 165% (conservative) |
| Break-even | Month 5 |
| 36-month ROI | 493% (conservative) |
| Deal cycle reduction | 13 days → 5 days |
| Cost per lease (AI) | €0.025 |
| Cost per lease (manual) | €480 -- €960 |

---

## What Comes Next

**Pilot (Q1 2027):** Run the system alongside the existing manual process on one
real acquisition. Measure accuracy on real leases. Verify lawyer adoption.
Confirm time savings. Cost: €20,000 -- €30,000.

**Pilot success gates:** ≥85% extraction accuracy on real leases, ≥60% time
savings, zero undetected critical errors, ≥2 of 3 lawyers rate it as useful.

**Full deployment (Q3 2027):** After successful pilot, deploy on all acquisitions.
Add OCR layer for scanned leases, integrate with financial model (human-approved),
launch portfolio monitoring dashboard.

**Commercialisation (2028+):** If the pilot proves strong ROI, productise as a
vertical SaaS for Portuguese commercial real estate. The NRAU legal grounding, the
Portuguese law corpus, and the Finanças/NIF extraction are genuine differentiators
that generic SaaS tools do not have.

---

## Document Index

| Document | Location | What it covers |
|---|---|---|
| This document | project_overview.md | Full project summary |
| Use case definition | use_case_definition.md | Problem, stakeholders, success criteria |
| ROI and risk | roi_risk_assessment.md | Financial case, risk matrix |
| Strategic plan | strategic_plan.md | Phases, GTM, KPIs, commercialisation |
| EU AI Act | compliance/eu_ai_act_compliance.md | Risk classification, obligations |
| GDPR | compliance/gdpr_documentation.md | Data flows, DPIA, transfers |
| MVP documentation | mvp/mvp_documentation.md | Quick start, architecture, limits |
| POC documentation | poc/poc_documentation.md | n8n workflow, steps, limits |
| LangSmith evaluation | evaluation/langsmith.md | What was measured, what failed |
| Stress test | evaluation/stress_test.md | Parallelisation, determinism |
| Proposal test | evaluation/acquisition_proposal_test.md | Proposal generator results |
| Round 1 decision | feedback/round1_decision.md | Teaching staff feedback, decision |
