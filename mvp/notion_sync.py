"""
Notion integration for the Lease Review Assistant.
Creates a page per lease review in the Notion database.
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")


def get_client() -> Client:
    token = os.getenv("NOTION_TOKEN")
    if not token:
        raise ValueError("NOTION_TOKEN must be set in .env")
    return Client(auth=token)


def push_review_to_notion(result: dict, validation: dict = None,
                          supabase_id: str = None) -> str:
    """
    Create a Notion page for a lease review result.
    Returns the Notion page ID.
    """
    if not NOTION_DATABASE_ID:
        raise ValueError("NOTION_DATABASE_ID must be set in .env")

    client = get_client()
    fields = result.get("extracted_fields", {})
    summary = result.get("summary", {})
    flagged = result.get("flagged_clauses", [])
    meta = result.get("meta", {})

    # determine risk level for select property
    high = summary.get("high_risk_clauses", 0)
    medium = summary.get("medium_risk_clauses", 0)
    risk_level = "High" if high > 0 else "Medium" if medium > 0 else "Low"

    # determine recommendation from validation if available
    recommendation = "REVIEW"
    if validation:
        score = validation.get("agreement_score", 0)
        if score >= 90 and high == 0:
            recommendation = "BUY"
        elif high > 2 or score < 70:
            recommendation = "PASS"

    # parse rent amount for number field
    rent_str = fields.get("rent_amount", "") or ""
    rent_num = None
    try:
        import re
        nums = re.findall(r"[\d,]+\.?\d*", rent_str.replace(",", ""))
        if nums:
            rent_num = float(nums[0])
    except Exception:
        pass

    # parse expiry date
    expiry_date = fields.get("lease_expiry_date")

    # build flagged clauses text for page body
    flags_text = ""
    for f in flagged:
        flags_text += (
            f"\n🔴 {f.get('clause_type')} — {f.get('risk_level', '').upper()}\n"
            f"Clause: {f.get('clause_reference', 'N/A')} | Page: {f.get('page_number', 'N/A')}\n"
            f"Quote: \"{f.get('quoted_text', '')}\"\n"
            f"Explanation: {f.get('plain_language_explanation', '')}\n"
            f"Action: {f.get('recommended_action', '')}\n"
            f"PT Law: {f.get('portuguese_law_reference', 'N/A')}\n"
        )

    validation_text = ""
    if validation:
        validation_text = (
            f"\nValidation (Claude): Agreement {validation.get('agreement_score', 0):.0f}% | "
            f"Confidence {validation.get('confidence_score', 0):.2f} | "
            f"Passed: {validation.get('validation_passed', False)}\n"
            f"{validation.get('summary', '')}\n"
        )

    properties = {
        "Filename": {
            "title": [{"text": {"content": meta.get("filename", "Unknown")}}]
        },
        "Tenant": {
            "rich_text": [{"text": {"content": fields.get("tenant_name") or ""}}]
        },
        "Property Address": {
            "rich_text": [{"text": {"content": fields.get("property_address") or ""}}]
        },
        "Risk Level": {
            "select": {"name": risk_level}
        },
        "Recommendation": {
            "select": {"name": recommendation}
        },
        "Reviewer Email": {
            "email": meta.get("reviewer_email") or None
        },
        "Review Date": {
            "date": {"start": datetime.now().strftime("%Y-%m-%d")}
        },
        "Confidence Score": {
            "number": float(validation.get("confidence_score", 0)) if validation else None
        },
    }

    # add rent if parseable
    if rent_num:
        properties["Annual Rent EUR"] = {"number": rent_num}

    # add expiry date if present
    if expiry_date:
        try:
            properties["Expiry Date"] = {
                "date": {"start": str(expiry_date)[:10]}
            }
        except Exception:
            pass

    # remove None values from properties
    properties = {
        k: v for k, v in properties.items()
        if v not in (None, {"email": None}, {"number": None})
    }

    # page content
    page_content = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"text": {"content": "Lease Summary"}}]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"text": {"content":
                    f"Tenant: {fields.get('tenant_name', 'N/A')}\n"
                    f"Landlord: {fields.get('landlord_name', 'N/A')}\n"
                    f"Property: {fields.get('property_address', 'N/A')}\n"
                    f"Term: {fields.get('lease_commencement_date', 'N/A')} to "
                    f"{fields.get('lease_expiry_date', 'N/A')}\n"
                    f"Rent: {fields.get('rent_amount', 'N/A')}\n"
                    f"Break options: {fields.get('break_option_dates', 'None')}\n"
                    f"Assignment: {fields.get('assignment_rights', 'N/A')}\n"
                }}]
            }
        },
    ]

    if flags_text:
        page_content.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"text": {"content": "Flagged Clauses"}}]
            }
        })
        page_content.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"text": {"content": flags_text[:2000]}}]
            }
        })

    if validation_text:
        page_content.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"text": {"content": "AI Validation"}}]
            }
        })
        page_content.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"text": {"content": validation_text[:2000]}}]
            }
        })

    if supabase_id:
        page_content.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"text": {"content":
                    f"Supabase ID: {supabase_id}\n"
                    f"Disclaimer: AI-generated draft. Must be reviewed by a qualified "
                    f"lawyer before use in any legal or financial decision."
                }}]
            }
        })

    response = client.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties=properties,
        children=page_content,
    )

    return response.get("id")
