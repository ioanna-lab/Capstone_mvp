# GDPR Documentation
**AI Lease & Due Diligence Review Assistant — Portugal**
**Capstone Round 2 · Ironhack AI Consulting · Ioanna Renta**
**Reference:** Regulation (EU) 2016/679 (GDPR)

---

## 1. Data Flow Map

```
[Lawyer uploads PDF]
        │
        ▼
[Streamlit app — local or Railway server, EU]
        │  ← lease text extracted from PDF (PyPDF)
        ▼
[OpenAI API — GPT-4o extraction]
        │  ← lease text sent as prompt (transient, not stored by OpenAI under zero-retention)
        ▼
[Anthropic API — Claude Haiku validation]
        │  ← extraction result sent for validation (transient)
        ▼
[Supabase — PostgreSQL, eu-west-1 Ireland]
        │  ← structured extraction result stored (persistent)
        ▼
[Notion API — workspace in EU data region]
        │  ← summary page created (persistent)
        ▼
[Gmail SMTP — reviewer email notification]
        │  ← summary + JSON attachment sent
        ▼
[Reviewer (lawyer) — reads, corrects, signs off]
        │  ← corrections saved to Supabase
        ▼
[Local disk — results/ folder]
           ← JSON file saved with timestamp
```

**Personal data present in lease documents:**
- Individual guarantors (name, address, NIF)
- Sole-trader tenants (name, NIF, personal address)
- Contact persons named in lease (rare in commercial leases)
- Reviewer email address

**Corporate data (not personal data under GDPR):**
- Company names, registered addresses, company NIF numbers
- Corporate landlord and tenant details
- Property addresses
- Financial terms (rents, deposits)

---

## 2. Processing Activities Register

| Activity | Purpose | Legal basis | Data categories | Retention | Recipients |
|---|---|---|---|---|---|
| Lease text extraction | Extract structured fields for due diligence | Legitimate interest (Art. 6(1)(f)) — commercial due diligence for property acquisition | Names, addresses, NIF (where individual), financial terms | Duration of due diligence process + 5 years (statutory) | OpenAI (processor), Anthropic (processor) |
| Extraction result storage | Maintain audit trail of AI-assisted reviews | Legitimate interest | Extracted fields, flags, reviewer email | 5 years from review date | Supabase (processor, EU) |
| Notion sync | Portfolio management and team collaboration | Legitimate interest | Summary fields, risk level, recommendation | Until manually deleted | Notion (processor) |
| Email notification | Notify reviewer of results requiring attention | Legitimate interest / performance of contract | Reviewer email, extraction summary | Not stored by system | Gmail / Google (processor) |
| Lawyer corrections | Improve future extraction accuracy (feedback loop) | Legitimate interest | Corrected field values (not typically personal) | 3 years | Supabase (processor, EU) |

---

## 3. Short DPIA — Highest-Risk Processing Activity

**Processing activity:** Sending commercial lease text to OpenAI API for extraction

**Why this is the highest-risk activity:**
- Lease documents may contain personal data (individual guarantor NIF, personal
  addresses)
- Data leaves the EU (OpenAI processes in the US)
- Volume: up to 200–300 leases per year
- Sensitivity: commercially confidential deal information

**Necessity and proportionality:**
The processing is necessary to achieve the stated purpose (automated extraction)
and proportionate because:
- Only the minimum required text is sent (truncated to 12,000 tokens)
- No more personal data is sent than is in the original document
- The alternative (fully manual abstraction) provides no better privacy protection
  since lawyers read the full document anyway

**Risks identified:**
1. Data breach at OpenAI — risk level: LOW. OpenAI's API uses TLS in transit;
   under zero data retention option, prompts are not stored after the API call
2. Re-identification — risk level: LOW. Individual guarantors are rarely named in
   commercial leases; where they are, the data is already held by the client
3. Cross-border transfer — risk level: MEDIUM. OpenAI processes in the US.
   Mitigation: Standard Contractual Clauses (SCCs) in OpenAI's DPA; zero data
   retention option enabled via API

**Mitigation measures:**
- Enable OpenAI zero data retention: add `"store": false` to API calls in production
- Sign DPA with OpenAI before pilot
- Sign DPA with Anthropic before pilot
- Instruct lawyers not to upload leases containing sensitive personal data of
  natural persons who have not been informed of AI processing

**Residual risk:** LOW — acceptable for legitimate commercial due diligence purpose

**DPIA conclusion:** Processing can proceed with stated mitigations in place.

---

## 4. Data Subject Rights Support

| Right | How supported |
|---|---|
| Right to access (Art. 15) | Extraction results stored in Supabase — retrievable by reviewer on request; JSON download available in app |
| Right to erasure (Art. 17) | Supabase records can be deleted by authorised user; Notion page can be deleted; results/ folder files can be deleted |
| Right to rectification (Art. 16) | Field correction mechanism in app allows any extracted value to be corrected and saved |
| Right to object (Art. 21) | Any individual named in a lease can object to processing; client company must assess and delete if no overriding legitimate interest |
| Right to portability (Art. 20) | JSON download available for all extraction results |

**Note:** In practice, most data subjects in commercial leases are corporate
entities (companies), not natural persons. GDPR rights apply to natural persons
only. The most likely natural persons are individual guarantors.

---

## 5. Third-Party and Cross-Border Transfers

| Provider | Location | Transfer mechanism | Personal data shared |
|---|---|---|---|
| OpenAI | USA | Standard Contractual Clauses (SCCs) | Lease text (may contain individual NIF, address) |
| Anthropic | USA | Standard Contractual Clauses (SCCs) | Extracted fields summary |
| Supabase | EU (Ireland, eu-west-1) | No transfer — EU-hosted | All structured extraction data |
| Notion | EU data region available | EU data region selected | Summary fields |
| Google (Gmail) | USA | SCCs | Reviewer email, summary text |

**Action required before production deployment:**
1. Sign OpenAI Data Processing Agreement — enable zero data retention
2. Sign Anthropic Data Processing Agreement
3. Confirm Notion workspace is in EU data region
4. Update privacy notice to inform data subjects of AI processing in due diligence
5. Conduct annual review of SCCs with each US provider
