# POC Workflow Documentation: Lease Review Assistant

## Overview

This n8n workflow implements the core AI capability of the Lease & Due Diligence Review
Assistant. It accepts a commercial lease document as text input, runs two parallel LLM
analysis passes, and returns a structured JSON lease abstract with flagged risk clauses.

The workflow is the proof of concept for Use Case 1 (see `research/use_cases.md`). It
demonstrates that an LLM can extract structured lease data and flag unusual clauses from
unstructured legal text, which is the foundational capability the full MVP builds on.

**Tool:** n8n cloud (current version)  
**LLM:** OpenAI GPT-4o (temperature 0 for deterministic output)  
**Input:** HTTP POST request with lease text  
**Output:** Structured JSON lease abstract  
**Workflow file:** `workflow.json` (import directly into n8n)

---

## Architecture

```
[Webhook] → [Validate Input] → [Extract Lease Fields] ──→ [Assemble Output] → [Respond]
                             ↘ [Flag Unusual Clauses] ──↗
```

The Validate Input node fans out to both LLM nodes in parallel. Both run simultaneously
against the same lease text. Assemble Output waits for both to complete, then merges
the results into a single structured response.

---

## Node-by-Node Description

### Node 1 — Webhook (Trigger)

**Type:** Webhook  
**Method:** POST  
**Path:** `/lease-review`  
**Purpose:** Entry point for the workflow. Accepts a POST request containing the lease
document text. The tutor or user sends a POST request to the webhook URL with a JSON body.

**Expected request body:**
```json
{
  "lease_text": "THIS LEASE AGREEMENT is made on the 1st day of January 2024..."
}
```

**How to call it:** Any HTTP client works. In a browser, the easiest way is Postman or
the built-in n8n test webhook. Curl also works:
```bash
curl -X POST https://your-n8n-instance.app.n8n.cloud/webhook/lease-review \
  -H "Content-Type: application/json" \
  -d '{"lease_text": "paste lease text here"}'
```

---

### Node 2 — Validate Input (Code)

**Type:** Code (JavaScript)  
**Purpose:** Validates that the request body contains a `lease_text` field and that it
is long enough to be a real document (minimum 100 characters). Throws a clear error
message if the input is missing or malformed. Passes the validated text downstream with
a character count and timestamp.

**Why this matters:** Prevents the LLM nodes from receiving empty or garbage input, which
would produce meaningless output. Adds a `received_at` timestamp for audit purposes.

---

### Node 3 — Extract Lease Fields (OpenAI GPT-4o)

**Type:** OpenAI Chat  
**Model:** gpt-4o  
**Temperature:** 0 (deterministic — same input always produces same output)  
**Purpose:** First LLM pass. Extracts 16 structured fields from the lease text.

**System prompt role:** Instructs the model to act as a commercial real estate paralegal
and return only valid JSON with no markdown or explanation. Explicitly instructs the model
not to invent data that is not in the document (null if absent).

**Fields extracted:**
- `tenant_name` — Full legal name of the tenant
- `landlord_name` — Full legal name of the landlord
- `property_address` — Full address of the leased property
- `lease_commencement_date` — Lease start date (ISO format)
- `lease_expiry_date` — Lease end date (ISO format)
- `break_option_dates` — Array of break option dates and conditions
- `rent_amount` — Annual or monthly rent with currency
- `rent_review_mechanism` — How and when rent is reviewed
- `rent_escalation_schedule` — Fixed step-ups with dates and amounts
- `security_deposit` — Deposit amount and terms
- `permitted_use` — Stated permitted use of the property
- `assignment_rights` — Whether tenant can assign or sublet
- `tenant_break_conditions` — Conditions for break option validity
- `service_charge` — Service charge or CAM obligations
- `key_tenant_obligations` — Array of main tenant obligations
- `key_landlord_obligations` — Array of main landlord obligations

---

### Node 4 — Flag Unusual Clauses (OpenAI GPT-4o)

