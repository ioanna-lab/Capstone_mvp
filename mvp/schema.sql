-- ── Lease Review Assistant — Portugal
-- ── Supabase PostgreSQL Schema
-- ── Run this entire block in the Supabase SQL Editor

-- ── 1. lease_reviews ────────────────────────────────────────────────────────
-- One row per processed lease document.
-- Stores both the GPT-4o extraction and the Claude validation result.

CREATE TABLE IF NOT EXISTS lease_reviews (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at              TIMESTAMPTZ DEFAULT NOW(),

    -- document metadata
    filename                TEXT NOT NULL,
    reviewer_email          TEXT,
    market                  TEXT DEFAULT 'PT',           -- Portugal by default

    -- extracted fields (GPT-4o)
    tenant_name             TEXT,
    landlord_name           TEXT,
    property_address        TEXT,
    lease_commencement_date DATE,
    lease_expiry_date       DATE,
    break_option_dates      JSONB,                       -- array of {date, conditions}
    rent_amount             TEXT,
    rent_review_mechanism   TEXT,
    rent_escalation_schedule JSONB,
    security_deposit        TEXT,
    permitted_use           TEXT,
    assignment_rights       TEXT,
    tenant_break_conditions JSONB,
    service_charge          TEXT,
    key_tenant_obligations  JSONB,
    key_landlord_obligations JSONB,

    -- portugal-specific fields
    nif_tenant              TEXT,                        -- Portuguese tax ID
    nif_landlord            TEXT,
    finanças_registration   TEXT,                        -- AT lease registration number
    stamp_duty_rate         NUMERIC(5,2),                -- % applicable
    imt_applicable          BOOLEAN DEFAULT FALSE,
    condominio_charges      TEXT,
    obras_consent_required  BOOLEAN,
    mandatory_notice_period INTEGER,                     -- days under NRAU

    -- flagged clauses
    flagged_clauses         JSONB,                       -- array of {type, risk, quote, explanation, action}
    total_flagged           INTEGER DEFAULT 0,
    high_risk_count         INTEGER DEFAULT 0,
    medium_risk_count       INTEGER DEFAULT 0,

    -- review summary
    review_recommendation   TEXT,
    extraction_model        TEXT DEFAULT 'gpt-4o',

    -- claude validation
    validation_model        TEXT DEFAULT 'claude-haiku-4-5-20251001',
    validation_result       JSONB,                       -- {agreement_score, disagreements, confidence}
    validation_passed       BOOLEAN,
    confidence_score        NUMERIC(4,2),                -- 0.00 to 1.00

    -- raw outputs for debugging
    raw_extraction          JSONB,
    raw_validation          JSONB,

    -- cost tracking
    extraction_tokens_in    INTEGER DEFAULT 0,
    extraction_tokens_out   INTEGER DEFAULT 0,
    validation_tokens_in    INTEGER DEFAULT 0,
    validation_tokens_out   INTEGER DEFAULT 0,
    total_cost_eur          NUMERIC(8,4) DEFAULT 0
);

-- ── 2. evaluation_history ───────────────────────────────────────────────────
-- One row per cross-model evaluation run.
-- Records how GPT-4o and Claude compared on the same document.

CREATE TABLE IF NOT EXISTS evaluation_history (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    lease_review_id     UUID REFERENCES lease_reviews(id) ON DELETE CASCADE,

    -- models compared
    model_a             TEXT NOT NULL,                   -- e.g. gpt-4o
    model_b             TEXT NOT NULL,                   -- e.g. claude-haiku-4-5-20251001

    -- field-level agreement
    fields_agreed       INTEGER DEFAULT 0,
    fields_disagreed    INTEGER DEFAULT 0,
    agreement_rate      NUMERIC(5,2),                    -- percentage

    -- disagreement detail
    disagreements       JSONB,                           -- [{field, model_a_value, model_b_value}]

    -- flagging comparison
    flags_agreed        INTEGER DEFAULT 0,
    flags_only_in_a     INTEGER DEFAULT 0,
    flags_only_in_b     INTEGER DEFAULT 0,

    -- overall verdict
    evaluation_passed   BOOLEAN,
    notes               TEXT
);

