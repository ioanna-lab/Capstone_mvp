# Round 1 Decision
**AI Lease & Due Diligence Review Assistant**
**Ironhack AI Consulting · Ioanna Renta**

---

## Decision: PROCEED — same use case, same industry, deepen Portugal localisation

After presenting Round 1 to teaching staff and colleagues, the decision is to
proceed with the same use case (AI-assisted lease and due diligence review for
commercial real estate) and deepen it significantly for Round 2.

No industry or use case change. The core hypothesis was validated.

---

## Feedback Received

**Strongest points (from colleagues and teaching staff):**
- End-to-end workflow with lawyer sign-off is clear and credible
- Time savings projection is compelling and well-evidenced
- The combination of source citations and mandatory human review directly addresses
  Chleo's transparency concern
- Use case is specific enough to feel commercially real

**Weaknesses identified:**
1. POC tested on 5 AI-generated leases only — performance on 20–50 real leases
   untested and undemonstrated
2. Accuracy results not convincing without real document validation
3. Hallucination risk on legally important fields (break options, rent terms) is
   the highest concern for the audience
4. Source citations must include page number and clause reference — not just quoted
   text
5. No feedback loop — system does not learn from lawyer corrections

**Average rating from colleagues: 4.50/5**

---

## What Changes for Round 2

Based on this feedback, Round 2 addresses every point:

| Feedback point | Round 2 response |
|---|---|
| Only 5 synthetic leases | Generated 200 synthetic Portuguese leases with ground truth CSV |
| Real lease accuracy unproven | 200-lease stress test demonstrating scale; pilot plan defined |
| Hallucination risk | Claude cross-model validation added; agreement score surfaced to lawyer |
| Page and clause citations | Added to every extracted field and every flagged clause |
| No feedback loop | Lawyer corrections saved to Supabase; fed back as few-shot examples |
| Portugal localisation | Full NRAU legal context injected; Portuguese terminology mapping; NIF, Finanças, stamp duty fields |

---

## What Stays the Same

- Use case: commercial lease and due diligence review
- Industry: commercial real estate, mid-market, Southern Europe
- Client profile: Chleo scenario
- Core architecture: LLM extraction + flagging + human review
- Round 1 materials: all preserved in capstone-round1/ folder

---

## Reflection

The Round 1 feedback was well-targeted. The core weakness — small synthetic test
set — was the right thing to push on. The 200-lease corpus with ground truth addresses
this directly, and the LangSmith evaluation in Round 2 turns the manual 5-case
scoring into a reproducible, automated experiment.

The Portugal localisation was implicit in Round 1 (Chleo is in Southern Europe) but
became explicit in Round 2. The legal grounding (NRAU, NIF, Finanças registration)
is a genuine differentiator that generic SaaS tools do not have.

The feedback loop was the most technically interesting addition. Storing lawyer
corrections and injecting them as few-shot examples is a lightweight form of
continuous learning that does not require fine-tuning.
