# Strategic Deployment and Commercialisation Plan
**AI Lease & Due Diligence Review Assistant — Portugal**
**Capstone Round 2 · Ironhack AI Consulting · Ioanna Renta**

---

## 1. Deployment Phases

### Phase 1 — POC (Complete)
**Duration:** 3–4 weeks
**Cost:** €8,000–€15,000
**Status:** ✅ Complete

Proof of concept built in n8n demonstrating end-to-end lease extraction.
5 synthetic leases tested, evaluation plan defined, teaching staff presentation
delivered. Decision: proceed to Round 2.

### Phase 2 — Pilot (Proposed)
**Duration:** 10 weeks
**Cost:** €20,000–€30,000
**Start:** Q1 2027 (pending client approval)

The pilot runs the AI system alongside the existing manual process on one real
acquisition. Lawyers use both methods and compare results. At the end, the client
has real accuracy numbers from real documents.

**Pilot scope:**
- One upcoming acquisition (10–20 leases)
- 2–3 lawyers trained on the system
- Full LangSmith tracing on every run
- Weekly accuracy review against manual abstraction
- Lawyer sign-off required on every lease

**Pilot success criteria (gates to full deployment):**
- Field extraction accuracy ≥85% on real leases (measured against manual review)
- Lawyer time savings ≥60% compared to manual abstraction
- Zero undetected critical errors (break options, rent amounts)
- ≥2 of 3 lawyers rate the system as "useful" or "very useful"
- Claude agreement score ≥75% on average across all pilot leases

**If pilot fails any gate:**
- Analyse failure mode
- Update prompts, add Portuguese law examples to RAG corpus
- Re-run evaluation before proceeding

### Phase 3 — Full Deployment
**Duration:** 8–12 weeks
**Cost:** €15,000–€25,000
**Start:** Q3 2027 (pending pilot success)

Production deployment on all acquisitions. Integration with the client's existing
deal management workflow. All lawyers trained. Monitoring dashboards live.

**Phase 3 additions over pilot:**
- OCR layer for scanned leases
- Integration with financial model (read-only, human-approved)
- Portfolio monitoring dashboard (Phase 2 use case)
- Automated LangSmith regression tests on every prompt change

---

## 2. Timeline and Milestones

| Milestone | Target date | Owner |
|---|---|---|
| Pilot agreement signed | Jan 2027 | Client + AI consultant |
| Lawyer onboarding and training | Feb 2027 | AI consultant |
| First real lease processed | Feb 2027 | Legal team |
| Mid-pilot accuracy review | Mar 2027 | AI consultant + legal team |
| Pilot completion and results report | Apr 2027 | AI consultant |
| Go/no-go decision for full deployment | Apr 2027 | CEO (Chleo) |
| Full deployment build start | May 2027 | AI consultant |
| Full deployment go-live | Jul 2027 | AI consultant |
| Phase 3 use case (portfolio monitoring) | Q4 2027 | AI consultant |

---

## 3. Go-to-Market

**Primary buyer:** CEO and CFO of mid-market commercial real estate developers
(200–1,000 staff) in Portugal and Southern Europe.

**Economic buyer:** CEO (deal cycle, cost reduction)
**Technical buyer:** Head of legal or general counsel (accuracy, trust, workflow)
**Champion:** One senior lawyer who co-designs the output format

**Channel:** Direct consulting engagement. The system is built custom for each
client, not sold as a SaaS product in Round 2.

**Pricing model (consulting):**
- Phase 1 POC: €8,000–€15,000 fixed fee
- Phase 2 Pilot: €20,000–€30,000 fixed fee
- Phase 3 Full deployment: €15,000–€25,000 fixed fee
- Annual support and maintenance: €10,000–€20,000 per year

**Differentiator vs. off-the-shelf SaaS (e.g. Kira, Luminance):**

| Factor | This system | Enterprise SaaS |
|---|---|---|
| Portuguese law localisation | Deep (NRAU, NIF, Finanças) | Generic, not localised |
| Customisation | Fully customisable | Fixed output format |
| Data residency | EU only (Supabase Ireland) | Often US-hosted |
| Annual licence | €7,825–€15,300 | €30,000–€60,000 |
| Onboarding | 2–3 weeks | 3–6 months |
| Human-in-the-loop | Mandatory by design | Optional |

---

## 4. Stakeholder Communication Plan

| Stakeholder | Message | Channel | Frequency |
|---|---|---|---|
| CEO (Chleo) | ROI, deal cycle reduction, risk mitigation | Executive briefing | Monthly during pilot |
| Legal team | Time savings, accuracy, trust-building | Training workshops | Weekly during pilot |
| Investment committee | Transparency, human oversight, compliance | Board update | Quarterly |
| IT / security | Data residency, GDPR compliance, API security | Technical review | At deployment |
| External counsel | Augmentation not replacement, review role preserved | 1:1 briefing | Before pilot start |

**Change management principle:** Co-design with lawyers, not deploy at lawyers.
The output format is designed with the legal team before building. Lawyers see
accuracy data from the pilot before full deployment. No adoption by mandate.

---

## 5. KPIs Per Phase

### Pilot KPIs
| KPI | Target | Measurement |
|---|---|---|
| Field extraction accuracy | ≥85% | Manual comparison on 10 pilot leases |
| Lawyer time per lease | <1 hour | Time tracking |
| Claude agreement score | ≥75% average | LangSmith dashboard |
| Critical error rate | 0 | Manual audit |
| Lawyer satisfaction | ≥3/5 | Post-pilot survey |

### Full Deployment KPIs
| KPI | Target | Measurement |
|---|---|---|
| Due diligence cycle | ≤5 working days | Deal tracking |
| Cost per deal (abstraction) | <€5,000 | Finance tracking |
| System uptime | ≥99% | Railway/Streamlit monitoring |
| Annual API cost | <€15,000 | Cost tracker in app |
| Lawyer adoption rate | ≥80% of leases processed by AI | Usage logs |

---

## 6. Commercialisation Model

**Phase 1 (current):** Consulting project. Build, deploy, and maintain for one client.
Revenue: project fees.

**Phase 2 (2028+):** If pilot proves strong ROI, productise as a vertical SaaS for
Portuguese commercial real estate. The Portuguese law corpus, the NRAU-grounded
prompts, and the Finanças/NIF extraction are genuine differentiators that a generic
SaaS does not have.

**Target SaaS metrics (2028):**
- 10 clients at €15,000/year = €150,000 ARR
- Gross margin ~70% (API costs are the main variable cost)
- TAM: ~500 mid-market real estate developers in Portugal + Spain + Greece

**IP assets:**
- portuguese_law.py (NRAU legal ruleset as machine-readable prompt)
- 200-lease Portuguese training corpus with ground truth
- Extraction prompts tuned for Portuguese legal terminology
- Cross-model validation architecture (GPT-4o + Claude)