-- ── 3. cost_history ─────────────────────────────────────────────────────────
-- One row per API call. Granular cost tracking.

CREATE TABLE IF NOT EXISTS cost_history (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    lease_review_id UUID REFERENCES lease_reviews(id) ON DELETE CASCADE,

    model           TEXT NOT NULL,
    call_type       TEXT NOT NULL,      -- extraction | flagging | validation | rag_query | proposal
    tokens_in       INTEGER DEFAULT 0,
    tokens_out      INTEGER DEFAULT 0,
    cost_eur        NUMERIC(8,6) DEFAULT 0,

    -- pricing snapshot (so history stays accurate if prices change)
    price_per_1k_in  NUMERIC(8,6),
    price_per_1k_out NUMERIC(8,6)
);

-- ── 4. acquisition_proposals ────────────────────────────────────────────────
-- One row per property under consideration.
-- Aggregates multiple lease reviews into a buy/hold/pass recommendation.

CREATE TABLE IF NOT EXISTS acquisition_proposals (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW(),

    -- property
    property_name           TEXT NOT NULL,
    property_address        TEXT,
    property_type           TEXT,                        -- office | retail | warehouse | mixed
    asking_price_eur        NUMERIC(14,2),
    district                TEXT,                        -- Lisboa | Porto | Algarve etc.

    -- lease summary (calculated from linked reviews)
    total_annual_rent_eur   NUMERIC(14,2),
    number_of_leases        INTEGER DEFAULT 0,
    wale_years              NUMERIC(5,2),                -- weighted average lease expiry
    earliest_break_date     DATE,
    vacancy_rate_pct        NUMERIC(5,2),

    -- risk
    composite_risk_score    NUMERIC(4,2),                -- 0 (low) to 10 (high)
    high_risk_leases        INTEGER DEFAULT 0,
    total_flags             INTEGER DEFAULT 0,

    -- financials
    gross_yield_pct         NUMERIC(5,2),
    estimated_imt_eur       NUMERIC(12,2),
    estimated_stamp_duty_eur NUMERIC(12,2),
    estimated_total_tax_eur  NUMERIC(12,2),

    -- recommendation
    recommendation          TEXT,                        -- BUY | REVIEW | PASS
    recommendation_reasons  JSONB,                       -- array of strings
    confidence_level        TEXT,                        -- HIGH | MEDIUM | LOW

    -- linked reviews
    lease_review_ids        UUID[],

    -- notion sync
    notion_page_id          TEXT,
    notion_synced_at        TIMESTAMPTZ,

    -- total cost of this analysis
    total_analysis_cost_eur NUMERIC(8,4) DEFAULT 0
);

-- ── 5. rag_documents ────────────────────────────────────────────────────────
-- Metadata for documents loaded into the RAG corpus.
-- The actual vectors live in Chroma; this table tracks what is in there.

CREATE TABLE IF NOT EXISTS rag_documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ DEFAULT NOW(),

    filename        TEXT NOT NULL,
    document_type   TEXT NOT NULL,   -- law | template | validated_lease | regulation | guidance
    jurisdiction    TEXT DEFAULT 'PT',
    language        TEXT DEFAULT 'pt',
    description     TEXT,
    source_url      TEXT,
    chunk_count     INTEGER DEFAULT 0,
    embedded_at     TIMESTAMPTZ,
    is_active       BOOLEAN DEFAULT TRUE
);

-- ── indexes ──────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_lease_reviews_created    ON lease_reviews(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lease_reviews_market     ON lease_reviews(market);
CREATE INDEX IF NOT EXISTS idx_cost_history_review      ON cost_history(lease_review_id);
CREATE INDEX IF NOT EXISTS idx_eval_history_review      ON evaluation_history(lease_review_id);
CREATE INDEX IF NOT EXISTS idx_proposals_recommendation ON acquisition_proposals(recommendation);

-- ── done ─────────────────────────────────────────────────────────────────────
-- 5 tables created:
--   lease_reviews, evaluation_history, cost_history,
--   acquisition_proposals, rag_documents
