# Timeline Estimate: AI Lease & Due Diligence Review Assistant

## Overview

Three phases: POC, Pilot, Full Deployment. The POC is what we are building now.
The pilot is the next step Chleo would commit to after a successful Round 1 presentation.
Full deployment follows a successful pilot.

---

## Phase 1 — POC (Proof of Concept)

**Duration:** 3–4 weeks  
**Cost:** €8,000–€15,000  
**Goal:** Demonstrate that an LLM can extract structured lease data from a real document
with sufficient accuracy to be worth piloting. This is the n8n workflow plus eval plan
delivered in Round 1 of this capstone.

| Week | Activity |
|------|----------|
| 1 | Finalise use case scope; select 5–10 sample lease documents from CUAD / EDGAR; design extraction prompt |
| 2 | Build n8n workflow: PDF in → LLM extraction → structured JSON out |
| 3 | Run eval plan: 5+ cases scored against ground truth; measure accuracy on standard clauses |
| 4 | Present to teaching staff / Chleo; collect feedback; decide keep or change |

**Milestone:** POC runs on at least 5 real lease documents; eval plan shows pass/fail results;
cost and limitations clearly documented.

**Assumption:** 1 AI engineer working part-time (3 days/week); existing cloud API access.

---

## Phase 2 — Pilot

**Duration:** 8–10 weeks  
**Cost:** €20,000–€30,000 (includes Phase 1 build cost if proceeding directly)  
**Goal:** Run the system on one real acquisition due diligence pack (10–20 leases) alongside
the existing manual process. Compare outputs. Measure accuracy, time saving, and lawyer
satisfaction. Make a go/no-go decision on full deployment.

| Week | Activity |
|------|----------|
| 1–2 | Upgrade POC to MVP: Python + Streamlit UI; structured output per lease; source citations |
| 3–4 | LangSmith evaluation setup: dataset of 20+ leases; accuracy experiment; trace logging |
| 5–6 | Run parallel review on one real deal: AI output vs manual output; lawyer review |
| 7 | Measure results: accuracy, time saved, lawyer feedback, errors caught vs missed |
| 8 | Adjust prompt and output format based on pilot findings |
| 9–10 | Write pilot report; go/no-go decision; plan for full deployment if green |

**Pilot success criteria (required to proceed to full deployment):**
- Extraction accuracy ≥ 90% on standard clauses
- Lawyer review time per lease ≤ 45 minutes (vs 4–8 hours manual)
- Zero unchecked AI extractions entering a financial model
- ≥ 3 out of 4 lawyers rate the output as "useful" or "very useful"
- No critical errors (missed break option, wrong rent amount) on standard clauses

**Assumption:** One real acquisition deal available for parallel testing; legal team
allocated 2–3 hours per week for feedback and review during pilot.

---

## Phase 3 — Full Deployment

**Duration:** 8–12 weeks after pilot sign-off  
**Cost:** €15,000–€25,000 additional (infrastructure hardening, integrations, training)  
**Goal:** System handles all due diligence lease reviews as standard practice. Integration
with deal management tooling. Portfolio monitoring layer added (Use Case 2).

| Activity | Duration |
|----------|----------|
| Infrastructure hardening: security review, data retention policy, access controls | 2 weeks |
| Integration with deal management system (shared drive, DMS, or CRM) | 3 weeks |
| Full legal team training and onboarding | 1 week |
| Portfolio monitoring layer: extracted data → dashboard of upcoming lease events | 3 weeks |
| Stabilisation and monitoring | 2–3 weeks |

**Milestone:** 100% of acquisition due diligence leases processed through the system;
portfolio monitoring dashboard live; SLA defined for system availability.

---

## Summary Timeline

```
Week 1–4:    POC build and presentation           (~€12k)
Week 5–14:   Pilot on one real deal               (~€20k)
Week 15–26:  Full deployment + portfolio layer    (~€20k)
─────────────────────────────────────────────────────────
Total:       ~6 months from kick-off to full deployment
Total cost:  ~€52k (mid-scenario; within €47k–€65k range)
```

---

## Key Risks to Timeline

| Risk | Likely delay | Mitigation |
|------|-------------|------------|
| No real deal available for pilot | +2–4 weeks | Use a completed past deal with known ground truth as synthetic pilot |
| Legal team bandwidth during busy deal period | +2–3 weeks | Schedule pilot during a quieter quarter; use synthetic documents in parallel |
| LLM output quality requires significant prompt iteration | +2–3 weeks | Build eval plan early; catch prompt issues in POC phase, not pilot |
| IT / security review takes longer than expected | +3–4 weeks | Start security conversation in week 2 of POC, not after pilot |

---

## What the next meeting with Chleo should commit to

After the Round 1 presentation, the ask is not full deployment. The ask is:

> "Commission a 10-week pilot on one upcoming acquisition. We run the AI alongside your
> legal team's existing process. At the end, you have real accuracy numbers, real time
> savings, and a clear picture of what full deployment would cost and deliver. The pilot
> costs €20,000–€30,000. If it does not meet the success criteria we defined, you stop."

That is a low-risk, time-boxed commitment a CEO can say yes to.