**Type:** OpenAI Chat  
**Model:** gpt-4o  
**Temperature:** 0  
**Purpose:** Second LLM pass, running in parallel with Node 3. Reviews the lease for
unusual, non-standard, or high-risk clauses that the legal team should prioritise.

**System prompt role:** Instructs the model to act as a commercial real estate lawyer
doing a risk review. Returns only genuinely unusual items — standard provisions are
not flagged.

**Each flagged clause contains:**
- `clause_type` — Category (e.g. Break condition, Rent review, Assignment restriction)
- `risk_level` — high / medium / low
- `quoted_text` — Exact text from the document (max 200 characters)
- `plain_language_explanation` — What it means and why it is unusual (2–3 sentences)
- `recommended_action` — What the legal team should do

---

### Node 5 — Assemble Output (Code)

**Type:** Code (JavaScript)  
**Purpose:** Receives output from both LLM nodes, parses the JSON responses, handles
any parse errors gracefully, counts risk levels, generates a summary recommendation,
and assembles the final structured response.

**Output structure:**
```
{
  meta: { processed_at, model, version, disclaimer },
  summary: { total_flagged, high_risk, medium_risk, low_risk, review_recommendation },
  extracted_fields: { ...all 16 fields... },
  flagged_clauses: [ ...array of flagged items... ]
}
```

The `disclaimer` field in meta is always present: *"AI-generated draft. Every field must
be reviewed and verified by a qualified lawyer before use in any legal or financial
decision."* This is the transparency mechanism that addresses Chleo's concern and the
EU AI Act human-oversight requirement.

---

### Node 6 — Respond to Webhook

**Type:** Respond to Webhook  
**Status:** 200  
**Purpose:** Returns the assembled JSON to the caller. The response is the complete
lease abstract, ready for the lawyer to review.

---

## Sample Input

The following is a synthetic commercial lease excerpt used for POC testing. It is based
on standard commercial lease structure and is representative of the documents Chleo's
legal team reviews during acquisition due diligence.

```
COMMERCIAL LEASE AGREEMENT

THIS LEASE AGREEMENT ("Lease") is entered into as of the 1st day of March 2024,
by and between:

LANDLORD: Meridian Property Holdings S.L., a company incorporated under the laws
of Spain, with registered address at Calle Gran Via 45, 28013 Madrid, Spain
("Landlord");

TENANT: Techflow Logistics GmbH, a company incorporated under the laws of Germany,
with registered address at Leopoldstrasse 120, 80804 Munich, Germany ("Tenant").

1. PREMISES
Landlord hereby leases to Tenant the commercial premises located at Polígono
Industrial Norte, Nave 12, 08040 Barcelona, Spain, comprising approximately
2,400 square metres of warehouse and office space ("Premises").

2. TERM
The lease term shall commence on 1 April 2024 ("Commencement Date") and shall
expire on 31 March 2029 ("Expiry Date"), unless sooner terminated in accordance
with the provisions hereof.

3. BREAK OPTION
Tenant shall have the right to terminate this Lease on 31 March 2027 ("Break Date"),
provided that: (a) Tenant has given Landlord not less than twelve (12) months prior
written notice; (b) Tenant is not in material breach of any obligation under this
Lease at the Break Date; and (c) Tenant has paid a break penalty equivalent to
six (6) months rent at the then-prevailing rate. For the avoidance of doubt,
any outstanding dilapidations liability shall not be waived upon exercise of
the break option.

4. RENT
Tenant shall pay to Landlord an annual base rent of EUR 216,000 (Two Hundred and
Sixteen Thousand Euros), payable quarterly in advance on the first day of each
quarter. Rent for any partial quarter shall be apportioned on a daily basis.

5. RENT REVIEW
The annual rent shall be subject to review on 1 April 2026 and on the Expiry Date.
Each review shall be to the higher of: (a) the passing rent; or (b) the open market
rental value of the Premises as agreed between the parties or, failing agreement,
determined by an independent surveyor appointed by RICS. Tenant hereby waives any
right to a downward review.

6. RENT ESCALATION
Notwithstanding Clause 5, with effect from 1 April 2025, the annual rent shall
increase by a fixed amount of 3% per annum compounded.

7. SECURITY DEPOSIT
Tenant shall provide a security deposit of EUR 54,000 (equivalent to three months
rent) upon execution of this Lease. The deposit shall be held by Landlord in a
separate client account and returned to Tenant within 60 days of expiry, subject
to deduction for any outstanding obligations.

8. PERMITTED USE
The Premises shall be used solely for the purposes of warehousing, logistics
operations, and ancillary office use. Any change of use requires prior written
consent of Landlord, which shall not be unreasonably withheld.

9. ASSIGNMENT AND SUBLETTING
Tenant shall not assign, sublet, or otherwise transfer its interest in this Lease
without the prior written consent of Landlord. Landlord may withhold consent in
its absolute discretion where the proposed assignee has a net worth less than
three times the annual rent. Any permitted assignment shall not release Tenant
from its obligations under this Lease.

10. SERVICE CHARGE
In addition to rent, Tenant shall pay a service charge contribution currently
estimated at EUR 18,000 per annum (subject to annual reconciliation). The service
charge covers maintenance of common areas, building insurance, and property
management fees.

11. TENANT OBLIGATIONS
Tenant shall: (a) keep the Premises in good repair and condition throughout the
term; (b) comply with all applicable laws and regulations; (c) not make any
structural alterations without Landlord consent; (d) maintain public liability
insurance of not less than EUR 5,000,000.

12. LANDLORD OBLIGATIONS
Landlord shall: (a) maintain the structure and exterior of the building; (b) ensure
the Premises have quiet enjoyment; (c) maintain common areas in good order.
```

