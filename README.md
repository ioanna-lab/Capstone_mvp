# AI Lease & Due Diligence Review Assistant — Portugal
**Ironhack AI Consulting Programme · Capstone Project**
**Student:** Ioanna Renta · GitHub: ioannarenta
**Cohort:** October 2026

---

## What This Is

An AI-powered commercial lease review assistant localised for the Portuguese
market. The system extracts structured data from lease PDFs, flags non-standard
clauses against Portuguese law (NRAU), validates the extraction using a second
AI model (Claude Haiku), and presents results in a web UI with a mandatory
lawyer sign-off workflow.

---

## Repository Structure

```
Capstone_mvp/
├── README.md                          ← this file
├── project_overview.md                ← full project summary, start here
├── roi_risk_assessment.md             ← 12/36-month ROI, risk matrix (20 pts)
├── strategic_plan.md                  ← POC → Pilot → Full deployment (10 pts)
├── use_case_definition.md             ← business problem, stakeholders (15 pts)
│
├── compliance/
│   ├── eu_ai_act_compliance.md        ← Limited Risk classification (20 pts)
│   └── gdpr_documentation.md         ← data flows, DPIA, transfers (10 pts)
│
├── evaluation/
│   ├── eval_plan.md                        ← from Round 1
│   ├── langsmith.md                        ← LangSmith dataset + traces
│   ├── langsmith-examples.png              ← LangSmith dataset screenshot
│   ├── stress_test.md                      ← stress test + determinism docs
│   ├── stress_test_results.png             ← stress test screenshot
│   ├── determinism_results.png             ← determinism check screenshot
│   ├── acquisition_proposal_test.md        ← proposal generator test results
│   └── acquisition_proposal_results.png   ← proposal screenshot
│
├── feedback/
│   └── round1_decision.md            ← teaching staff feedback + decision
│
├── poc/
│   ├── poc_workflow.json              ← n8n workflow (import-ready)
│   └── poc_documentation.md          ← tools, steps, limits vs production
│
└── mvp/                               ← working Python application (15 pts)
    ├── app.py                         ← Streamlit UI (5 tabs)
    ├── extractor.py                   ← GPT-4o extraction pipeline
    ├── validator.py                   ← Claude Haiku validation layer
    ├── rag.py                         ← Chroma RAG over uploaded leases
    ├── prompts.py                     ← all LLM prompts with PT law context
    ├── portugal_law.py                ← NRAU legal context + model pricing
    ├── database.py                    ← Supabase persistence
    ├── notion_sync.py                 ← Notion integration
    ├── notifier.py                    ← Gmail email notification
    ├── proposal.py                    ← acquisition proposal generator
    ├── stress_test.py                 ← parallel stress test + determinism
    ├── utils.py                       ← PDF extraction, JSON parsing
    ├── generate_corpus.py             ← generates 200 synthetic PT leases
    ├── create_langsmith_eval.py       ← creates LangSmith evaluation dataset
    ├── check_models.py                ← checks available OpenAI models
    ├── schema.sql                     ← Supabase PostgreSQL schema
    ├── requirements.txt               ← Python dependencies
    ├── Procfile                       ← Render deployment config
    ├── runtime.txt                    ← Python version for Render
    ├── .env.example                   ← environment variable template
    ├── mvp_documentation.md           ← quick start, architecture, limits
    └── data/leases/synthetic/
        ├── PT_0001_*.pdf              ← 200 synthetic Portuguese lease PDFs
        └── ground_truth.csv           ← known correct values for all 200 leases
```

---

## Quick Start

```bash
cd mvp
pip install -r requirements.txt
cp .env.example .env
# fill in all API keys in .env
python3 generate_corpus.py      # generate 200 synthetic leases (first time only)
streamlit run app.py
```

See `mvp/mvp_documentation.md` for full setup instructions.

---

## Deployment (Render)

The app runs standalone on Render without any local server needed.

1. Push this repo to GitHub
2. Go to render.com → New Web Service → connect repo
3. Root directory: `mvp`
4. Build command: `pip install -r requirements.txt`
5. Start command: as in `Procfile`
6. Add all `.env` variables in Render's Environment tab
7. Deploy

---

## Round 1 → Round 2 Evolution

| Round 1 | Round 2 |
|---|---|
| n8n POC, 5 synthetic leases | Full Python MVP, 200 Portuguese leases |
| Generic commercial lease | Localised for Portugal (NRAU, NIF, Finanças) |
| Quoted text only | Page number + clause reference on every field |
| Single model (GPT-4o-mini) | 7 models incl. o1, o3, o3-mini, o1-pro |
| No validation | Claude Haiku cross-model validation |
| No persistence | Supabase PostgreSQL + Notion sync |
| No feedback loop | Lawyer corrections → few-shot examples |
| Manual eval (5 cases) | LangSmith dataset + live traces |

---

## Compliance Summary

- **EU AI Act:** Limited Risk — transparency obligations only (Art. 50)
- **GDPR:** Legitimate interest, Supabase EU-hosted, OpenAI zero data retention
- **Portuguese law:** NRAU Lei 6/2006, Código Civil Arts 1022-1120

---

## Stress Testing & Determinism

The system includes a full stress test suite to validate performance at scale.

**Run 10 leases in parallel from the terminal:**
```bash
cd mvp
python3 run_stress_test.py --leases 10 --threads 4
```

**Run determinism check (3 identical runs, confirm same output):**
```bash
# Via the UI: Stress Test tab → Determinism check section
# Or via terminal — see evaluation/stress_test.md
```

**What the stress test proves:**
- The system processes multiple leases simultaneously (not sequentially)
- 4 threads delivers ~4x speedup over sequential processing
- Temperature=0 ensures identical output on repeated runs of the same document
- Cost is ~€0.025 per lease regardless of thread count

See `evaluation/stress_test.md` for full documentation, results interpretation,
and production scaling estimates.

---

## Contact

Ioanna Renta · ioanna@irenta.io · linkedin.com/in/ioannarenta
