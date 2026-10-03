# AI Opportunities & Risks: Commercial Real Estate, Mid-Market

## Company Context

Chleo runs a mid-market commercial property developer and acquirer (200–1,000 staff,
Southern Europe). The company executes 8–12 acquisitions per year. Each acquisition
involves a legal due diligence phase in which in-house lawyers and external counsel manually
review lease abstracts and due diligence packs to identify key dates, financial obligations,
unusual clauses, and risks. This process currently takes 2–3 lawyer-days per acquisition.

---

## Opportunity Map

### Opportunity 1 — Lease & Due Diligence Review Automation (PRIMARY)

**The problem it solves:**  
Manual extraction of key lease terms is slow, expensive, and error-prone. Each lease can
take 4–8 hours to abstract manually. A typical acquisition due diligence pack contains
10–30 leases. Two missed or misread clauses on past deals have had material financial
consequences for the company.

**What AI makes possible:**  
An LLM-based extraction system ingests commercial lease PDFs and outputs a structured
summary per lease: key dates (commencement, expiry, break options), rent and escalation
schedules, tenant obligations, unusual or non-standard clauses flagged for human review.
Every extracted field is linked back to the exact source passage in the document.

**Fit for company size:**  
Mid-market is the sweet spot for this use case. Institutional players already have
enterprise tools. Small firms do not have the deal volume to justify investment.
A 200–1,000-person developer running ~10 deals/year has enough volume that automation
pays back quickly, but a lean enough legal team that the time saving is immediately felt.

**Transparency answer for Chleo:**  
The AI does not make decisions. It produces a structured first draft with source citations.
A lawyer reviews, corrects, and approves every output before it informs any decision.
The AI is a fast paralegal, not a replacement for legal judgment.

**Estimated value:**  
- 1,600 paralegal hours saved per year (at 20 leases × 10 deals × 8 hours)
- At €80–120/hour external rate: €128,000–€192,000/year in direct cost
- Additional value: faster deal cycles, reduced risk of missed obligations

---

### Opportunity 2 — Portfolio Risk Monitoring

**The problem it solves:**  
Once a property is acquired, ongoing lease obligations (rent reviews, break options,
renewal deadlines) are tracked manually in spreadsheets. Critical dates are missed.

**What AI makes possible:**  
Automated extraction feeds a live dashboard of upcoming lease events across the portfolio.
Alerts fire 90/60/30 days before a break option, a rent review, or a lease expiry.

**Fit for company size:**  
Well suited. Mid-market developers typically manage 30–150 assets. Manual tracking at that
scale is fragile. A structured database of extracted lease terms enables portfolio-level
queries that are currently impossible.

**Transparency answer for Chleo:**  
The system surfaces dates and obligations that already exist in signed documents.
It does not interpret or decide — it reminds. Human review before any action.

---

### Opportunity 3 — Tender & Contract Review Support

**The problem it solves:**  
Construction and fit-out contracts for new developments contain scope, liability, and
penalty clauses that need careful review. Legal bandwidth is a bottleneck.

**What AI makes possible:**  
AI pre-screens incoming contracts, flags non-standard clauses, identifies scope gaps,
and generates a summary for the lawyer to review — reducing the time before the lawyer
engages from hours to minutes.

**Fit for company size:**  
Moderate fit. More useful for companies with higher development (rather than acquisition)
activity. Deprioritised relative to Opportunity 1 for this capstone.

---

## Risk Map

### Risk 1 — AI Hallucination on Legal Text

| Dimension | Detail |
|-----------|--------|
| Likelihood | Medium |
| Impact | High |
| Category | Technical / Legal |
| Description | LLMs can confidently produce plausible-sounding but incorrect extractions. A hallucinated break date or a fabricated rent escalation clause that passes into a deal model without review could cost significantly more than the AI saved. |
| Mitigation | Human-in-the-loop mandatory before any output is used. Every extracted field links to source text. Confidence scores surfaced. Low-confidence fields routed to human review automatically. Evaluation framework tests specifically for hallucination on lease-specific inputs. |

---

### Risk 2 — Data Quality & Document Variability

