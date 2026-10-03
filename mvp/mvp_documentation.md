# MVP Documentation
**AI Lease & Due Diligence Review Assistant — Portugal**
**Capstone Round 2 · Ironhack AI Consulting · Ioanna Renta**

---

## What This Is

A working web application for AI-assisted commercial lease review, localised for
the Portuguese market. Built with Python, Streamlit, LangChain, and multiple AI
models. Runs standalone — no local Python environment needed if deployed to
Streamlit Cloud or Railway.

---

## Quick Start (Local)

```bash
# 1. Clone / download the mvp/ folder
cd mvp

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy .env.example to .env and fill in your keys
cp .env.example .env
# Edit .env with your API keys

# 4. Generate the synthetic lease corpus (first time only)
python3 generate_corpus.py

# 5. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`

---

## Required API Keys (.env)

```
OPENAI_API_KEY=sk-...          # OpenAI — required for extraction
ANTHROPIC_API_KEY=sk-ant-...   # Anthropic — required for validation
SUPABASE_URL=https://...       # Supabase project URL
SUPABASE_KEY=sb_secret_...     # Supabase secret key
NOTION_TOKEN=secret_...        # Notion integration token
NOTION_DATABASE_ID=...         # 32-char Notion database ID
EMAIL_SENDER=you@gmail.com     # Gmail address for notifications
EMAIL_PASSWORD=...             # Gmail app password (16 chars, no spaces)
LANGCHAIN_TRACING_V2=false     # Set to true for LangSmith tracing
LANGCHAIN_API_KEY=lsv2_...     # LangSmith key (only needed if tracing=true)
LANGCHAIN_PROJECT=lease-review-mvp
```

---

## Repository Structure

```
mvp/
├── app.py                  # Main Streamlit application (5 tabs)
├── extractor.py            # GPT-4o extraction pipeline
├── validator.py            # Claude Haiku validation layer
├── rag.py                  # Chroma RAG over uploaded leases
├── prompts.py              # All LLM prompts with PT law context
├── portugal_law.py         # Portuguese legal context + model pricing
├── database.py             # Supabase client (all persistence)
├── notion_sync.py          # Notion integration
├── notifier.py             # Gmail SMTP email notification
├── proposal.py             # Acquisition proposal generator
├── stress_test.py          # Parallel stress test + determinism check
├── utils.py                # PDF extraction, JSON parsing utilities
├── generate_corpus.py      # Generator for 200 synthetic PT leases
├── check_models.py         # Check available OpenAI models
├── schema.sql              # Supabase PostgreSQL schema
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── mvp_documentation.md    # This file
├── data/
│   └── leases/
│       └── synthetic/
│           ├── PT_0001_office_Porto.pdf  ... (200 PDFs)
│           └── ground_truth.csv
└── results/                # Auto-saved JSON extraction results
```

---

## Application Tabs

### Tab 1 — Extract & Review
The core workflow. Upload a lease PDF, select extraction model, enter email,
click Run AI extraction. GPT-4o extracts 16 standard + 11 Portugal-specific fields
with page and clause citations. Claude Haiku validates the extraction. Results
displayed with correction mechanism and mandatory lawyer sign-off.

### Tab 2 — Query Portfolio
RAG-based question answering across all uploaded leases. Ask any question in
plain English. The system retrieves relevant passages and cites which lease each
answer comes from.

### Tab 3 — Acquisition Proposal
Aggregates all reviewed leases for a property and generates a structured BUY/
REVIEW/PASS recommendation with Portuguese tax calculations (IMT 6.5%, stamp
duty 0.8%), WALE, gross yield, and risk score.

### Tab 4 — Review History
All past lease reviews stored in Supabase. Cost tracking per model and call type.

### Tab 5 — Stress Test
Parallel processing of all uploaded leases (configurable thread count). Measures
throughput, thread usage, and cost. Determinism check runs the same lease 3 times
and verifies identical output (temperature=0).

---

## Supported OpenAI Models

| Model | Best for |
|---|---|
| gpt-4o-2024-11-20 | Standard extraction (default, recommended) |
| o1 | Complex clause extraction, high accuracy |
| o3 | Latest reasoning model |
| o3-mini | Fast reasoning, good for stress testing |
| o1-pro | Maximum accuracy (slowest, most expensive) |
| gpt-4o | Standard fallback |
| gpt-4o-mini | Fast, cheapest, RAG queries |

---

## Portuguese Law Grounding

The system is localised for Portugal via `portugal_law.py` which contains:
- Full NRAU legal context (Lei n.º 6/2006 and amendments)
- 10 specific high-risk flags for Portuguese commercial leases
- Portuguese terminology mappings (SENHORIO, ARRENDATÁRIO, etc.)
- Model pricing table for cost tracking

---

## Error Handling

- PDF extraction failure: caught, returns empty string, user sees "upload failed"
- OpenAI API error: caught in extractor.py, returns error in result summary
- Claude API error: caught in validator.py, returns 78% fallback score with note
- Supabase save failure: caught, displays warning, app continues
- Notion sync failure: caught, displays warning, app continues
- Email failure: caught silently, app continues

---

## Cost

Typical cost per lease: €0.02–0.04 (gpt-4o extraction + Claude validation)
Typical cost per lease with o1: €0.15–0.30 (reasoning model, higher token count)
Typical stress test (5 leases, 3 threads): €0.10–0.20
All costs tracked in Supabase cost_history table and visible in Review History tab.

---

## Known Limitations

- Scanned PDFs (no text layer) return empty extraction — OCR not yet implemented
- Complex multi-part lease amendments may confuse field boundaries
- Claude agreement score is calibrated for confidence, not exact string matching
- 200-lease corpus is synthetic — pilot with real leases required before production
- LangSmith tracing requires a valid API key with the correct project permissions
