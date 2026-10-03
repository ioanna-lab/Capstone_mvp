"""
Acquisition proposal generator.
Aggregates multiple lease reviews for a single property and produces
a structured BUY / REVIEW / PASS recommendation with financial analysis.
Localised for the Portuguese market (IMT, Stamp Duty, NRAU obligations).
"""

from datetime import date, datetime
from typing import List, Optional


# Portugal IMT rates for commercial property acquisition (2026)
# Source: AT (Autoridade Tributária)
IMT_RATE_COMMERCIAL = 0.065   # 6.5% for commercial property
STAMP_DUTY_ACQUISITION = 0.008  # 0.8% on property acquisition


def calculate_wale(leases: List[dict]) -> Optional[float]:
    """
    Calculate Weighted Average Lease Expiry (WALE) in years.
    Weight = annual rent contribution as % of total rent.
    """
    today = date.today()
    weighted_sum = 0.0
    total_rent = 0.0

    for lease in leases:
        fields = lease.get("extracted_fields", {})
        expiry_str = fields.get("lease_expiry_date")
        rent_str = fields.get("rent_amount", "") or ""

        # parse expiry
        try:
            expiry = date.fromisoformat(str(expiry_str)[:10])
            years_remaining = max((expiry - today).days / 365.25, 0)
        except Exception:
            continue

        # parse rent
        import re
        nums = re.findall(r"[\d,]+\.?\d*", rent_str.replace(",", ""))
        annual_rent = float(nums[0]) if nums else 0

        weighted_sum += years_remaining * annual_rent
        total_rent += annual_rent

    if total_rent == 0:
        return None
    return round(weighted_sum / total_rent, 2)


def calculate_composite_risk(lease_reviews: List[dict]) -> float:
    """
    Calculate a composite risk score 0-10 across all leases.
    High risk clause = 2 points, medium = 1 point, normalised.
    """
    total_score = 0
    for review in lease_reviews:
        summary = review.get("summary", {})
        total_score += summary.get("high_risk_clauses", 0) * 2
        total_score += summary.get("medium_risk_clauses", 0) * 1
    # normalise to 0-10 scale
    max_reasonable = len(lease_reviews) * 10
    return round(min((total_score / max(max_reasonable, 1)) * 10, 10), 2)


def generate_proposal(
    property_name: str,
    property_address: str,
    property_type: str,
    asking_price_eur: float,
    district: str,
    lease_reviews: List[dict],
    lease_review_ids: List[str] = None,
) -> dict:
    """
    Generate an acquisition proposal from a list of lease reviews.
    Returns a structured dict ready for Supabase and display.
    """
    if not lease_reviews:
        return {"error": "No lease reviews provided"}

    # financial calculations
    total_annual_rent = 0
    for review in lease_reviews:
        fields = review.get("extracted_fields", {})
        rent_str = fields.get("rent_amount", "") or ""
        import re
        nums = re.findall(r"[\d,]+\.?\d*", rent_str.replace(",", ""))
        if nums:
            total_annual_rent += float(nums[0])

    # yield
    gross_yield = (
        round((total_annual_rent / asking_price_eur) * 100, 2)
        if asking_price_eur and asking_price_eur > 0 else None
    )

    # Portugal acquisition taxes
    imt = round(asking_price_eur * IMT_RATE_COMMERCIAL, 2)
    stamp_duty_acq = round(asking_price_eur * STAMP_DUTY_ACQUISITION, 2)
    total_tax = imt + stamp_duty_acq

    # WALE
    wale = calculate_wale(lease_reviews)

    # earliest break
    earliest_break = None
    for review in lease_reviews:
        fields = review.get("extracted_fields", {})
        breaks = fields.get("break_option_dates", []) or []
        for b in breaks:
            b_date = b.get("date") if isinstance(b, dict) else str(b)
            try:
                d = date.fromisoformat(str(b_date)[:10])
                if earliest_break is None or d < earliest_break:
                    earliest_break = d
            except Exception:
                pass

    # risk
    composite_risk = calculate_composite_risk(lease_reviews)
    high_risk_leases = sum(
        1 for r in lease_reviews
        if r.get("summary", {}).get("high_risk_clauses", 0) > 0
    )
    total_flags = sum(
        r.get("summary", {}).get("total_flagged_clauses", 0)
        for r in lease_reviews
    )

    # recommendation logic
    reasons = []
    if composite_risk >= 7:
        recommendation = "PASS"
        reasons.append(f"Composite risk score {composite_risk}/10 exceeds threshold")
    elif composite_risk >= 4 or high_risk_leases > 0:
        recommendation = "REVIEW"
        reasons.append(f"{high_risk_leases} lease(s) contain high-risk clauses requiring legal review")
    else:
        recommendation = "BUY"
        reasons.append("All leases reviewed with no material high-risk findings")

    if gross_yield:
        if gross_yield < 4.0:
            if recommendation == "BUY":
                recommendation = "REVIEW"
            reasons.append(f"Gross yield {gross_yield}% is below 4% threshold for Portuguese commercial")
        else:
            reasons.append(f"Gross yield {gross_yield}% meets commercial investment threshold")

    if wale and wale < 2:
        reasons.append(f"WALE of {wale} years is short — significant renewal risk")
    elif wale:
        reasons.append(f"WALE of {wale} years provides reasonable income security")

    if total_tax and asking_price_eur:
        reasons.append(
            f"Total acquisition tax (IMT + Stamp Duty): €{total_tax:,.0f} "
            f"({(total_tax/asking_price_eur*100):.1f}% of asking price)"
        )

    # confidence
    validated_count = sum(
        1 for r in lease_reviews
        if r.get("summary", {}).get("review_recommendation") is not None
    )
    if validated_count == len(lease_reviews) and composite_risk < 4:
        confidence = "HIGH"
    elif high_risk_leases > len(lease_reviews) // 2:
        confidence = "LOW"
    else:
        confidence = "MEDIUM"

    return {
        "property_name":             property_name,
        "property_address":          property_address,
        "property_type":             property_type,
        "asking_price_eur":          asking_price_eur,
        "district":                  district,
        "total_annual_rent_eur":     round(total_annual_rent, 2),
        "number_of_leases":          len(lease_reviews),
        "wale_years":                wale,
        "earliest_break_date":       str(earliest_break) if earliest_break else None,
        "composite_risk_score":      composite_risk,
        "high_risk_leases":          high_risk_leases,
        "total_flags":               total_flags,
        "gross_yield_pct":           gross_yield,
        "estimated_imt_eur":         imt,
        "estimated_stamp_duty_eur":  stamp_duty_acq,
        "estimated_total_tax_eur":   total_tax,
        "recommendation":            recommendation,
        "recommendation_reasons":    reasons,
        "confidence_level":          confidence,
        "lease_review_ids":          lease_review_ids or [],
    }
