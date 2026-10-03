# Use Case Proposals: AI for Commercial Real Estate Due Diligence

## Company Context Recap

**Chleo's company:** Mid-market commercial property developer and acquirer  
**Size:** ~400 staff (mid-range of 200–1,000)  
**Activity:** 8–12 acquisitions per year, primarily commercial property in Southern Europe  
**Legal team:** 4 in-house lawyers + external counsel on larger deals  
**Current pain:** Manual lease review and due diligence abstraction consumes 2–3 lawyer-days
per acquisition. Two deals in recent years involved clause errors that had material financial
consequences.

---

## Use Case 1 — Lease & Due Diligence Review Assistant (PRIMARY)

### Problem statement

Before each property acquisition closes, the legal team must review all active leases on the
target property. For a typical acquisition, this means 10–30 commercial lease documents,
each 30–120 pages long. The team manually reads each lease and extracts:

- Lease commencement and expiry dates
- Break option dates and conditions
- Rent amount, review mechanism, and escalation schedule
- Tenant and landlord obligations
- Unusual, non-standard, or high-risk clauses
- Assignment and subletting restrictions
- Service charge and CAM obligations

This takes 4–8 hours per lease for a trained paralegal, and 1–2 hours for a lawyer doing
a focused review. For a 20-lease due diligence pack, that is 2–3 full lawyer-days before
any legal analysis or negotiation begins.

Errors compound the cost: a misread break option or an overlooked rent step that enters a
financial model unchecked can affect deal valuation materially.

### Proposed AI solution

An AI-powered lease review assistant that:
1. Accepts a lease PDF as input (digitally authored or scanned)
2. Extracts all standard lease data fields into a structured JSON output
3. Flags non-standard, unusual, or potentially high-risk clauses with a short plain-language
   explanation of why they are flagged
4. Links every extracted field to the exact source passage in the document (with page number)
5. Produces a one-page human-readable lease abstract the lawyer can review, correct, and
   sign off on in 15–30 minutes rather than 4–8 hours

The lawyer's role shifts from extraction to review and judgment. The AI does the reading;
the lawyer does the thinking.

### Workflow

```
Lease PDF (upload)
    → OCR / text extraction (if scanned)
    → LLM extraction pass: standard fields
    → LLM flagging pass: unusual clauses
    → Structured JSON output + source citations
    → Human-readable lease abstract (Markdown / PDF)
    → Lawyer reviews, corrects, approves
    → Output stored in deal folder
```

### Stakeholders

| Stakeholder | Concern | What the AI addresses |
|-------------|---------|----------------------|
| CEO (Chleo) | Deal speed, cost, risk of missed obligations | Faster reviews, lower error rate, audit trail |
| Head of Legal | Accuracy, liability, lawyer trust | Transparent sourcing, human sign-off required |
| Acquisition team | Deal cycle time | Due diligence pack reviewed in hours not days |
| External counsel | Scope of engagement | Less time on abstraction, more on complex analysis |
| CFO | Legal cost | Reduced paralegal and external counsel hours |

### Success criteria

- Extraction of standard lease fields with accuracy ≥ 90% vs. manual lawyer review
- Time from lease upload to reviewed abstract ≤ 45 minutes (vs. 4–8 hours manual)
- Lawyer adoption: ≥ 80% of due diligence leases processed through the tool within 6 months
  of pilot launch
- Zero instances of an unchecked AI extraction entering a financial model (process criterion)

### Why this fits mid-market

- Volume (8–12 deals × 10–30 leases = 80–360 leases per year) is large enough to justify
  investment and small enough to run a meaningful pilot without enterprise infrastructure
- In-house legal team is large enough to have a workflow but small enough that the time
  saving is immediately visible and felt
- No dedicated data science team means the solution must be no/low-code or API-based —
  no custom model training, prompt-based extraction on a general LLM

### Data sources for POC and eval