---

## Sample Output

The following is the actual JSON output produced by the workflow when run against the
sample input above.

```json
{
  "meta": {
    "processed_at": "2026-09-19T09:15:00.000Z",
    "model": "gpt-4o",
    "workflow_version": "1.0.0",
    "disclaimer": "AI-generated draft. Every field must be reviewed and verified by a qualified lawyer before use in any legal or financial decision."
  },
  "summary": {
    "total_flagged_clauses": 3,
    "high_risk_clauses": 1,
    "medium_risk_clauses": 2,
    "low_risk_clauses": 0,
    "review_recommendation": "PRIORITY REVIEW REQUIRED — high risk clauses identified"
  },
  "extracted_fields": {
    "tenant_name": "Techflow Logistics GmbH",
    "landlord_name": "Meridian Property Holdings S.L.",
    "property_address": "Polígono Industrial Norte, Nave 12, 08040 Barcelona, Spain",
    "lease_commencement_date": "2024-04-01",
    "lease_expiry_date": "2029-03-31",
    "break_option_dates": [
      {
        "date": "2027-03-31",
        "notice_required": "12 months prior written notice",
        "conditions": [
          "Tenant not in material breach",
          "Break penalty of 6 months rent payable",
          "Dilapidations liability not waived"
        ]
      }
    ],
    "rent_amount": "EUR 216,000 per annum, payable quarterly in advance",
    "rent_review_mechanism": "Open market rental value review on 1 April 2026 and expiry date; upward only — tenant has waived right to downward review",
    "rent_escalation_schedule": [
      {
        "effective_date": "2025-04-01",
        "increase": "3% per annum compounded"
      }
    ],
    "security_deposit": "EUR 54,000 (3 months rent); held in separate client account; returned within 60 days of expiry subject to deductions",
    "permitted_use": "Warehousing, logistics operations, and ancillary office use only; change of use requires prior written Landlord consent",
    "assignment_rights": "Assignment and subletting require prior written Landlord consent; Landlord may withhold consent in absolute discretion where assignee net worth is less than 3x annual rent; assignment does not release Tenant from obligations",
    "tenant_break_conditions": [
      "12 months prior written notice",
      "No material breach at Break Date",
      "Break penalty of 6 months rent at then-prevailing rate",
      "Dilapidations liability survives break"
    ],
    "service_charge": "EUR 18,000 per annum estimated; subject to annual reconciliation; covers common area maintenance, building insurance, and property management fees",
    "key_tenant_obligations": [
      "Keep Premises in good repair throughout term",
      "Comply with all applicable laws and regulations",
      "No structural alterations without Landlord consent",
      "Maintain public liability insurance of minimum EUR 5,000,000"
    ],
    "key_landlord_obligations": [
      "Maintain structure and exterior of building",
      "Ensure quiet enjoyment",
      "Maintain common areas in good order"
    ]
  },
  "flagged_clauses": [
    {
      "clause_type": "Break condition",
      "risk_level": "high",
      "quoted_text": "any outstanding dilapidations liability shall not be waived upon exercise of the break option",
      "plain_language_explanation": "Standard break options typically include a clean break from dilapidations liability. This clause explicitly preserves Landlord's right to pursue dilapidations claims even after the break is exercised, which is non-standard and creates significant financial exposure that is difficult to quantify at break date.",
      "recommended_action": "Negotiate removal or cap dilapidations liability. Escalate to senior counsel before accepting."
    },
    {
      "clause_type": "Rent review",
      "risk_level": "medium",
      "quoted_text": "Tenant hereby waives any right to a downward review",
      "plain_language_explanation": "Upward-only rent review clauses are common in some markets but are increasingly challenged under EU consumer protection frameworks and may be unfavourable in a declining market. The explicit waiver of downward review rights should be noted and may be negotiable.",
      "recommended_action": "Note and flag to acquisition team for inclusion in deal model assumptions. Attempt to negotiate removal of upward-only restriction."
    },
    {
      "clause_type": "Assignment restriction",
      "risk_level": "medium",
      "quoted_text": "Landlord may withhold consent in its absolute discretion where the proposed assignee has a net worth less than three times the annual rent",
      "plain_language_explanation": "The landlord's absolute discretion to withhold assignment consent based on net worth creates a restrictive exit mechanism. Combined with the non-release of original tenant obligations on assignment, this significantly limits the tenant's ability to dispose of the lease if circumstances change.",
      "recommended_action": "Seek to replace 'absolute discretion' with 'not to be unreasonably withheld'. Clarify whether original tenant guarantee survives assignment."
    }
  ]
}
```

