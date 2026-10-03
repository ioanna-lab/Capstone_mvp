"""
Supabase database client for the Lease Review Assistant.
Handles all persistence: lease reviews, evaluations, costs, proposals.
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


def get_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
    return create_client(url, key)


def save_lease_review(result: dict, validation: dict = None,
                      cost_breakdown: dict = None) -> str:
    """
    Save a complete lease review to Supabase.
    Returns the UUID of the saved record.
    """
    client = get_client()
    fields = result.get("extracted_fields", {})
    pt_fields = result.get("portugal_fields", {})
    flagged = result.get("flagged_clauses", [])
    summary = result.get("summary", {})
    costs = cost_breakdown or {}

    # parse dates safely
    def safe_date(val):
        if not val:
            return None
        try:
            return str(val)[:10]  # ISO date string
        except Exception:
            return None

    record = {
        "filename":               result.get("meta", {}).get("filename", "unknown"),
        "reviewer_email":         result.get("meta", {}).get("reviewer_email"),
        "market":                 "PT",
        "extraction_model":       result.get("meta", {}).get("model", "gpt-4o"),

        # standard fields
        "tenant_name":            fields.get("tenant_name"),
        "landlord_name":          fields.get("landlord_name"),
        "property_address":       fields.get("property_address"),
        "lease_commencement_date": safe_date(fields.get("lease_commencement_date")),
        "lease_expiry_date":      safe_date(fields.get("lease_expiry_date")),
        "break_option_dates":     fields.get("break_option_dates"),
        "rent_amount":            fields.get("rent_amount"),
        "rent_review_mechanism":  fields.get("rent_review_mechanism"),
        "rent_escalation_schedule": fields.get("rent_escalation_schedule"),
        "security_deposit":       fields.get("security_deposit"),
        "permitted_use":          fields.get("permitted_use"),
        "assignment_rights":      fields.get("assignment_rights"),
        "tenant_break_conditions": fields.get("tenant_break_conditions"),
        "service_charge":         fields.get("service_charge"),
        "key_tenant_obligations": fields.get("key_tenant_obligations"),
        "key_landlord_obligations": fields.get("key_landlord_obligations"),

        # portugal-specific fields
        "nif_tenant":             pt_fields.get("nif_tenant"),
        "nif_landlord":           pt_fields.get("nif_landlord"),
        "financas_registration":  pt_fields.get("financas_registration"),
        "stamp_duty_rate":        10.0,  # statutory rate in Portugal
        "mandatory_notice_period": pt_fields.get("notice_period_tenant_days"),
        "obras_consent_required": True,  # default under Portuguese law

        # flagging
        "flagged_clauses":        flagged,
        "total_flagged":          summary.get("total_flagged_clauses", 0),
        "high_risk_count":        summary.get("high_risk_clauses", 0),
        "medium_risk_count":      summary.get("medium_risk_clauses", 0),
        "review_recommendation":  summary.get("review_recommendation"),

        # raw outputs
        "raw_extraction":         result,

        # cost tracking
        "extraction_tokens_in":   costs.get("extraction_tokens_in", 0),
        "extraction_tokens_out":  costs.get("extraction_tokens_out", 0),
        "validation_tokens_in":   costs.get("validation_tokens_in", 0),
        "validation_tokens_out":  costs.get("validation_tokens_out", 0),
        "total_cost_eur":         costs.get("total_cost_eur", 0),
    }

    # add validation if present
    if validation:
        record["validation_model"] = "claude-haiku-4-5-20251001"
        record["validation_result"] = validation
        record["validation_passed"] = validation.get("validation_passed", False)
        record["confidence_score"] = validation.get("confidence_score", 0.0)
        record["raw_validation"] = validation

    response = client.table("lease_reviews").insert(record).execute()

    if response.data:
        return response.data[0]["id"]
    return None


def save_evaluation(lease_review_id: str, model_a: str, model_b: str,
                    comparison: dict) -> str:
    """Save a cross-model evaluation result."""
    client = get_client()
    record = {
        "lease_review_id":   lease_review_id,
        "model_a":           model_a,
        "model_b":           model_b,
        "fields_agreed":     comparison.get("fields_agreed", 0),
        "fields_disagreed":  comparison.get("fields_disagreed", 0),
        "agreement_rate":    comparison.get("agreement_rate", 0.0),
        "disagreements":     comparison.get("disagreements", []),
        "flags_agreed":      comparison.get("flags_agreed", 0),
        "flags_only_in_a":   comparison.get("flags_only_in_a", 0),
        "flags_only_in_b":   comparison.get("flags_only_in_b", 0),
        "evaluation_passed": comparison.get("evaluation_passed", False),
        "notes":             comparison.get("notes"),
    }
    response = client.table("evaluation_history").insert(record).execute()
    if response.data:
        return response.data[0]["id"]
    return None


def save_cost(lease_review_id: str, model: str, call_type: str,
              tokens_in: int, tokens_out: int, cost_eur: float,
              price_in: float = None, price_out: float = None):
    """Save a granular cost record for one API call."""
    client = get_client()
    record = {
        "lease_review_id":   lease_review_id,
        "model":             model,
        "call_type":         call_type,
        "tokens_in":         tokens_in,
        "tokens_out":        tokens_out,
        "cost_eur":          cost_eur,
        "price_per_1k_in":   price_in,
        "price_per_1k_out":  price_out,
    }
    client.table("cost_history").insert(record).execute()


def save_proposal(proposal: dict) -> str:
    """Save an acquisition proposal."""
    client = get_client()
    response = client.table("acquisition_proposals").insert(proposal).execute()
    if response.data:
        return response.data[0]["id"]
    return None


def get_recent_reviews(limit: int = 20) -> list:
    """Get the most recent lease reviews for the history tab."""
    client = get_client()
    response = (
        client.table("lease_reviews")
        .select("id, created_at, filename, tenant_name, property_address, "
                "rent_amount, total_flagged, high_risk_count, "
                "review_recommendation, validation_passed, total_cost_eur")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data or []


def get_review_by_id(review_id: str) -> dict:
    """Get a full lease review by ID."""
    client = get_client()
    response = (
        client.table("lease_reviews")
        .select("*")
        .eq("id", review_id)
        .single()
        .execute()
    )
    return response.data


def get_cost_summary() -> dict:
    """Get total cost and call counts across all reviews."""
    client = get_client()
    response = (
        client.table("cost_history")
        .select("model, call_type, tokens_in, tokens_out, cost_eur")
        .execute()
    )
    rows = response.data or []
    total_cost = sum(r.get("cost_eur", 0) for r in rows)
    total_calls = len(rows)
    by_model = {}
    for r in rows:
        m = r.get("model", "unknown")
        if m not in by_model:
            by_model[m] = {"calls": 0, "cost_eur": 0}
        by_model[m]["calls"] += 1
        by_model[m]["cost_eur"] += r.get("cost_eur", 0)
    return {
        "total_cost_eur": round(total_cost, 4),
        "total_calls": total_calls,
        "by_model": by_model,
    }


def get_few_shot_examples(field_name: str, limit: int = 3) -> list:
    """
    Retrieve validated corrections for a specific field to use as few-shot
    examples in the extraction prompt. This is the feedback loop.
    """
    client = get_client()
    # corrections are stored in a jsonb column on lease_reviews
    # we query for reviews where validation flagged this field as incorrect
    # and a lawyer correction was stored
    try:
        response = (
            client.table("lease_reviews")
            .select("validation_result, raw_extraction")
            .not_.is_("validation_result", "null")
            .limit(20)
            .execute()
        )
        examples = []
        for row in (response.data or []):
            val = row.get("validation_result", {})
            fv = val.get("field_validations", {}).get(field_name, {})
            if fv.get("status") == "incorrect" and fv.get("comment"):
                raw = row.get("raw_extraction", {})
                fields = raw.get("extracted_fields", {})
                examples.append({
                    "field_name": field_name,
                    "incorrect_value": fields.get(field_name),
                    "correct_value": fv.get("comment"),
                    "input_snippet": str(fields.get(field_name, ""))[:200],
                })
        return examples[:limit]
    except Exception:
        return []
