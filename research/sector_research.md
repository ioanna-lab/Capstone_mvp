# Sector Research: Commercial Real Estate & Construction (Mid-Market)

## Company Profile — Chleo's Context

**Sector:** Commercial real estate development and property acquisition  
**Company size:** Mid-market, 200–1,000 employees  
**Geography:** Southern Europe (primary market); pan-European acquisitions  
**Core activity:** Acquiring, developing, and managing commercial property portfolios  
**Deal volume:** Approximately 8–12 acquisitions per year  
**Legal team size:** 3–6 in-house lawyers plus external counsel on larger deals  

---

## Market Context

### AI adoption in real estate — where the sector stands

The real estate sector has historically been a cautious technology adopter, but AI adoption is
accelerating sharply. The JLL Global Real Estate Technology Survey 2025 found that 88% of
real estate investors, owners and landlords are already piloting AI — up from just 5% in 2023.
Despite this, over 60% remain strategically, organisationally and technically unprepared for
scaled AI implementation beyond pilots.

In property management specifically, Buildium's 2026 report found adoption jumped from 20%
in 2024 to 58% in 2025, but only 8% of companies had fully automated any process. The
pattern is clear: firms are experimenting but not yet operationalising.

The commercial real estate (CRE) sub-sector shows similar dynamics:
- 68% of CRE firms planned to increase AI investment in 2024 (Gitnux, 2026)
- 62% expect AI to transform operations by 2025
- 52% are already using AI for data analytics
- 45% year-on-year growth in CRE AI adoption from 2022 to 2023

The global AI-in-real-estate market was valued at USD 2.9 billion in 2024 and is projected to
reach USD 41.5 billion by 2033 — roughly 14x growth over nine years.

### Where AI investment is going in CRE

According to PropTech research compiled in 2024–2025, the applications attracting the most
venture investment are:
1. Automated underwriting and mortgage processing
2. AI-powered property management platforms
3. Computer vision for property assessment and construction monitoring
4. Generative AI for marketing and content creation
5. **Lease abstraction, compliance, and back-office automation** (enterprise focus)

Institutional players — large REITs, asset managers — have focused disproportionately on
lease abstraction and compliance automation. Mid-market developers have been slower to follow,
creating a window where early movers gain a real operational advantage.

### Construction side: significantly behind

Construction firms lag even further. Only 1.5% of construction firms had any AI tools in use
as of 2024 (Rowan Build, 2025), compared to 70–90% in manufacturing. Among contractors with
over $50 million in revenue, AI adoption grew from 8% in 2020 to 39% by 2023 — showing
that larger construction players are beginning to move, but the long tail is still very early.

---

## The Lease & Due Diligence Problem — Quantified

Manual lease review and due diligence abstraction is the most consistently documented pain
point in CRE operations. The numbers are well-established:

| Metric | Manual | AI-assisted | Source |
|--------|--------|-------------|--------|
| Time per lease (standard) | 4–8 hours | 17–30 minutes | Kolena, MRI Software |
| Time per lease (complex) | Up to 20 hours | 1.5–2 hours | GrowthFactor case study |
| Review accuracy | ~91% | ~94–95% | Oxmaint, 2026 |
| Portfolio abstraction (100 leases) | 800 paralegal hours | 80–160 hours | Oxmaint |
| Cost reduction on outsourced abstraction | — | 50–90% | Kolena, 2025 |
| Overall review time reduction | — | 70–90% | TheAIConsultingNetwork, 2026 |

For a mid-market developer running 8–12 acquisitions per year, each involving 10–30 leases in
a due diligence pack, the total manual abstraction burden is significant:
- At 8 hours per lease × 20 leases × 10 deals = **1,600 paralegal hours per year**
- At an external paralegal rate of €80–120/hour, that is €128,000–€192,000 per year in
  abstraction cost alone — before accounting for internal lawyer time, deal delays, and errors

CBRE research quantifies a further downstream effect: AI-assisted abstraction saves up to
25% of a broker's and lawyer's time across the acquisition workflow, not just the abstraction
step itself.

---

## The Transparency Problem — Why Chleo Is Scared

The survey data is consistent with what Chleo expressed at dinner. Commercial Observer's
2026 industry survey found:
- 44% of real estate investment committees distrust AI-generated analysis
- Only 27% express any level of trust in AI for financial underwriting
- Top concerns: AI hallucinations (41%), integration challenges (33%), data privacy and quality
- "Trust is the gating factor for AI in real estate" — firms evaluate whether outputs can be
  explained, verified and defended in an investment committee setting

