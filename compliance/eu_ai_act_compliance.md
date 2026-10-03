# EU AI Act Compliance Documentation
**AI Lease & Due Diligence Review Assistant — Portugal**
**Capstone Round 2 · Ironhack AI Consulting · Ioanna Renta**
**Reference:** Regulation (EU) 2024/1689 (EU AI Act), in force August 2024

---

## 1. Risk Classification

**Classification: LIMITED RISK**

### Step-by-Step Reasoning

**Step 1 — Is this an AI system under the Act?**
Yes. The system uses a machine learning model (GPT-4o) to process input data
(lease PDFs) and produce outputs (structured field extractions, risk flags) that
influence human decisions. It meets the definition of an AI system under Art. 3(1).

**Step 2 — Is this a prohibited practice (Art. 5)?**
No. The system does not manipulate persons, exploit vulnerabilities, perform social
scoring, conduct real-time biometric surveillance, or any other prohibited practice.

**Step 3 — Is this a high-risk AI system (Art. 6, Annex III)?**
This is the critical question. Annex III lists high-risk categories. The most
relevant is:

> *Annex III, point 5(b): AI systems intended to be used for creditworthiness
> assessment or credit scoring, and AI systems intended to be used for life and
> health insurance, including risk assessment.*

**Analysis:** Our system is used in commercial property due diligence, not credit
assessment or insurance. It does not produce a credit score, a lending decision,
or an insurance risk assessment.

> *Annex III, point 6: AI systems intended to be used by competent public
> authorities or Union institutions.*

**Analysis:** Our system is used by a private commercial real estate company, not
a public authority.

**Conclusion on high risk:** The system does not fall under any Annex III category
in its current architecture. **The critical design constraint that maintains this
classification is the mandatory human-in-the-loop: the system produces a draft
for lawyer review, not a final legal or financial decision.**

**Watch point:** If the extraction output were to feed directly and automatically
into a property valuation model or financing application without human review, the
classification would shift toward high risk under Annex III point 5(b). The
human-in-the-loop requirement is therefore a compliance constraint, not just good
practice.

**Step 4 — Does the system interact with natural persons in a way that requires
transparency (Art. 50)?**
The system is used by lawyers and professionals, not by the general public. The
professional users are aware they are using an AI system. Standard transparency
obligations apply: the output is labelled as AI-generated and must not be presented
as a final legal opinion.

**Final classification: LIMITED RISK**

---

## 2. Mandatory Requirements Summary (Limited Risk)

Under Art. 50, limited-risk AI systems must comply with transparency obligations:

| Obligation | How we comply |
|---|---|
| Inform users they are interacting with AI | Every output is labelled "AI-generated draft" — on screen, in email, in saved JSON |
| Do not present AI output as human expert opinion | Disclaimer on every output: "Must be reviewed by a qualified lawyer before use in any legal or financial decision" |
| Allow users to opt out of AI-only interaction | Lawyer sign-off is mandatory — no output can be used without human approval |

No conformity assessment procedure is required for limited-risk systems. No
registration in the EU database is required.

---

## 3. Conformity Assessment Summary

**System name:** AI Lease & Due Diligence Review Assistant
**Version:** Round 2 MVP (October 2026)
**Deployer:** [Client company name — Chleo's company]
**Developer:** Ioanna Renta, Ironhack AI Consulting Programme
**Classification:** Limited risk

**Purpose:** AI-assisted extraction of structured data from commercial lease
documents for use in property acquisition due diligence. Operated exclusively
by qualified lawyers and real estate professionals.

**Intended use:** Process digitally-authored commercial lease PDFs, extract
16 standard + 11 Portugal-specific fields, flag non-standard clauses, and
present results for lawyer review and sign-off.

**Intended users:** Qualified lawyers and real estate paralegals employed by
or contracted to the deploying company. Not intended for use by the general public.

**Known limitations:**
- Accuracy is lower on scanned documents (OCR not yet implemented)
- Accuracy is lower on complex multi-part lease amendments
- System has been tested on synthetic Portuguese leases; pilot validation on
  real leases is planned
- Claude agreement score is indicative, not a definitive accuracy measure

**Human oversight measures:**
- Mandatory lawyer sign-off before any output may be used in a decision
- Every field cites source text (page and clause) for verification
- Field correction mechanism allows lawyers to record and save corrections
- Corrections feed back into future extraction prompts (feedback loop)

**Data protection:** See gdpr_documentation.md

**Incident reporting:** Any extraction error with material financial consequences
must be reported to the AI consulting team within 48 hours for root cause analysis
and prompt remediation.

---

## 4. Technical Documentation Outline

*This is a skeleton ToC as required by the Act for documentation purposes.*

**1. General description**
- 1.1 System purpose and intended use
- 1.2 Intended users and deployment context
- 1.3 Version and change log

**2. System architecture**
- 2.1 Input: PDF text extraction (PyPDF)
- 2.2 Processing: LangChain + GPT-4o extraction pipeline
- 2.3 Validation: Anthropic Claude Haiku cross-check
- 2.4 Storage: Supabase PostgreSQL (EU-hosted)
- 2.5 UI: Streamlit web application
- 2.6 RAG: Chroma vector store with Portuguese law corpus
- 2.7 Integrations: Notion, Gmail SMTP

**3. Training and data**
- 3.1 No custom model training — uses pre-trained GPT-4o and Claude Haiku
- 3.2 Portuguese law context injected via system prompt (portugal_law.py)
- 3.3 Test corpus: 200 synthetic Portuguese commercial leases with ground truth CSV
- 3.4 Few-shot learning from lawyer corrections (feedback loop)

**4. Performance and accuracy**
- 4.1 Accuracy metrics (from LangSmith evaluation)
- 4.2 Known failure modes and mitigations
- 4.3 Cross-model agreement scores

**5. Human oversight**
- 5.1 Mandatory sign-off workflow
- 5.2 Field correction mechanism
- 5.3 Feedback loop design

**6. Risk management**
- 6.1 Risk matrix (see roi_risk_assessment.md)
- 6.2 Monitoring and incident response

**7. Data protection**
- 7.1 See gdpr_documentation.md

**8. Cybersecurity**
- 8.1 API key management (.env, not committed to version control)
- 8.2 Supabase row-level security
- 8.3 No storage of raw lease text at AI provider
