"""
Email notification for the Lease Review Assistant.
Sends extraction results to the reviewer via Gmail SMTP.
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def send_extraction_email(result: dict, recipient_email: str, filename: str) -> bool:
    """
    Send extraction results by email to the reviewer.
    Attaches the full JSON result and includes a summary in the body.

    Returns True if sent successfully, False otherwise.
    """
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")

    if not sender or not password:
        return False, "EMAIL_SENDER or EMAIL_PASSWORD not set in .env"

    summary = result.get("summary", {})
    high_risk = summary.get("high_risk_clauses", 0)
    medium_risk = summary.get("medium_risk_clauses", 0)
    total_flagged = summary.get("total_flagged_clauses", 0)
    recommendation = summary.get("review_recommendation", "")
    fields = result.get("extracted_fields", {})
    flagged = result.get("flagged_clauses", [])

    # subject line flags priority
    if high_risk > 0:
        subject = f"🔴 PRIORITY REVIEW REQUIRED — {filename}"
    elif medium_risk > 0:
        subject = f"🟡 Review recommended — {filename}"
    else:
        subject = f"🟢 Extraction complete — {filename}"

    # build email body
    body = f"""
Lease Review Assistant — Extraction Report
Generated: {datetime.now().strftime("%d %B %Y %H:%M")}

DOCUMENT: {filename}

REVIEW RECOMMENDATION: {recommendation}
Total flagged clauses: {total_flagged}
High risk: {high_risk}
Medium risk: {medium_risk}

KEY EXTRACTED FIELDS:
  Tenant:              {fields.get("tenant_name", "Not found")}
  Landlord:            {fields.get("landlord_name", "Not found")}
  Property:            {fields.get("property_address", "Not found")}
  Commencement:        {fields.get("lease_commencement_date", "Not found")}
  Expiry:              {fields.get("lease_expiry_date", "Not found")}
  Rent:                {fields.get("rent_amount", "Not found")}
  Break options:       {fields.get("break_option_dates", "None")}
  Assignment rights:   {fields.get("assignment_rights", "Not found")}
"""

    if flagged:
        body += "\nFLAGGED CLAUSES:\n"
        for i, clause in enumerate(flagged, 1):
            body += f"""
  {i}. {clause.get("clause_type", "Clause")} — Risk: {clause.get("risk_level", "").upper()}
     Quote: "{clause.get("quoted_text", "")}"
     Explanation: {clause.get("plain_language_explanation", "")}
     Action: {clause.get("recommended_action", "")}
"""

    body += """
---
DISCLAIMER: This is an AI-generated draft. Every field must be reviewed and
verified by a qualified lawyer before use in any legal or financial decision.

Lease Review Assistant · Capstone Round 2 · Ironhack AI Consulting
"""

    # build the email
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # attach JSON file
    json_bytes = json.dumps(result, indent=2).encode("utf-8")
    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(json_bytes)
    encoders.encode_base64(attachment)
    json_filename = filename.replace(".pdf", "_review.json")
    attachment.add_header("Content-Disposition", f"attachment; filename={json_filename}")
    msg.attach(attachment)

    # send via Gmail SMTP
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient_email, msg.as_string())
        return True, "Email sent successfully."
    except Exception as e:
        return False, str(e)
