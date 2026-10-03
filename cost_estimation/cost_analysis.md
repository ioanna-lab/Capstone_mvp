# Cost Analysis: AI Lease & Due Diligence Review Assistant

## Scope

This estimate covers the cost of building and operating an AI-assisted lease review system
for Chleo's company: a mid-market commercial property developer running 8–12 acquisitions
per year with a 4-person in-house legal team.

All figures are estimates at a consulting-conversation level. Assumptions are stated
explicitly. A pilot phase would validate or revise these numbers before full commitment.

---

## Upfront (Build) Costs

| Item | Low estimate | High estimate | Notes |
|------|-------------|---------------|-------|
| Solution design & architecture | €5,000 | €10,000 | 2–4 weeks consulting; scoping, workflow design, vendor evaluation |
| LLM API integration & prompt engineering | €8,000 | €15,000 | n8n POC → Python/LangChain MVP; extraction prompt design and testing |
| UI development (Streamlit or similar) | €5,000 | €10,000 | Simple upload interface + structured output view; lawyer-facing |
| Evaluation framework & testing | €3,000 | €6,000 | Eval dataset, LangSmith setup, accuracy testing against CUAD baseline |
| Legal team onboarding & change management | €2,000 | €4,000 | Training sessions, workflow documentation, feedback loop setup |
| Infrastructure setup | €1,000 | €2,000 | Cloud hosting (AWS/GCP), environment, security config |
| **Total upfront** | **€24,000** | **€47,000** | |

**Most likely scenario for a mid-market company using a small external AI consultant:**
€28,000–€35,000 upfront, with a 6–10 week build timeline.

---

## Ongoing (Run) Costs — Annual

| Item | Low estimate | High estimate | Notes |
|------|-------------|---------------|-------|
| LLM API usage (Claude or OpenAI) | €3,600 | €7,200 | ~300 leases/year × avg 30 pages × ~€0.01–0.02/page equivalent |
| Cloud hosting & infrastructure | €1,200 | €2,400 | Basic compute; scales with volume |
| Maintenance & prompt updates | €4,000 | €8,000 | Quarterly prompt tuning, model version updates, bug fixes |
| LangSmith evaluation monitoring | €600 | €1,200 | Monitoring plan; scales with trace volume |
| **Total annual run cost** | **€9,400** | **€18,800** | |

**Most likely annual run cost:** €12,000–€15,000/year.

---

## Cost vs Savings

| | Conservative | Mid | Optimistic |
|---|---|---|---|
| Annual manual abstraction cost (saved) | €102,400 | €160,000 | €192,000 |
| Annual AI run cost | €18,800 | €15,000 | €9,400 |
| **Net annual saving** | **€83,600** | **€145,000** | **€182,600** |
| Upfront build cost | €47,000 | €35,000 | €24,000 |
| **Payback period** | **~7 months** | **~3 months** | **~2 months** |

Even in the conservative scenario, the system pays back its build cost within the first year.

---

## What is NOT included in this estimate

- External legal counsel cost reductions (deal cycle compression frees lawyer time)
- Cost of errors avoided (missed clauses on past deals; not quantified here)
- Internal IT or security review costs (assumed manageable within existing IT overhead)
- Licence costs for enterprise lease abstraction SaaS (not the approach taken here;
  this estimate assumes a custom-built system on LLM APIs)

---

## Build vs Buy Comparison

| Approach | Upfront | Annual | Pros | Cons |
|----------|---------|--------|------|------|
| Custom build (this proposal) | €24k–€47k | €9k–€19k | Full control, customisable output format, no vendor lock-in | Requires ongoing maintenance |
| Off-shelf SaaS (Kira, Primer, etc.) | €5k–€15k setup | €30k–€60k licence | Fast to deploy, maintained by vendor | Expensive at scale, fixed output format, data leaves company |
| Hybrid (SaaS POC → custom MVP) | €10k–€25k | €15k–€30k | Validates quickly, builds toward ownership | Transition cost and effort |

**Recommendation for pilot:** Start with a custom-built POC on Claude API (this approach).
Low upfront, full output control, and avoids committing to enterprise SaaS pricing before
the use case is validated internally.

---

## Key Assumptions

1. **300 leases/year** processed through the system (10 deals × 20 leases × 1.5 processing
   passes per lease for extraction + flagging)
2. **Hourly rates** based on Southern European market: paralegal €80/hr, lawyer €120/hr
3. **LLM pricing** based on Claude 3.5 Sonnet API pricing as of mid-2025; subject to change
4. **Build timeline** assumes a 2-person team (1 AI engineer + 1 part-time consultant);
   internal IT support required for infrastructure
5. **Manual cost baseline** uses 8 hours per lease (conservative; complex leases are higher)
6. **80% adoption rate** assumed within 6 months of pilot launch; not all leases will go
   through the tool immediately

---

## Sources

- Claude API pricing: https://www.anthropic.com/api
- Kira Systems pricing: ~$2,500/month base (TheAIConsultingNetwork, 2026)
- Paralegal and lawyer rates: Southern European market benchmarks, 2024–2025
- Manual abstraction cost methodology: derived from sector_research.md figures