This is not irrational. Lease review errors have direct financial consequences. A missed
break clause, a misread rent escalation, or an overlooked co-tenancy trigger can materially
affect deal valuation. The fear is not of AI in the abstract — it is of invisible errors in
high-stakes documents.

The right answer is not to replace human review. It is to make AI output fully auditable:
every extracted field linked to the source passage, every flagged clause pinpointing the exact
location in the document, every output reviewed and signed off by a lawyer before it informs
a decision.

---

## Mid-Market Specific Constraints

The RSM Middle Market AI Survey 2025 found:
- 91% of mid-market executives report their organisations are using AI in some form
- 53% say they were only somewhat prepared when they implemented generative AI
- 62% say generative AI was harder to implement than expected
- 41% cite data quality as the top implementation problem
- 39% cite lack of in-house expertise

For Chleo's company specifically, this translates to:
- No dedicated data science or ML team
- Lease documents likely spread across shared drives, email attachments, and external counsel
  portals — not a clean central repository
- Limited capacity to evaluate vendors or manage a complex technical implementation
- High sensitivity to any solution that could create liability if it produces wrong output

A successful AI solution for this profile must be: low friction to deploy, transparent in its
outputs, and clearly positioned as a tool that augments lawyers rather than replacing them.

---

## Public Data Sources

| Source | What it contains | Relevance | URL |
|--------|------------------|-----------|-----|
| SEC EDGAR (EDGAR full-text search) | Commercial lease agreements filed as exhibits to public company filings | Real lease text for NLP training and POC testing | https://efts.sec.gov/LATEST/search-index?q=%22lease+agreement%22&dateRange=custom&startdt=2020-01-01&enddt=2024-12-31&forms=10-K |
| CUAD Dataset (Hugging Face) | Contract Understanding Atticus Dataset — 510 commercial contracts with 41 clause types labelled by legal experts | Gold-standard labelled contract data for evaluation | https://huggingface.co/datasets/cuad |
| ATTICUS Open Contract Data | Commercial contracts with expert annotations | Supplementary labelled data | https://www.atticusprojectai.org/cuad |
| Kaggle — Real Estate datasets | Property transaction data, price indices, market statistics | Chart data for market context | https://www.kaggle.com/datasets?search=real+estate |
| JLL Research reports | AI adoption surveys, CRE market data | Market benchmarks | https://www.jll.com/en-us/research |
| MSCI Real Estate | European commercial property indices | Market sizing and context | https://www.msci.com/real-estate |

**Primary dataset for POC:** CUAD (Hugging Face) — 510 contracts, 41 labelled clause types,
Creative Commons licence. This is the standard benchmark dataset for contract understanding
NLP tasks and is directly applicable to lease clause extraction.

---

## Sources

- JLL Global Real Estate Technology Survey 2025 — https://www.jll.com/en-us/insights/ai-for-business-growth
- Buildium 2026 Property Management AI Report — via TechnBrains https://www.technbrains.com/blog/ai-in-proptech/
- Gitnux AI in Commercial Real Estate Statistics 2026 — https://gitnux.org/ai-in-the-commercial-real-estate-industry-statistics/
- Oxmaint AI Document Abstraction — https://oxmaint.com/industries/facility-management/ai-document-abstraction-saves-manual-data-entry
- Kolena AI Lease Abstraction Guide — https://www.kolena.com/blog/lease-abstraction-with-ai/
- MRI Software Lease Abstraction — https://www.mrisoftware.com/solutions/lease-abstraction-software/
- TheAIConsultingNetwork 2026 — https://www.theaiconsultingnetwork.com/blog/automating-commercial-lease-abstraction-ai
- Commercial Observer AI Survey 2026 — https://commercialobserver.com/2026/03/real-estate-data-ai-risk/
- RSM Middle Market AI Survey 2025 — https://rsmus.com/insights/services/digital-transformation/middle-market-ai-trends.html
- GrowthFactor AI Lease Abstraction — https://www.growthfactor.ai/resources/blog/ai-powered-lease-abstraction
- Rowan Build AI Adoption Construction 2025 — https://blog.rowan.build/ai-adoption-construction-industry-2025
- V7 Labs AI Real Estate Lease Abstraction 2025 — https://www.v7labs.com/blog/ai-real-estate-lease-abstraction
- Tommaso Maria Ricci AI for Real Estate 2026 — https://www.tommasomariaricci.com/blog/ai-for-real-estate-companies
