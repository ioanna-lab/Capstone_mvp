"""
Portuguese commercial lease law context.
Injected into extraction and flagging prompts to ground the AI
in actual Portuguese legal obligations rather than generic norms.

Sources:
- NRAU (Lei n.º 6/2006, amended by Lei 31/2012, 79/2014, 43/2017, 13/2019)
- Código Civil, Articles 1022-1120 (arrendamento)
- Portal das Finanças registration rules
- Imposto do Selo (Stamp Duty) — 10% of one month's rent
- IMT (Imposto Municipal sobre Transmissões) — on acquisition only
- DLA Piper RealWorld Portugal 2026
- Global Citizens Solutions Portugal Rental Guide 2026
- MSP Lawyer Portugal Rental Guide 2026
"""

PORTUGAL_LEGAL_CONTEXT = """
PORTUGUESE COMMERCIAL LEASE LAW — KEY OBLIGATIONS AND RULES (2026)

GOVERNING LAW:
- Primary law: NRAU (Novo Regime do Arrendamento Urbano) — Lei n.º 6/2006, as amended
- Civil Code Articles 1022-1120 (general lease provisions)
- Applies to all urban commercial and residential leases in Portugal

MANDATORY CONTRACT REQUIREMENTS (flag absence of any):
- Must be in writing (verbal leases are invalid)
- Must include full legal names and NIF (tax ID) of both parties
- Must specify property description and address
- Must state lease duration and commencement date
- Must state monthly rent amount and payment method
- Must state deposit amount and conditions
- Must state renewal and termination conditions

LEASE REGISTRATION — MANDATORY:
- Landlord must register lease with Portal das Finanças (AT — Autoridade Tributária)
- Registration deadline: by end of month following lease commencement
- Failure to register: landlord faces fines; tenant loses legal protections
- Flag any lease that does not reference Finanças registration

STAMP DUTY (Imposto do Selo):
- Rate: 10% of one month's rent (not annual rent)
- Payable by: landlord (landlord bears this cost by law)
- Triggered by: registration with Portal das Finanças
- Also triggered by: contract amendments or renewals
- Flag if lease incorrectly attributes stamp duty to tenant

LEASE DURATION:
- Minimum commercial lease term: none mandated, but 1 year is standard
- Default term if not stated: 5 years (renews for same period)
- Automatic renewal: applies unless opposition given in writing within notice period
- Flag leases with no stated duration (defaults apply, may be unfavourable)

NOTICE PERIODS — TENANT TERMINATION:
- Lease 1 year or longer: 120 days written notice
- Lease under 1 year: 60 days written notice
- Early termination allowed after 1/3 of term has elapsed
- Flag notice periods shorter than statutory minimums

NOTICE PERIODS — LANDLORD TERMINATION:
- Lease 6 years or more: 240 days notice
- Lease 1-6 years: 120 days notice
- Lease under 1 year: 60 days notice
- Landlord can only terminate for: personal use, major renovation, demolition, rent default
- Flag any landlord termination right that exceeds these statutory grounds

RENT INCREASES:
- Landlord must give minimum 30 days written notice of any rent increase
- Annual increases typically linked to CPI (INE — Instituto Nacional de Estatística)
- Upward-only rent review clauses are legal but unusual — flag them
- Flag any rent increase mechanism that deviates from CPI without clear justification

DEPOSIT (CAUÇÃO):
- Legally: 2 months rent maximum for residential; commercial has no statutory cap
- Commercial deposits of 3-6 months are common but above 6 months should be flagged
- Must be returned within agreed period after lease end (typically 30-60 days)
- Flag deposits with no return timeline or disproportionately long return periods

ASSIGNMENT AND SUBLETTING:
- Non-residential leases: may transfer without landlord consent if transferring entire
  commercial establishment — landlord must be notified within 1 month
- Pure assignment of lease rights: requires landlord consent
- Landlord has pre-emption right (direito de preferência) on assignment
- Flag absolute assignment prohibitions — may be invalid under Portuguese law
  for commercial establishment transfers

REPAIRS AND MAINTENANCE:
- Landlord: responsible for structural repairs and maintaining habitability
- Tenant: responsible for ordinary wear and maintenance
- Alterations require written landlord consent
- Flag tenant obligations to carry out structural repairs (non-standard)

EVICTION (DESPEJO):
- Non-payment of 3 months rent: landlord may issue formal notice
- After notice, tenant has 1 month to pay arrears and avoid eviction
- Eviction requires court order under NRAU simplified procedure
- Flag any clause purporting to allow self-help eviction (illegal in Portugal)

HIGH-RISK FLAGS SPECIFIC TO PORTUGAL:
1. No NIF numbers stated — mandatory under Portuguese law
2. No Finanças registration clause — landlord legal obligation
3. Stamp duty attributed to tenant — landlord bears this by law
4. Notice period below statutory minimum — may be unenforceable
5. Absolute assignment prohibition for commercial establishments — may be invalid
6. Landlord termination rights beyond statutory grounds — may be unenforceable
7. Deposit above 6 months for commercial lease — unusual, flag for negotiation
8. No automatic renewal clause — NRAU defaults apply
9. Rent review mechanism not linked to CPI — requires justification
10. No governing law clause specifying Portuguese law — essential for enforceability
"""