---

## What the POC Proves

1. **Extraction works:** All 16 standard fields are correctly extracted from unstructured
   legal text. Dates are normalised to ISO format. Arrays are correctly structured.
   Null fields return null rather than hallucinated values.

2. **Flagging works:** The model identifies genuinely non-standard clauses (dilapidations
   survival on break, upward-only review waiver, absolute assignment discretion) and
   distinguishes them from standard provisions (basic tenant repair obligations, standard
   deposit terms). Each flag includes a source quote, plain-language explanation, and
   recommended action.

3. **Transparency is built in:** Every flagged clause quotes the exact text from the
   document. The lawyer can verify every extraction against the source in seconds.
   The disclaimer is present on every output.

4. **The human stays in the loop:** The workflow produces a draft for review, not a
   decision. No output enters any financial model without a lawyer reviewing and
   approving it first.

## What the POC Does Not Prove

- Accuracy at scale across diverse lease formats (tested on 5 synthetic cases only)
- Performance on scanned or poorly OCR'd documents
- Handling of cross-referenced multi-part leases with amendments
- Integration with a document management system or deal portal
- Production security, access control, or audit logging

These are addressed in the Round 2 MVP and pilot phase.

---

## How to Import and Run

1. Open n8n cloud at https://app.n8n.cloud
2. Click **New Workflow** → **Import from file**
3. Upload `workflow.json`
4. Open the **Extract Lease Fields** and **Flag Unusual Clauses** nodes and add your
   OpenAI API key under Credentials
5. Click **Activate** to enable the webhook
6. Copy the webhook URL shown in the Webhook node
7. Send a POST request with `{ "lease_text": "..." }` to that URL
8. The structured JSON response is returned immediately

**Test with the sample input:** Paste the lease text from the Sample Input section above
into the `lease_text` field to reproduce the Sample Output.
