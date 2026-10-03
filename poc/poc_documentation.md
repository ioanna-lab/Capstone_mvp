# POC Documentation — n8n Lease Extraction Workflow
**AI Lease & Due Diligence Review Assistant**
**Capstone Round 1 · Ironhack AI Consulting · Ioanna Renta**

---

## Overview

The Round 1 proof of concept is a no-code workflow built in n8n that demonstrates
end-to-end lease extraction using GPT-4o-mini. It accepts a commercial lease
document via webhook and returns a structured JSON with 16 extracted fields and
flagged unusual clauses.

---

## Tools Used

| Tool | Role | Why chosen |
|---|---|---|
| n8n | Workflow orchestration | No-code, import/export as JSON, visual for demonstration |
| GPT-4o-mini | LLM extraction and flagging | Cost-effective, sufficient accuracy for POC |
| Webhook node | HTTP entry point | Allows any client to call the workflow |
| JSON parsing | Output assembly | Standard JavaScript in n8n code node |

---

## Workflow Steps (6 nodes)

**Node 1 — Webhook**
Listens for HTTP POST requests. Accepts `{ "lease_text": "..." }` as input.
Triggers the workflow when a lease document is submitted.

**Node 2 — Validate Input**
JavaScript code node. Checks that `lease_text` is present and at least 100
characters. Returns a clear error if not. Passes validated text forward.

**Node 3 — Extract Lease Fields (GPT-4o-mini)**
OpenAI node. Sends the lease text with a structured extraction prompt requesting
16 fields as JSON. Temperature=0 for deterministic output.

**Node 4 — Flag Unusual Clauses (GPT-4o-mini)**
OpenAI node. Parallel path. Sends the same lease text with a risk-focused prompt.
Returns flagged clauses with risk level, quoted text, and recommended action.

**Node 5 — Assemble Output**
JavaScript code node. Parses both LLM responses, counts risk levels, adds the
disclaimer, and builds the final structured response.

**Node 6 — Respond to Webhook**
Returns the assembled JSON to the caller.

---

## AI Capability Shown

The POC demonstrates three AI capabilities:

1. **Structured extraction from unstructured legal text** — converting a 20-page
   lease document into a structured JSON with 16 typed fields
2. **Risk classification** — identifying unusual or non-standard clauses and
   assigning risk levels (high/medium/low)
3. **Source citation** — quoting the exact text from the document that supports
   each flag

---

## Sample Input

```json
{
  "lease_text": "THIS COMMERCIAL LEASE AGREEMENT is entered into on 1 March 2024
between LANDLORD: Meridian Property Holdings S.L. and TENANT: Techflow Logistics
GmbH. The lease term commences 1 April 2024 and expires 31 March 2029.
Annual rent: EUR 216,000 payable quarterly in advance.
Break option: Tenant may terminate on 31 March 2027 with 12 months notice and
payment of 6 months rent penalty. Dilapidations liability survives the break..."
}
```

## Sample Output

```json
{
  "extracted_fields": {
    "tenant_name": "Techflow Logistics GmbH",
    "landlord_name": "Meridian Property Holdings S.L.",
    "lease_commencement_date": "2024-04-01",
    "lease_expiry_date": "2029-03-31",
    "rent_amount": "EUR 216,000 per year",
    "break_option_dates": [{"date": "2027-03-31", "conditions": "12 months notice, 6 months penalty"}]
  },
  "flagged_clauses": [
    {
      "clause_type": "Break condition — dilapidations survival",
      "risk_level": "high",
      "quoted_text": "Dilapidations liability survives the break...",
      "plain_language_explanation": "The tenant remains liable for repair costs after exercising the break option. This is non-standard and could result in significant unexpected costs.",
      "recommended_action": "Negotiate removal or cap on dilapidations liability before signing."
    }
  ],
  "summary": {
    "total_flagged_clauses": 1,
    "high_risk_clauses": 1,
    "review_recommendation": "PRIORITY REVIEW REQUIRED",
    "disclaimer": "AI-generated draft. Must be reviewed by a qualified lawyer."
  }
}
```

---

## Limits vs Production

| POC limitation | Round 2 MVP solution |
|---|---|
| No persistent storage | Supabase PostgreSQL |
| No UI | Streamlit 5-tab application |
| No cross-model validation | Claude Haiku validation layer |
| No Portuguese law grounding | portugal_law.py with full NRAU context |
| No source citations with page numbers | Page and clause reference on every field |
| No feedback loop | Lawyer corrections → Supabase → few-shot examples |
| One document at a time | RAG across multiple leases |
| No lawyer sign-off workflow | Mandatory sign-off with checkboxes and name |
| gpt-4o-mini only | 7 models including o1, o3, o3-mini, o1-pro |

---

## How to Reproduce

1. Go to `https://n8n.io` and create a free account
2. Click **New workflow**
3. Click the **...** menu → **Import from file**
4. Upload `poc/poc_workflow.json` from this repository
5. Add your OpenAI API key in the OpenAI nodes
6. Click **Activate** to start the webhook
7. Copy the webhook URL and test with a POST request:

```bash
curl -X POST https://your-n8n-webhook-url \
  -H "Content-Type: application/json" \
  -d '{"lease_text": "YOUR LEASE TEXT HERE"}'
```

**Note:** The workflow was designed and documented but not run live during the
capstone session. The Python MVP was built and run live instead, demonstrating
the same functionality with more features. The n8n JSON is fully importable and
activatable.
