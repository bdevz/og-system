"""
Priority Calculator for Agent Z
================================
Computes consultant priority scores using deterministic weighted scoring.
AI gathers inputs. This script does the math. Every calculation is logged.

Usage:
    from priority_calculator import calculate_priority, calculate_batch_priorities

    result = calculate_priority({
        "consultant_id": "C-042",
        "visa_urgency_tier": "HIGH",
        "days_on_bench": 45,
        "market_demand": "HIGH",
        "rate_tier": "TOP_QUARTILE",
        "active_submission_count": 0
    })
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path


WEIGHTS_FILE = Path(__file__).parent / "priority_weights.json"
LOG_FILE = Path(__file__).parent / "scoring_log.jsonl"


def load_weights() -> dict:
    """Load weights from the human-editable JSON config."""
    with open(WEIGHTS_FILE, "r") as f:
        return json.load(f)


def _score_visa_urgency(tier: str, tables: dict) -> float:
    """Score visa urgency from tier label."""
    return float(tables["visa_urgency"].get(tier, 0))


def _score_days_on_bench(days: int, tables: dict) -> float:
    """Score days on bench using bracket lookup."""
    if days <= 7:
        return float(tables["days_on_bench"]["0-7"])
    elif days <= 14:
        return float(tables["days_on_bench"]["8-14"])
    elif days <= 30:
        return float(tables["days_on_bench"]["15-30"])
    elif days <= 60:
        return float(tables["days_on_bench"]["31-60"])
    else:
        return float(tables["days_on_bench"]["61+"])


def _score_market_demand(level: str, tables: dict) -> float:
    """Score market demand from level label."""
    return float(tables["market_demand"].get(level, 3))


def _score_rate_tier(tier: str, tables: dict) -> float:
    """Score rate tier from tier label."""
    return float(tables["rate_tier"].get(tier, 3))


def _score_active_submissions(count: int, tables: dict) -> float:
    """Score active submission count (fewer = needs more attention)."""
    if count == 0:
        return float(tables["active_submissions"]["0"])
    elif count <= 3:
        return float(tables["active_submissions"]["1-3"])
    elif count <= 6:
        return float(tables["active_submissions"]["4-6"])
    else:
        return float(tables["active_submissions"]["7+"])


def calculate_priority(inputs: dict) -> dict:
    """
    Calculate priority score for a single consultant.

    Args:
        inputs: Dict with keys:
            - consultant_id (str): Unique identifier
            - consultant_name (str, optional): For readability
            - visa_urgency_tier (str): CRITICAL / HIGH / MEDIUM / LOW / NA
            - days_on_bench (int): Days since bench_start_date
            - market_demand (str): HIGH / MEDIUM / LOW
            - rate_tier (str): TOP_QUARTILE / MID / BOTTOM
            - active_submission_count (int): Number of active submissions

    Returns:
        Dict with score, breakdown, priority_tier, and recommendation.
    """
    config = load_weights()
    weights = config["weights"]
    tables = config["scoring_tables"]
    thresholds = config["thresholds"]

    # Score each factor
    visa_score = _score_visa_urgency(inputs["visa_urgency_tier"], tables)
    bench_score = _score_days_on_bench(inputs["days_on_bench"], tables)
    demand_score = _score_market_demand(inputs["market_demand"], tables)
    rate_score = _score_rate_tier(inputs["rate_tier"], tables)
    submission_score = _score_active_submissions(inputs["active_submission_count"], tables)

    # Weighted contributions
    visa_contribution = visa_score * weights["visa_urgency"]
    bench_contribution = bench_score * weights["days_on_bench"]
    demand_contribution = demand_score * weights["market_demand"]
    rate_contribution = rate_score * weights["rate_tier"]
    submission_contribution = submission_score * weights["active_submission_count"]

    # Composite score
    composite = round(
        visa_contribution
        + bench_contribution
        + demand_contribution
        + rate_contribution
        + submission_contribution,
        2
    )

    # Determine priority tier
    if composite >= thresholds["p1_urgent"]:
        priority_tier = "P1"
        tier_label = "URGENT"
    elif composite >= thresholds["p2_active"]:
        priority_tier = "P2"
        tier_label = "ACTIVE"
    elif composite >= thresholds["p3_maintenance"]:
        priority_tier = "P3"
        tier_label = "MAINTENANCE"
    else:
        priority_tier = "P4"
        tier_label = "LOW/ON HOLD"

    result = {
        "consultant_id": inputs.get("consultant_id", "UNKNOWN"),
        "consultant_name": inputs.get("consultant_name", ""),
        "score": composite,
        "priority_tier": priority_tier,
        "tier_label": tier_label,
        "breakdown": {
            "visa_urgency": {
                "raw_score": visa_score,
                "weight": weights["visa_urgency"],
                "contribution": round(visa_contribution, 3),
                "input": inputs["visa_urgency_tier"]
            },
            "days_on_bench": {
                "raw_score": bench_score,
                "weight": weights["days_on_bench"],
                "contribution": round(bench_contribution, 3),
                "input": inputs["days_on_bench"]
            },
            "market_demand": {
                "raw_score": demand_score,
                "weight": weights["market_demand"],
                "contribution": round(demand_contribution, 3),
                "input": inputs["market_demand"]
            },
            "rate_tier": {
                "raw_score": rate_score,
                "weight": weights["rate_tier"],
                "contribution": round(rate_contribution, 3),
                "input": inputs["rate_tier"]
            },
            "active_submissions": {
                "raw_score": submission_score,
                "weight": weights["active_submission_count"],
                "contribution": round(submission_contribution, 3),
                "input": inputs["active_submission_count"]
            }
        },
        "weights_version": config["version"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Log the calculation
    _log_calculation(result)

    return result


def calculate_batch_priorities(consultant_list: list) -> list:
    """
    Calculate priority scores for a batch of consultants and return sorted by score descending.

    Args:
        consultant_list: List of dicts, each matching the calculate_priority input schema.

    Returns:
        List of results sorted by score descending.
    """
    results = [calculate_priority(c) for c in consultant_list]
    results.sort(key=lambda x: x["score"], reverse=True)

    # Add rank
    for i, r in enumerate(results):
        r["rank"] = i + 1

    return results


def _log_calculation(result: dict):
    """Append calculation to scoring log (append-only audit trail)."""
    log_entry = {
        "event_type": "priority_calculation",
        "timestamp": result["timestamp"],
        "consultant_id": result["consultant_id"],
        "score": result["score"],
        "priority_tier": result["priority_tier"],
        "breakdown": result["breakdown"],
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
            results = calculate_batch_priorities(data)
        else:
            results = calculate_priority(data)
        print(json.dumps(results, indent=2))
    else:
        # Demo with sample data
        sample = {
            "consultant_id": "C-042",
            "consultant_name": "Ravi Kumar",
            "visa_urgency_tier": "HIGH",
            "days_on_bench": 45,
            "market_demand": "HIGH",
            "rate_tier": "TOP_QUARTILE",
            "active_submission_count": 0
        }
        result = calculate_priority(sample)
        print(json.dumps(result, indent=2))