- **CUAD (Contract Understanding Atticus Dataset):** 510 commercial contracts with 41 clause
  types labelled by legal experts. Available on Hugging Face under Creative Commons licence.
  URL: https://huggingface.co/datasets/cuad
- **SEC EDGAR commercial lease exhibits:** Real commercial lease agreements filed as exhibits
  to public company 10-K and 8-K filings. Publicly available, no personal data.
  URL: https://efts.sec.gov/LATEST/search-index?q=%22lease+agreement%22&forms=10-K
- **Synthetic leases:** 5–10 synthetic lease documents generated for the POC eval set,
  with known ground truth for pass/fail evaluation

---

## Use Case 2 — Portfolio Lease Obligation Tracker

### Problem statement

Once acquired, each property enters the portfolio. Lease obligations — rent reviews, break
options, renewal deadlines, tenant notice periods — must be tracked across the entire
portfolio. Currently this is done in spreadsheets maintained by the asset management team.
Critical dates are missed. A break option exercised by a tenant can be overlooked until
the notice window has closed, removing Chleo's ability to respond.

### Proposed AI solution

A downstream extension of Use Case 1. Once a lease is extracted and reviewed, its key
dates and obligations are automatically written to a portfolio database. A monitoring layer
surfaces:

- Upcoming critical dates (break options, rent reviews, lease expiries) at 90/60/30-day
  horizons
- Portfolio-level summaries: how many leases expire in the next 12 months, total rent at
  risk, concentration by tenant or property type
- Exception alerts: leases with unusual clause combinations that warrant re-review

### Why this is Use Case 2, not 1

This use case depends on Use Case 1 being operational first. The tracker is only as good as
the data that feeds it. It is the natural Phase 2 — once the extraction is reliable and the
legal team trusts the output, automating the downstream tracking is a low-effort extension.

### Stakeholders

Asset managers, CFO, Head of Legal, CEO

### Fit for company size

Strong. A 400-person developer managing 50–150 properties with manually-tracked lease
obligations is exactly the profile where a structured portfolio view has immediate value.

---

## Use Case 3 — Construction & Fit-Out Contract Pre-Screening

### Problem statement

When Chleo's company procures construction or fit-out work for a development project,
incoming contractor proposals and contracts must be reviewed for scope, liability caps,
penalty clauses, and variations from standard terms. This pre-screening work currently
falls on the same legal team already stretched by acquisition due diligence.

### Proposed AI solution

An AI pre-screening layer that:
1. Compares an incoming contract against a library of standard terms
2. Flags deviations: increased liability caps, non-standard penalty clauses, scope ambiguity
3. Generates a short "points for negotiation" summary for the lawyer

### Why this is Use Case 3

Data availability is lower (no equivalent of CUAD for construction contracts). The document
variability is higher. The legal workflow is different from lease review. Deprioritised for
Round 1; worth revisiting in Round 2 if the lease use case is well established.

---

## Use Case Prioritisation Summary

| Use Case | Priority | Reason |
|----------|----------|--------|
| Lease & Due Diligence Review Assistant | **1 — Primary** | Clear pain, quantified value, public data, well-scoped POC, direct ROI |
| Portfolio Lease Obligation Tracker | 2 — Phase 2 | Depends on Use Case 1; easy extension once extraction is trusted |
| Construction Contract Pre-Screening | 3 — Phase 3 | Lower data availability, different workflow, deprioritise for now |

---

## Recommendation to Chleo

Start with one capability, run end to end, and demonstrate that the output is trustworthy
before expanding. The lease review assistant is the right starting point because:

1. The pain is felt immediately and daily by the legal team
2. The ROI is calculable and defensible (lawyer hours × deal volume)
3. The output is fully auditable — every field traced to a source passage
4. The risk of a wrong output is contained by the mandatory human review step
5. Success in Use Case 1 builds the data foundation for Use Case 2 at low marginal cost
