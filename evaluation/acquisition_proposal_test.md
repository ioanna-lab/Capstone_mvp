# Acquisition Proposal Test Results
**AI Lease & Due Diligence Review Assistant — Portugal**
**Capstone Round 2 · Ironhack AI Consulting · Ioanna Renta**

---

## What the Acquisition Proposal Generator Does

After all leases in a due diligence pack have been extracted and reviewed, the
system aggregates the results across all leases for a single property and produces
a structured investment recommendation.

This directly addresses the business use case: Chleo's company reviews 10-30
leases per acquisition. The proposal generator turns individual lease reviews
into a single consolidated view for the investment committee.

---

## What It Calculates

| Output | How calculated |
|---|---|
| BUY / REVIEW / PASS | Based on composite risk score and gross yield threshold |
| Gross yield | Total annual rent ÷ asking price × 100 |
| WALE (Weighted Average Lease Expiry) | Rent-weighted average years remaining across all leases |
| Composite risk score | High-risk clauses × 2 + medium-risk clauses × 1, normalised to 0-10 |
| IMT | Asking price × 6.5% (Portuguese commercial property transfer tax) |
| Stamp duty | Asking price × 0.8% (Portuguese acquisition stamp duty) |
| Total acquisition tax | IMT + stamp duty |

---

## Decision Logic

```
IF composite_risk_score >= 7:
    → PASS (too risky)
ELIF composite_risk_score >= 4 OR any high-risk leases:
    → REVIEW (requires legal attention before proceeding)
ELSE:
    → BUY (clean portfolio)

IF gross_yield < 4.0% AND recommendation == BUY:
    → downgrade to REVIEW (yield below Portuguese commercial threshold)
```

---

## Test Run — Parque Logístico Lisboa

**Property:** Parque Logístico Lisboa, Zona Industrial de Lisboa
**Type:** Warehouse
**Asking price:** €8,500,000
**Leases included:** 4 synthetic warehouse leases

### Input leases

| Lease | Category | Flags | High risk |
|---|---|---|---|
| PT_0199_warehouse_Lisboa.pdf | warehouse | 4 | 2 |
| PT_0198_warehouse_Coimbra.pdf | warehouse | 3 | 2 |
| PT_0197_warehouse_Setúbal.pdf | warehouse | 2 | 2 |
| PT_0196_warehouse_Lisboa.pdf | warehouse | 3 | 2 |

### Output

| Metric | Value | Assessment |
|---|---|---|
| Recommendation | REVIEW | High-risk clauses require legal attention |
| Confidence | LOW | No leases have completed lawyer sign-off |
| Gross yield | 0.5% | Below 4% Portuguese commercial threshold |
| WALE | 1.9 years | Short -- significant renewal risk |
| Risk score | 4.5/10 | Moderate -- high-risk clauses present |
| Total annual rent | €43,900 | Extracted from all 4 leases |
| IMT (6.5%) | €552,500 | Portuguese property transfer tax |
| Stamp duty (0.8%) | €68,000 | Portuguese acquisition stamp duty |
| Total tax | €620,500 | 7.3% of asking price |

### Reasoning provided by the system

- 4 lease(s) contain high-risk clauses requiring legal review
- Gross yield 0.52% is below 4% threshold for Portuguese commercial
- WALE of 1.85 years is short -- significant renewal risk
- Total acquisition tax (IMT + Stamp Duty): €620,500 (7.3% of asking price)

### Notes on the test results

**Low gross yield:** The 0.5% yield is because the synthetic warehouse leases
have modest rent amounts relative to an €8.5M asking price. In a real scenario,
4 warehouse units in Lisboa at €8.5M would command €400,000-600,000 annual rent
(5-7% yield). The system correctly identified the yield as below threshold and
factored it into the REVIEW recommendation.

**LOW confidence:** Confidence is LOW because none of the 4 leases have been
through the mandatory lawyer sign-off workflow. Once sign-off is completed, the
confidence level would upgrade to MEDIUM or HIGH.

**Proposal saved to database:** The proposal was saved to the Supabase
`acquisition_proposals` table and is visible in the Review History tab.

---

## Screenshot

See `evaluation/acquisition_proposal_results.png`

---

## How to Run the Acquisition Proposal

1. Upload lease PDFs in the sidebar
2. Run extraction on each lease (Extract & Review tab)
3. Go to **Acquisition Proposal** tab
4. Fill in property details and asking price
5. Select all extracted leases
6. Click **Generate proposal**

The proposal is saved automatically to Supabase. Results include the
BUY/REVIEW/PASS recommendation, all financial metrics, and Portuguese tax
calculations (IMT + stamp duty).