PORTUGAL_EXTRACTION_FIELDS = """
PORTUGAL-SPECIFIC FIELDS TO EXTRACT (in addition to standard 16 fields):

- nif_tenant: Portuguese tax identification number (NIF) of tenant
- nif_landlord: Portuguese tax identification number (NIF) of landlord
- financas_registration: Reference to Finanças/AT registration obligation or number
- stamp_duty_clause: Which party bears stamp duty (should be landlord under Portuguese law)
- governing_law: Stated governing law (should be Portuguese law)
- deposit_months: Security deposit expressed as number of months rent
- cpi_index: Whether rent increases reference INE/CPI index (yes/no/not stated)
- automatic_renewal: Whether automatic renewal is stated (yes/no/not stated)
- notice_period_tenant_days: Tenant notice period in days as stated in contract
- notice_period_landlord_days: Landlord notice period in days as stated in contract
- early_termination_after_months: After how many months tenant can exit early
"""

# Model pricing for cost tracking (EUR equivalent, October 2026)
# Sources: OpenAI pricing page, Anthropic pricing page
MODEL_PRICING = {
    # GPT-4o family
    "gpt-4o": {
        "input_per_1k": 0.0025,
        "output_per_1k": 0.0100,
        "eur_rate": 0.92,
    },
    "gpt-4o-2024-11-20": {
        "input_per_1k": 0.0025,
        "output_per_1k": 0.0100,
        "eur_rate": 0.92,
    },
    "gpt-4o-mini": {
        "input_per_1k": 0.00015,
        "output_per_1k": 0.00060,
        "eur_rate": 0.92,
    },
    # Reasoning models (o1, o3 family)
    # Note: reasoning models use more tokens due to internal chain-of-thought
    "o1": {
        "input_per_1k": 0.0150,
        "output_per_1k": 0.0600,
        "eur_rate": 0.92,
    },
    "o1-pro": {
        "input_per_1k": 0.1500,
        "output_per_1k": 0.6000,
        "eur_rate": 0.92,
    },
    "o3": {
        "input_per_1k": 0.0100,
        "output_per_1k": 0.0400,
        "eur_rate": 0.92,
    },
    "o3-mini": {
        "input_per_1k": 0.0011,
        "output_per_1k": 0.0044,
        "eur_rate": 0.92,
    },
    # Claude family
    "claude-haiku-4-5-20251001": {
        "input_per_1k": 0.00080,
        "output_per_1k": 0.00400,
        "eur_rate": 0.92,
    },
    "claude-sonnet-4-6": {
        "input_per_1k": 0.00300,
        "output_per_1k": 0.01500,
        "eur_rate": 0.92,
    },
    # Embeddings
    "text-embedding-3-small": {
        "input_per_1k": 0.00002,
        "output_per_1k": 0.0,
        "eur_rate": 0.92,
    },
}


def get_cost_eur(model: str, tokens_in: int, tokens_out: int) -> float:
    """Calculate cost in EUR for a given model call."""
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4o-mini"])
    cost_usd = (
        (tokens_in / 1000) * pricing["input_per_1k"] +
        (tokens_out / 1000) * pricing["output_per_1k"]
    )
    return round(cost_usd * pricing["eur_rate"], 6)
