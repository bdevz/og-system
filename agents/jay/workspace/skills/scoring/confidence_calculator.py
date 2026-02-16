"""
Confidence Calculator for Agent Jay
====================================
Computes job-consultant match confidence scores using deterministic weighted scoring.
Jay gathers inputs. This script does the math. Every calculation is logged.

Usage:
    from confidence_calculator import calculate_confidence, calculate_batch_confidence

    result = calculate_confidence({
        "consultant_id": "C-042",
        "job_id": "J-5829",
        "skill_match_percent": 85,
        "years_experience_diff": 2,
        "posting_freshness_days": 1,
        "applicant_count": 18,
        "vendor_tier": 1,
        "consultant_rate": 95000,
        "target_rate": 100000,
        "red_flags": []
    })
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path


WEIGHTS_FILE = Path(__file__).parent / "confidence_weights.json"
LOG_FILE = Path(__file__).parent / "scoring_log.jsonl"


def load_weights() -> dict:
    """Load weights from the human-editable JSON config."""
    with open(WEIGHTS_FILE, "r") as f:
        return json.load(f)


def _score_skill_match(skill_match_percent: float, tables: dict) -> float:
    """Score skill match from percentage (0-100)."""
    if skill_match_percent >= 90:
        return float(tables["skill_match"]["90-100"])
    elif skill_match_percent >= 75:
        return float(tables["skill_match"]["75-90"])
    elif skill_match_percent >= 60:
        return float(tables["skill_match"]["60-75"])
    elif skill_match_percent >= 40:
        return float(tables["skill_match"]["40-60"])
    else:
        return float(tables["skill_match"]["0-40"])


def _score_experience_alignment(years_diff: int, tables: dict) -> float:
    """Score experience alignment based on difference from requirement."""
    abs_diff = abs(years_diff)
    if abs_diff <= 1:
        return float(tables["experience_alignment"]["exact-1"])
    elif abs_diff <= 2:
        return float(tables["experience_alignment"]["2"])
    elif abs_diff <= 3:
        return float(tables["experience_alignment"]["3"])
    elif abs_diff <= 5:
        return float(tables["experience_alignment"]["4-5"])
    else:
        return float(tables["experience_alignment"]["6+"])


def _score_posting_freshness(days_old: int, tables: dict) -> float:
    """Score posting freshness based on age in days."""
    if days_old <= 1:
        return float(tables["posting_freshness"]["0-1"])
    elif days_old <= 3:
        return float(tables["posting_freshness"]["1-3"])
    elif days_old <= 7:
        return float(tables["posting_freshness"]["3-7"])
    elif days_old <= 14:
        return float(tables["posting_freshness"]["7-14"])
    else:
        return float(tables["posting_freshness"]["14+"])


def _score_applicant_volume(count: int, tables: dict) -> float:
    """Score applicant count (fewer is better - less competition)."""
    if count < 25:
        return float(tables["applicant_volume"]["0-25"])
    elif count < 50:
        return float(tables["applicant_volume"]["25-50"])
    elif count < 100:
        return float(tables["applicant_volume"]["50-100"])
    elif count < 200:
        return float(tables["applicant_volume"]["100-200"])
    else:
        return float(tables["applicant_volume"]["200+"])


def _score_vendor_tier(tier: int, tables: dict) -> float:
    """Score vendor tier (1=best, 3=worst)."""
    return float(tables["vendor_tier"].get(str(tier), tables["vendor_tier"].get("unknown", 5)))


def _score_rate_compatibility(consultant_rate: float, target_rate: float, tables: dict) -> float:
    """Score rate compatibility based on percentage difference."""
    if target_rate == 0:
        return 5  # Unknown target, neutral score

    diff_percent = abs((consultant_rate - target_rate) / target_rate) * 100

    if diff_percent <= 15:
        return float(tables["rate_compatibility"]["within-15"])
    elif diff_percent <= 30:
        return float(tables["rate_compatibility"]["within-30"])
    else:
        return float(tables["rate_compatibility"]["beyond-30"])


def _apply_red_flag_penalty(base_score: float, red_flags: list) -> tuple:
    """Apply penalty for each red flag. Returns (adjusted_score, penalty)."""
    penalty = 0
    for flag in red_flags:
        # Each flag reduces score by 0.5-2 points depending on severity
        penalty += 1  # Base penalty per flag

    adjusted = max(1, base_score - penalty)  # Never go below 1
    return adjusted, penalty


def calculate_confidence(inputs: dict) -> dict:
    """
    Calculate confidence score for a consultant-job match.

    Args:
        inputs: Dict with keys:
            - consultant_id (str): Unique identifier
            - consultant_name (str, optional): For readability
            - job_id (str): Unique job identifier
            - job_title (str, optional): For readability
            - vendor_name (str, optional): For reference
            - skill_match_percent (float): 0-100, % of MUST_HAVE skills consultant has
            - years_experience_diff (int): Required years - consultant years (can be negative)
            - posting_freshness_days (int): Days since posting
            - applicant_count (int): Number of applicants
            - vendor_tier (int): 1/2/3 or "unknown"
            - consultant_rate (float): Consultant's target rate in dollars
            - target_rate (float): Job's target rate in dollars
            - red_flags (list, optional): List of red flag strings

    Returns:
        Dict with score, breakdown, recommendation, and reasoning.
    """
    config = load_weights()
    weights = config["weights"]
    tables = config["scoring_tables"]
    thresholds = config["thresholds"]

    # Handle missing red flags
    red_flags = inputs.get("red_flags", [])

    # Score each factor
    skill_score = _score_skill_match(inputs["skill_match_percent"], tables)
    exp_score = _score_experience_alignment(inputs["years_experience_diff"], tables)
    fresh_score = _score_posting_freshness(inputs["posting_freshness_days"], tables)
    volume_score = _score_applicant_volume(inputs["applicant_count"], tables)

    # Handle vendor tier (can be int or string "unknown")
    vendor_tier_val = inputs["vendor_tier"]
    if isinstance(vendor_tier_val, str):
        vendor_tier_val = "unknown"
    vendor_score = _score_vendor_tier(vendor_tier_val, tables)

    rate_score = _score_rate_compatibility(
        inputs["consultant_rate"],
        inputs["target_rate"],
        tables
    )

    # Weighted contributions
    skill_contribution = skill_score * weights["skill_match"]
    exp_contribution = exp_score * weights["experience_alignment"]
    fresh_contribution = fresh_score * weights["posting_freshness"]
    volume_contribution = volume_score * weights["applicant_volume"]
    vendor_contribution = vendor_score * weights["vendor_tier"]
    rate_contribution = rate_score * weights["rate_compatibility"]

    # Composite score before penalties
    composite_before_penalty = round(
        skill_contribution
        + exp_contribution
        + fresh_contribution
        + volume_contribution
        + vendor_contribution
        + rate_contribution,
        2
    )

    # Apply red flag penalties
    composite_after_penalty, penalty = _apply_red_flag_penalty(composite_before_penalty, red_flags)
    composite = round(composite_after_penalty, 2)

    # Determine recommendation
    if composite >= thresholds["pass"]:
        recommendation = "PASS"
        recommendation_label = "Pass to Rick"
    elif composite >= thresholds["review"]:
        recommendation = "REVIEW"
        recommendation_label = "Send to human review"
    else:
        recommendation = "SKIP"
        recommendation_label = "Auto-skip, low confidence"

    result = {
        "consultant_id": inputs.get("consultant_id", "UNKNOWN"),
        "consultant_name": inputs.get("consultant_name", ""),
        "job_id": inputs.get("job_id", "UNKNOWN"),
        "job_title": inputs.get("job_title", ""),
        "vendor_name": inputs.get("vendor_name", ""),
        "score": composite,
        "recommendation": recommendation,
        "recommendation_label": recommendation_label,
        "breakdown": {
            "skill_match": {
                "raw_score": skill_score,
                "weight": weights["skill_match"],
                "contribution": round(skill_contribution, 3),
                "input": inputs["skill_match_percent"]
            },
            "experience_alignment": {
                "raw_score": exp_score,
                "weight": weights["experience_alignment"],
                "contribution": round(exp_contribution, 3),
                "input": inputs["years_experience_diff"]
            },
            "posting_freshness": {
                "raw_score": fresh_score,
                "weight": weights["posting_freshness"],
                "contribution": round(fresh_contribution, 3),
                "input": inputs["posting_freshness_days"]
            },
            "applicant_volume": {
                "raw_score": volume_score,
                "weight": weights["applicant_volume"],
                "contribution": round(volume_contribution, 3),
                "input": inputs["applicant_count"]
            },
            "vendor_tier": {
                "raw_score": vendor_score,
                "weight": weights["vendor_tier"],
                "contribution": round(vendor_contribution, 3),
                "input": vendor_tier_val
            },
            "rate_compatibility": {
                "raw_score": rate_score,
                "weight": weights["rate_compatibility"],
                "contribution": round(rate_contribution, 3),
                "input": {
                    "consultant_rate": inputs["consultant_rate"],
                    "target_rate": inputs["target_rate"]
                }
            },
            "red_flags": {
                "count": len(red_flags),
                "penalty": penalty,
                "flags": red_flags
            }
        },
        "score_components": {
            "before_penalties": composite_before_penalty,
            "after_penalties": composite,
            "total_penalty": penalty
        },
        "weights_version": config["version"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Log the calculation
    _log_calculation(result)

    return result


def calculate_batch_confidence(job_consultant_pairs: list) -> list:
    """
    Calculate confidence scores for a batch of job-consultant pairs and return sorted by score descending.

    Args:
        job_consultant_pairs: List of dicts, each matching the calculate_confidence input schema.

    Returns:
        List of results sorted by score descending.
    """
    results = [calculate_confidence(pair) for pair in job_consultant_pairs]
    results.sort(key=lambda x: x["score"], reverse=True)

    # Add rank
    for i, r in enumerate(results):
        r["rank"] = i + 1

    return results


def _log_calculation(result: dict):
    """Append calculation to scoring log (append-only audit trail)."""
    log_entry = {
        "event_type": "confidence_calculation",
        "timestamp": result["timestamp"],
        "consultant_id": result["consultant_id"],
        "job_id": result["job_id"],
        "score": result["score"],
        "recommendation": result["recommendation"],
        "red_flag_count": result["breakdown"]["red_flags"]["count"],
        "weights_version": result["weights_version"]
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Read input from file
        with open(sys.argv[1], "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            results = calculate_batch_confidence(data)
        else:
            results = calculate_confidence(data)
        print(json.dumps(results, indent=2))
    else:
        # Demo with sample data
        sample = {
            "consultant_id": "C-042",
            "consultant_name": "Ravi Kumar",
            "job_id": "J-5829",
            "job_title": "Senior Java Developer",
            "vendor_name": "Robert Half",
            "skill_match_percent": 85,
            "years_experience_diff": 2,
            "posting_freshness_days": 1,
            "applicant_count": 18,
            "vendor_tier": 1,
            "consultant_rate": 95000,
            "target_rate": 100000,
            "red_flags": []
        }
        result = calculate_confidence(sample)
        print(json.dumps(result, indent=2))

        # Also test a batch
        print("\n\n=== BATCH TEST ===\n")
        batch = [
            {
                "consultant_id": "C-042",
                "consultant_name": "Ravi Kumar",
                "job_id": "J-5829",
                "job_title": "Senior Java Developer",
                "vendor_name": "Robert Half",
                "skill_match_percent": 85,
                "years_experience_diff": 2,
                "posting_freshness_days": 1,
                "applicant_count": 18,
                "vendor_tier": 1,
                "consultant_rate": 95000,
                "target_rate": 100000,
                "red_flags": []
            },
            {
                "consultant_id": "C-107",
                "consultant_name": "Sarah Chen",
                "job_id": "J-5830",
                "job_title": "Python ML Engineer",
                "vendor_name": "Unknown Vendor",
                "skill_match_percent": 65,
                "years_experience_diff": 4,
                "posting_freshness_days": 12,
                "applicant_count": 245,
                "vendor_tier": "unknown",
                "consultant_rate": 120000,
                "target_rate": 110000,
                "red_flags": ["contradictory_tech_stack", "vague_requirements"]
            }
        ]
        batch_results = calculate_batch_confidence(batch)
        print(json.dumps(batch_results, indent=2))
