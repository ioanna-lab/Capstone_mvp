"""
Lease extraction and clause flagging.
Supports multiple OpenAI models including reasoning models (o1, o3).
Updated for Portuguese market with page citations and PT-specific fields.
"""

from dotenv import load_dotenv
load_dotenv()

import os
from openai import OpenAI
from langsmith import traceable

from prompts import (
    EXTRACTION_SYSTEM, FLAGGING_SYSTEM, FLAGGING_USER,
    build_extraction_prompt,
)
from utils import safe_parse_json, truncate_text

# Available models and their characteristics
AVAILABLE_MODELS = {
    "o1-pro":              {"reasoning": True,  "label": "o1-pro (most accurate, slowest)"},
    "o1":                  {"reasoning": True,  "label": "o1 (high accuracy, slower)"},
    "o3":                  {"reasoning": True,  "label": "o3 (latest reasoning)"},
    "o3-mini":             {"reasoning": True,  "label": "o3-mini (fast reasoning)"},
    "gpt-4o-2024-11-20":   {"reasoning": False, "label": "gpt-4o Nov 2024 (recommended)"},
    "gpt-4o":              {"reasoning": False, "label": "gpt-4o (standard)"},
    "gpt-4o-mini":         {"reasoning": False, "label": "gpt-4o-mini (fastest, cheapest)"},
}

DEFAULT_MODEL = "gpt-4o-2024-11-20"


def get_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _call_model(client, model: str, system: str, user: str) -> str:
    """
    Call OpenAI model handling both standard and reasoning model APIs.
    Reasoning models (o1, o3) do not support system messages or temperature.
    They use max_completion_tokens instead of max_tokens.
    """
    is_reasoning = AVAILABLE_MODELS.get(model, {}).get("reasoning", False)

    if is_reasoning:
        # reasoning models: no system message, no temperature
        # combine system context into the user message
        combined = f"{system}\n\n{user}"
        response = client.chat.completions.create(
            model=model,
            max_completion_tokens=4000,
            messages=[{"role": "user", "content": combined}],
        )
    else:
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            max_tokens=4000,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
    return response.choices[0].message.content


@traceable(name="extract_lease_fields")
def extract_lease_fields(lease_text: str, model: str = DEFAULT_MODEL) -> dict:
    client = get_client()
    content = _call_model(
        client, model,
        EXTRACTION_SYSTEM,
        build_extraction_prompt(lease_text),
    )
    parsed = safe_parse_json(content)

    # handle both new format {fields, citations} and old flat format
    if "fields" in parsed:
        return {"fields": parsed.get("fields", {}), "citations": parsed.get("citations", {})}
    return {"fields": parsed, "citations": {}}


@traceable(name="flag_unusual_clauses")
def flag_unusual_clauses(lease_text: str, model: str = DEFAULT_MODEL) -> dict:
    client = get_client()
    content = _call_model(
        client, model,
        FLAGGING_SYSTEM,
        FLAGGING_USER.format(lease_text=lease_text),
    )
    return safe_parse_json(content)


@traceable(name="process_lease_document")
def process_lease(lease_text: str, filename: str,
                  model: str = DEFAULT_MODEL) -> dict:
    text = truncate_text(lease_text)

    extraction = extract_lease_fields(text, model=model)
    flagged = flag_unusual_clauses(text, model=model)

    fields = extraction.get("fields", {})
    citations = extraction.get("citations", {})
    flagged_clauses = flagged.get("flagged_clauses", [])

    # split standard fields from PT-specific fields
    pt_field_keys = {
        "nif_tenant", "nif_landlord", "financas_registration",
        "stamp_duty_clause", "governing_law", "deposit_months",
        "cpi_index", "automatic_renewal", "notice_period_tenant_days",
        "notice_period_landlord_days", "early_termination_after_months",
    }
    standard_fields = {k: v for k, v in fields.items() if k not in pt_field_keys}
    portugal_fields = {k: v for k, v in fields.items() if k in pt_field_keys}

    high   = sum(1 for c in flagged_clauses if c.get("risk_level") == "high")
    medium = sum(1 for c in flagged_clauses if c.get("risk_level") == "medium")

    if high > 0:
        recommendation = "PRIORITY REVIEW REQUIRED — high risk clauses identified"
    elif medium > 0:
        recommendation = "REVIEW RECOMMENDED — medium risk clauses identified"
    else:
        recommendation = "STANDARD REVIEW — no high-risk clauses identified"

    return {
        "meta": {
            "filename": filename,
            "model": model,
            "is_reasoning_model": AVAILABLE_MODELS.get(model, {}).get("reasoning", False),
            "disclaimer": (
                "AI-generated draft. Must be reviewed by a qualified lawyer "
                "before use in any legal or financial decision."
            ),
        },
        "summary": {
            "total_flagged_clauses": len(flagged_clauses),
            "high_risk_clauses": high,
            "medium_risk_clauses": medium,
            "low_risk_clauses": sum(1 for c in flagged_clauses
                                    if c.get("risk_level") == "low"),
            "review_recommendation": recommendation,
        },
        "extracted_fields": standard_fields,
        "portugal_fields":  portugal_fields,
        "citations":        citations,
        "flagged_clauses":  flagged_clauses,
    }
