"""
Utility functions: PDF text extraction and safe JSON parsing.
"""

import json
import re
from pypdf import PdfReader
import streamlit as st


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract plain text from an uploaded PDF file.
    uploaded_file is a Streamlit UploadedFile object.
    Returns the full text as a string.
    """
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def safe_parse_json(raw: str) -> dict:
    """
    Safely parse a JSON string returned by an LLM.
    Strips markdown code fences if present.
    Returns a dict, or an error dict if parsing fails.
    """
    # strip markdown fences
    cleaned = re.sub(r"```json\s*", "", raw)
    cleaned = re.sub(r"```\s*", "", cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        return {
            "parse_error": f"Could not parse LLM output as JSON: {str(e)}",
            "raw_output": raw,
        }


def format_extraction_result(extracted: dict, flagged: dict, filename: str) -> dict:
    """
    Assemble the final structured output from extraction and flagging results.
    Adds metadata, summary counts, and disclaimer.
    """
    flagged_clauses = flagged.get("flagged_clauses", [])

    high   = sum(1 for c in flagged_clauses if c.get("risk_level") == "high")
    medium = sum(1 for c in flagged_clauses if c.get("risk_level") == "medium")
    low    = sum(1 for c in flagged_clauses if c.get("risk_level") == "low")

    if high > 0:
        recommendation = "PRIORITY REVIEW REQUIRED — high risk clauses identified"
    elif medium > 0:
        recommendation = "REVIEW RECOMMENDED — medium risk clauses identified"
    else:
        recommendation = "STANDARD REVIEW — no high-risk clauses identified"

    return {
        "meta": {
            "filename": filename,
            "model": "gpt-4o",
            "disclaimer": (
                "AI-generated draft. Every field must be reviewed and verified "
                "by a qualified lawyer before use in any legal or financial decision."
            ),
        },
        "summary": {
            "total_flagged_clauses": len(flagged_clauses),
            "high_risk_clauses": high,
            "medium_risk_clauses": medium,
            "low_risk_clauses": low,
            "review_recommendation": recommendation,
        },
        "extracted_fields": extracted,
        "flagged_clauses": flagged_clauses,
    }


def truncate_text(text: str, max_chars: int = 12000) -> str:
    """
    Truncate lease text to fit within LLM context limits.
    12,000 characters covers most standard commercial leases comfortably.
    Logs a warning if truncation occurs.
    """
    if len(text) > max_chars:
        st.warning(
            f"Document is long ({len(text):,} characters). "
            f"Truncated to {max_chars:,} characters for processing. "
            f"Consider splitting very long leases."
        )
        return text[:max_chars]
    return text
