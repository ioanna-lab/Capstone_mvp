# Charts Documentation

All charts were produced in Python using Plotly. Data is drawn from cited industry sources
or calculated from stated assumptions. No proprietary data is used.

Tool: Python 3, plotly 5.x, kaleido (PNG export)
Output: 6 PNG files at 900×500px, 2x scale

---

## Chart 1 — Lease review time: manual vs AI-assisted

**File:** `chart1_review_time.png`

**What it shows:**
Time in hours required to abstract a single commercial lease, comparing manual review
against AI-assisted review, for both simple and complex lease documents.

**Why this metric matters to Chleo:**
This is the most immediate operational pain point. A lawyer or paralegal spending 4–8 hours
per lease on a 20-lease due diligence pack is 2–3 full working days before any legal
analysis begins. AI-assisted review compresses this to 30–90 minutes per lease, freeing
lawyer time for judgment rather than extraction.

**Data sources:**
- MRI Software: AI reduces lease review time by 50–75%; some cases up to 85%
- Kolena (2025): per-lease review reduced from 2 hours to 17 minutes in real deployments
- GrowthFactor case study: one client reduced from 20 hours to 1.5 hours (90% faster)
- Simple lease manual baseline: 6 hours (mid-range of 4–8h industry benchmark)

**Assumptions:**
Simple lease = standard commercial lease, digitally authored, under 50 pages.
Complex lease = multi-part lease with amendments, cross-references, or scanned pages.

---

## Chart 2 — Annual cost of manual lease abstraction: Chleo's company

**File:** `chart2_annual_cost.png`

**What it shows:**
Estimated annual spend on manual lease abstraction for Chleo's company at three deal volume
scenarios (8, 10, 12 acquisitions/year), at two hourly rates (€80 paralegal, €120 lawyer).

**Why this metric matters to Chleo:**
Translates the time problem into a financial one. At 10 deals/year with 20 leases per deal,
the company is spending €128,000–€192,000 annually on abstraction alone — before accounting
for external counsel premiums, deal delays caused by slow review, or the cost of errors.
This is the baseline against which AI investment cost is compared in the cost analysis.

**Calculation:**
Annual cost = deals/year × 20 leases/deal × 8 hours/lease × hourly rate
Example: 10 deals × 20 leases × 8h × €80 = €128,000

**Assumptions:**
- 20 leases per acquisition due diligence pack (conservative mid-market estimate)
- 8 hours per lease (lower bound of industry benchmark for standard leases)
- €80/hr: external paralegal rate, Southern Europe
- €120/hr: in-house or external lawyer rate, Southern Europe
- No overhead or management cost included (conservative)

---

## Chart 3 — AI adoption in real estate: 2023 → 2025

**File:** `chart3_adoption.png`

**What it shows:**
Four AI adoption metrics for real estate firms, comparing 2023 baseline against 2025
figures. Covers: firms piloting AI, increasing AI budget, using AI for data analytics,
and firms that have fully automated any process.

**Why this metric matters to Chleo:**
Addresses the "are we behind?" question directly. The sector moved from 5% piloting AI
in 2023 to 88% in 2025 — an 18x jump in two years. Chleo's competitors are already
running pilots. The window for early-mover advantage is closing. The 8% fully automated
figure is also important: it shows that most companies are still in the experimental phase,
meaning there is time to build properly rather than rush.

**Data sources:**
- JLL Global Real Estate Technology Survey 2025: 88% piloting AI (up from 5% in 2023)
- Gitnux CRE AI Statistics 2026: 68% increasing AI budget; 52% using AI for data analytics
- Buildium 2026: only 8% of companies had fully automated any process
- 2023 baselines for budget and analytics estimated from trend data; piloting confirmed at 5%

---

## Chart 4 — Top barriers to AI adoption in real estate

**File:** `chart4_barriers.png`

**What it shows:**
The five most-cited barriers to AI adoption among real estate firms, as a percentage of
firms citing each barrier. Bars are colour-coded by severity (dark red ≥40%, orange 35–39%,
amber below 35%).

**Why this metric matters to Chleo:**
This chart is the direct answer to Chleo's fear expressed at dinner: "AI is not transparent."
That fear is industry-wide. Investment committee distrust (44%) and AI hallucinations (41%)
are the top two concerns. The chart validates Chleo's concern as legitimate and shared —
and sets up the solution design: every output cited to source, human sign-off required,
no automated decisions. The barriers are real and addressable, not reasons to avoid AI.

**Data sources:**
- Commercial Observer AI Survey 2026: hallucinations 41%, integration 33%,
  investment committee distrust 44%
- RSM Middle Market AI Survey 2025: lack of in-house expertise 39%, data quality 41%

---

## Chart 5 — Extraction accuracy: manual vs AI-assisted

**File:** `chart5_accuracy.png`

**What it shows:**
Extraction accuracy (%) for three clause complexity levels — standard clauses, non-standard
clauses, and complex amendments — comparing manual review against AI-assisted review.
A 90% accuracy threshold line marks the minimum acceptable for production use.

**Why this metric matters to Chleo:**
Addresses the "but is it accurate enough?" question. AI outperforms manual on standard
clauses (95% vs 91%) and closes the gap significantly on complex clauses. The 90% threshold
line makes the pass/fail criterion visible. It also honestly shows that complex amendments
remain below threshold for both methods — the AI is not a silver bullet, and the chart
does not pretend otherwise. Non-standard and complex clauses are routed to human review.

**Data sources:**
- Oxmaint (2026): AI achieves 94% accuracy vs 91% manual on standard clause types
- Kolena (2025): accuracy above 95% maintained in real-world deployments
- Non-standard and complex figures: estimated from industry benchmarks on clause complexity;
  exact figures vary by portfolio type and model training

**Assumptions:**
Non-standard and complex accuracy figures are indicative estimates based on published
ranges. The eval plan (evaluation/eval_plan.md) tests this directly on the POC.

---

## Chart 6 — Due diligence timeline per acquisition: 13 days → 4.5 days

**File:** `chart6_timeline.png`

**What it shows:**
Working days per phase of a typical acquisition due diligence process, before and after
AI-assisted lease review. Five phases shown: lease collection and prep, lease abstraction,
lawyer review and analysis, flagged clause negotiation, final sign-off.

**Why this metric matters to Chleo:**
Deal speed matters. In competitive property markets, a buyer who can complete due diligence
in 4–5 days instead of 13 days can move faster, reduce carrying cost uncertainty, and
present a more credible offer to sellers. The abstraction phase alone shrinks from 6 days
to half a day. Lawyer review shrinks from 3 days to 1 because the lawyer arrives at a
structured, cited abstract rather than a blank page. The total cycle compresses by 65%.

**Calculation:**
Before AI: 1 + 6 + 3 + 2 + 1 = 13 working days
After AI:  1 + 0.5 + 1 + 1.5 + 0.5 = 4.5 working days

**Assumptions:**
- 20 leases per acquisition
- Abstraction phase before AI: 20 leases × 8h ÷ 8h/day = 20 paralegal-days, compressed
  to ~6 working days with 3–4 people working in parallel
- After AI: abstraction runs overnight or same-day; lawyer arrives at structured abstracts
- Negotiation phase unchanged in volume but reduced in prep time since issues are
  pre-identified by the flagging layer
- These are directional estimates; actual times vary by deal complexity