| Dimension | Detail |
|-----------|--------|
| Likelihood | High |
| Impact | Medium |
| Category | Operational / Technical |
| Description | Lease documents vary enormously in format: scanned PDFs, handwritten amendments, multi-part contracts with cross-references. OCR quality on scanned documents degrades extraction accuracy. Non-standard clause structures confuse extraction models trained on standard templates. |
| Mitigation | Pre-processing pipeline with OCR quality check. Flagging documents where extraction confidence is below threshold. Starting the pilot with digitally-authored leases only, then extending to scanned documents in a second phase. |

---

### Risk 3 — Lawyer Adoption & Trust

| Dimension | Detail |
|-----------|--------|
| Likelihood | Medium–High |
| Impact | High |
| Category | Organisational |
| Description | If the legal team does not trust the output, they will re-do the work manually — paying both the AI cost and the manual cost. This is the most common failure mode for legal AI tools. Trust is built through demonstrable accuracy and transparent sourcing, not through telling lawyers to trust the AI. |
| Mitigation | Co-design the output format with the legal team before building. Run the pilot on a completed deal (where ground truth is known) so lawyers can see exactly where the AI was right and where it needed correction. Make the correction workflow frictionless — the lawyer's changes improve future outputs. |

---

### Risk 4 — EU AI Act & GDPR Compliance

| Dimension | Detail |
|-----------|--------|
| Likelihood | Low–Medium (for this specific use case) |
| Impact | Medium |
| Category | Regulatory |
| Description | The EU AI Act classifies AI systems used in credit and financial decisions as high-risk. Lease review for property acquisition sits adjacent to financial underwriting. If the system's output feeds directly into deal valuation or financing decisions without human review, it could attract high-risk classification obligations. GDPR is relevant where leases contain personal data of individual tenants (residential sub-tenants, guarantors). |
| Mitigation | Design the system explicitly as a drafting aid, not a decision system. The lawyer signs off on every output. No automated decision-making. For GDPR: process only commercially-necessary data, minimise retention of personal data extracted from documents, document legal basis (legitimate interest for commercial due diligence). Classification likely falls under limited risk with these design choices. |

---

### Risk 5 — Vendor & Model Dependency

| Dimension | Detail |
|-----------|--------|
| Likelihood | Medium |
| Impact | Medium |
| Category | Strategic / Technical |
| Description | Building on a single LLM provider (OpenAI, Anthropic) creates dependency on that provider's pricing, availability, and policy changes. An off-the-shelf lease abstraction SaaS creates vendor lock-in and limits customisation for the company's specific clause vocabulary. |
| Mitigation | Use an open or switchable API layer (LangChain/LangGraph) so the underlying model can be swapped. For the MVP, Anthropic Claude API is the primary model. For production, evaluate open-weight models (Mistral, LLaMA) for on-premises processing of confidential deal documents. |

---

### Risk 6 — Scope Creep

| Dimension | Detail |
|-----------|--------|
| Likelihood | High (for internal projects) |
| Impact | Medium |
| Category | Operational |
| Description | "AI for lease review" can expand rapidly into "AI for everything legal." Trying to solve portfolio monitoring, contract review, and due diligence simultaneously increases cost, complexity, and time to value. |
| Mitigation | Constrain Round 1 (and the pilot) to a single, well-defined capability: structured extraction from a single lease document producing a standardised output. Expand to portfolio monitoring only after the core extraction is reliable and trusted. |

---

## Opportunity vs Risk Summary

| | Lease & Due Diligence Review | Portfolio Risk Monitoring | Tender Review |
|---|---|---|---|
| Business value | High | Medium–High | Medium |
| Technical feasibility | High | High | Medium |
| Data availability | High (CUAD, EDGAR) | Medium | Low |
| Regulatory risk | Low–Medium | Low | Low |
| Adoption risk | Medium | Low | Medium |
| Recommended priority | **Primary (now)** | Secondary (Phase 2) | Tertiary (Phase 3) |

---

## Key Takeaway for Chleo

The opportunity is clear and quantifiable. The risks are real but manageable with the right
design choices — specifically: human review of every output, transparent sourcing, and a
pilot scoped tightly before any wider rollout. The question is not whether the technology
works. The technology works. The question is whether the company can implement it in a way
that the legal team trusts and uses consistently. That is an organisational question as much
as a technical one, and it is the focus of the pilot design.
