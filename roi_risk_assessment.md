# ROI and Risk Assessment
**AI Lease & Due Diligence Review Assistant — Portugal**
**Capstone Round 2 · Ironhack AI Consulting · Ioanna Renta**

---

## Part 1 — ROI Analysis

### Upfront Costs

| Item | Low estimate | High estimate | Notes |
|---|---|---|---|
| POC development | €8,000 | €15,000 | 3–4 weeks, one AI consultant |
| Pilot build (MVP) | €20,000 | €30,000 | 8–10 weeks, consultant + lawyer co-design |
| Full deployment | €15,000 | €25,000 | 8–12 weeks, production hardening |
| **Total build cost** | **€43,000** | **€70,000** | |

### Ongoing Costs (Annual)

| Item | Low estimate | High estimate | Notes |
|---|---|---|---|
| OpenAI API (GPT-4o) | €3,000 | €6,000 | ~€0.02–0.04 per lease, 10 deals × 20 leases |
| Anthropic API (Claude) | €500 | €1,000 | Validation calls only |
| Supabase hosting | €25 | €300 | Free tier → Pro as volume grows |
| Streamlit Cloud / Railway | €0 | €500 | Free tier sufficient for pilot |
| Maintenance (10% of build) | €4,300 | €7,000 | Bug fixes, prompt updates |
| LangSmith tracing | €0 | €500 | Free tier sufficient for pilot |
| **Total annual run cost** | **€7,825** | **€15,300** | |

### Quantified Business Value

| Value driver | Calculation | Annual value |
|---|---|---|
| Lawyer time saved (abstraction) | 10 deals × 20 leases × 5.5h saved × €120/hr | €132,000 |
| Paralegal time saved | 10 deals × 20 leases × 3h saved × €80/hr | €48,000 |
| Deal cycle acceleration | 2 more deals per year at €50,000 margin each | €100,000 |
| Error prevention (2 past errors/yr) | Avg financial impact €75,000 per error prevented | €150,000 |
| **Conservative annual value** | Lawyer + paralegal savings only | **€180,000** |
| **Full annual value** | All drivers | **€430,000** |

### ROI Calculations

**Assumptions:**
- 10 deals per year, 20 leases per deal (conservative)
- Lawyer rate: €120/hr, paralegal rate: €80/hr
- Time saved per lease: 5.5 hours lawyer, 3 hours paralegal
- Build cost amortised over 3 years
- Conservative value only (time savings, no deal acceleration or error prevention)

**12-month ROI (conservative):**
```
Annual value:          €180,000
Annual run cost:       €11,500 (midpoint)
Build cost year 1:     €56,500 (midpoint, full in year 1)
Net benefit year 1:    €180,000 - €11,500 - €56,500 = €112,000
ROI year 1:            (€112,000 / €68,000) × 100 = 165%
```

**36-month ROI (conservative):**
```
Total value (3 yrs):   €540,000
Total cost (3 yrs):    €56,500 build + €34,500 run = €91,000
Net benefit:           €449,000
ROI 36 months:         (€449,000 / €91,000) × 100 = 493%
```

### Assumptions Table

| Assumption | Value | Source |
|---|---|---|
| Deals per year | 10 | Company stated |
| Leases per deal | 20 (avg) | Industry benchmark |
| Manual abstraction time | 4–8h per lease | DLA Piper 2025 survey |
| AI-assisted review time | 0.5–1.5h per lease | Kolena 2025 benchmark |
| Lawyer hourly rate | €120 | Southern European legal market rate |
| Paralegal hourly rate | €80 | Southern European legal market rate |
| API cost per lease | €0.02–0.04 | Measured in MVP (€0.0218 avg) |
| Error rate manual | 2 material errors/yr | Company stated |

### Break-Even

At conservative value assumptions, break-even occurs at **month 5** of year 1.
Even if actual savings are 50% lower than projected, break-even is within year 1.

---

## Part 2 — Risk Matrix

| # | Risk | Category | Likelihood (1–5) | Impact (1–5) | Score | Mitigation |
|---|---|---|---|---|---|---|
| R1 | AI hallucination on legally important fields (break options, rent terms) | Technical | 3 | 5 | 15 | Every field cites source text; mandatory lawyer sign-off before use; Claude cross-validation flags disagreements; temperature=0 for determinism |
| R2 | Lawyer non-adoption — team re-does work manually | Operational | 3 | 4 | 12 | Co-design output format with legal team before build; run pilot on completed deals so lawyers see accuracy; show time savings with real numbers |
| R3 | EU AI Act reclassification to high risk | Regulatory | 2 | 4 | 8 | Maintain human-in-the-loop as a hard architectural constraint; do not allow direct financial model integration without review; document governance |
| R4 | GDPR breach — lease data contains personal data (guarantors, NIF) | Regulatory | 2 | 4 | 8 | Process data under legitimate interest (commercial due diligence); data minimisation — only extract fields relevant to review; Supabase hosted in EU (Ireland); DPA with Supabase and OpenAI |
| R5 | Document quality degradation — scanned leases produce low accuracy | Technical | 3 | 3 | 9 | Start pilot with digitally-authored leases only; add OCR layer in Phase 2; flag low-confidence extractions for full manual review |
| R6 | Prompt regression — model updates change extraction behaviour | Technical | 3 | 3 | 9 | LangSmith tracing on every run; versioned prompts in code; regression tests on 200-lease corpus before any prompt change; pin model versions |
| R7 | OpenAI / Anthropic API outage or pricing change | Operational | 2 | 3 | 6 | Multi-model architecture already built (gpt-4o, o1, o3-mini); Claude as fallback extractor; cost tracker alerts on spend spikes |
| R8 | Confidential deal data leaving the company network | Regulatory/Ethical | 2 | 5 | 10 | OpenAI zero data retention option for API; Anthropic same; all data processed in transit only — nothing stored at model provider; Supabase EU-hosted |
| R9 | Over-reliance — lawyers stop checking AI output | Ethical | 2 | 5 | 10 | Mandatory sign-off checkboxes cannot be skipped; disclaimer on every output; training for legal team on AI limitations; periodic accuracy audits |
| R10 | Incorrect Portuguese law application — NRAU changes | Regulatory | 2 | 4 | 8 | Portuguese law context versioned in portugal_law.py; annual review of NRAU changes; lawyer review of the legal ruleset before each pilot phase |

### Risk Priority

High priority (score ≥10): R1, R8, R9
Medium priority (score 6–9): R2, R3, R4, R5, R6, R7, R10
Low priority (score <6): None

### Risk Owner and Review Cadence

Risks R1, R8, R9 (highest score) are reviewed monthly during the pilot.
All other risks reviewed quarterly. Risk owner: AI consulting team + legal team lead.
