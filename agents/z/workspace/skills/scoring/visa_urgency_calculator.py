"""
Visa Urgency Calculator for Agent Z
=====================================
Deterministic calculation of visa urgency tier from visa type and expiration date.
No AI estimation. Pure date math.

Usage:
    from visa_urgency_calculator import calculate_visa_urgency

    result = calculate_visa_urgency({
        "visa_status": "OPT",
        "visa_expiration_date": "2026-03-15"
    })
"""

import json
from datetime import datetime, timezone, date
from pathlib import Path


LOG_FILE = Path(__file__).parent / "scoring_log.jsonl"

# Visa types that have expiration dates (need urgency tracking)
EXPIRING_VISA_TYPES = {"H1B", "OPT", "CPT", "STEM-OPT", "L1", "TN", "GC-EAD"}

# Visa types that don't expire in a meaningful way for urgency (stored uppercase for comparison)
NON_EXPIRING_VISA_TYPES = {"GC", "CITIZEN"}

# Common aliases for visa types (normalized to canonical forms)
VISA_ALIASES = {
    "GREEN-CARD": "GC",
    "GREENCARD": "GC",
    "US-CITIZEN": "CITIZEN",
    "USC": "CITIZEN",
    "PERMANENT-RESIDENT": "GC",
    "PR": "GC",
}


def calculate_visa_urgency(inputs: dict) -> dict:
    """
    Calculate visa urgency from visa status and expiration date.

    Args:
        inputs: Dict with keys:
            - visa_status (str): H1B / OPT / CPT / STEM-OPT / GC / GC-EAD / Citizen / TN / L1
            - visa_expiration_date (str or None): ISO date string (YYYY-MM-DD) or None
            - current_date (str, optional): Override current date for testing

    Returns:
        Dict with urgency_tier, days_remaining, urgency_score, and explanation.
    """
    visa_status = inputs["visa_status"].upper().replace(" ", "-")
    # Apply alias normalization
    visa_status = VISA_ALIASES.get(visa_status, visa_status)
    expiration_str = inputs.get("visa_expiration_date")

    # Determine current date
    if "current_date" in inputs and inputs["current_date"]:
        current = date.fromisoformat(inputs["current_date"])
    else:
        current = date.today()

    # Non-expiring visa types
    if visa_status in NON_EXPIRING_VISA_TYPES:
        result = {
            "visa_status": visa_status,
            "urgency_tier": "NA",
            "urgency_score": 0,
            "days_remaining": None,
            "explanation": f"{visa_status} does not have an expiration-based urgency.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        _log_calculation(result)
        return result

    # Expiring visa types: need expiration date
    if not expiration_str:
        result = {
            "visa_status": visa_status,
            "urgency_tier": "UNKNOWN",
            "urgency_score": -1,
            "days_remaining": None,
            "explanation": f"ALERT: {visa_status} visa requires an expiration date but none was provided. Cannot calculate urgency.",
            "data_gap": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        _log_calculation(result)
        return result

    # Calculate days remaining
    expiration = date.fromisoformat(expiration_str)
    days_remaining = (expiration - current).days

    # Already expired
    if days_remaining < 0:
        urgency_tier = "CRITICAL"
        urgency_score = 10
        explanation = f"EXPIRED {abs(days_remaining)} days ago. Immediate action required."
    # Urgency tiers per architecture spec
    elif days_remaining < 30:
        urgency_tier = "CRITICAL"
        urgency_score = 10
        explanation = f"Expires in {days_remaining} days. FIRE ALARM -- escalate immediately."
    elif days_remaining < 90:
        urgency_tier = "HIGH"
        urgency_score = 8
        explanation = f"Expires in {days_remaining} days. High priority for placement."
    elif days_remaining < 180:
        urgency_tier = "MEDIUM"
        urgency_score = 5
        explanation = f"Expires in {days_remaining} days. Active marketing priority."
    else:
        urgency_tier = "LOW"
        urgency_score = 2
        explanation = f"Expires in {days_remaining} days. Standard priority."

    result = {
        "visa_status": visa_status,
        "visa_expiration_date": expiration_str,
        "urgency_tier": urgency_tier,
        "urgency_score": urgency_score,
        "days_remaining": days_remaining,
        "explanation": explanation,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    _log_calculation(result)
    return result


def calculate_batch_visa_urgency(consultant_list: list) -> list:
    """Calculate visa urgency for a list of consultants."""
    results = []
    for c in consultant_list:
        urgency = calculate_visa_urgency({
            "visa_status": c.get("visa_status", ""),
            "visa_expiration_date": c.get("visa_expiration_date"),
            "current_date": c.get("current_date")
        })
        urgency["consultant_id"] = c.get("consultant_id", "UNKNOWN")
        urgency["consultant_name"] = c.get("consultant_name", "")
        results.append(urgency)

    # Sort by urgency (CRITICAL first, then HIGH, etc.)
    tier_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "NA": 4, "UNKNOWN": 5}
    results.sort(key=lambda x: (tier_order.get(x["urgency_tier"], 99), x.get("days_remaining") or 9999))

    return results


def _log_calculation(result: dict):
    """Append calculation to scoring log."""
    log_entry = {
        "event_type": "visa_urgency_calculation",
        "timestamp": result["timestamp"],
        "visa_status": result["visa_status"],
        "urgency_tier": result["urgency_tier"],
        "urgency_score": result["urgency_score"],
        "days_remaining": result.get("days_remaining")
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            results = calculate_batch_visa_urgency(data)
        else:
            results = calculate_visa_urgency(data)
        print(json.dumps(results, indent=2))
    else:
        # Demo
        samples = [
            {"visa_status": "OPT", "visa_expiration_date": "2026-03-05", "current_date": "2026-02-12"},
            {"visa_status": "H1B", "visa_expiration_date": "2026-06-15", "current_date": "2026-02-12"},
            {"visa_status": "GC", "visa_expiration_date": None},
            {"visa_status": "Citizen", "visa_expiration_date": None},
            {"visa_status": "H1B", "visa_expiration_date": None},
        ]
        for s in samples:
            result = calculate_visa_urgency(s)
            print(f"{s['visa_status']:10s} | {result['urgency_tier']:10s} | {result['explanation']}")
