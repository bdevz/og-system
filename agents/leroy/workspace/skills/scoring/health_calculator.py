"""
Health Calculator for Agent Leroy
==================================
Computes LinkedIn profile health score using deterministic weighted scoring.
Leroy gathers inputs. This script does the math. Every calculation is logged.

Usage:
    from scoring.health_calculator import calculate_health, calculate_portfolio_health

    result = calculate_health({
        "profile_id": "P-001",
        "account_age_days": 180,
        "connection_count": 350,
        "daily_application_count": 2,
        "days_since_last_restriction": 45,
        "activity_diversity_score": 85,
        "session_pattern_regularity_score": 90,
        "connection_request_acceptance_rate": 75
    })

    # Portfolio snapshot
    portfolio = calculate_portfolio_health([profile1, profile2, ...])
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path


WEIGHTS_FILE = Path(__file__).parent / "health_weights.json"
LOG_FILE = Path(__file__).parent / "scoring_log.jsonl"


def load_weights() -> dict:
    """Load weights and scoring tables from the human-editable JSON config."""
    with open(WEIGHTS_FILE, "r") as f:
        return json.load(f)


def _score_account_age(days: int, tables: dict) -> float:
    """Score account age using bracket lookup."""
    if days < 30:
        return float(tables["account_age"]["less_than_30"])
    elif days < 91:
        return float(tables["account_age"]["30_to_90"])
    elif days < 181:
        return float(tables["account_age"]["91_to_180"])
    else:
        return float(tables["account_age"]["181_plus"])


def _score_connection_count(count: int, tables: dict) -> float:
    """Score connection count using bracket lookup."""
    if count < 50:
        return float(tables["connection_count"]["less_than_50"])
    elif count < 101:
        return float(tables["connection_count"]["50_to_100"])
    elif count < 301:
        return float(tables["connection_count"]["101_to_300"])
    else:
        return float(tables["connection_count"]["301_plus"])


def _score_daily_applications(count: int, tables: dict) -> float:
    """Score daily application count (more apps = lower score, danger zone)."""
    if count == 0:
        return float(tables["daily_application_count"]["0_applications"])
    elif count <= 2:
        return float(tables["daily_application_count"]["1_to_2"])
    elif count <= 4:
        return float(tables["daily_application_count"]["3_to_4"])
    elif count == 5:
        return float(tables["daily_application_count"]["5"])
    else:
        return float(tables["daily_application_count"]["6_plus"])


def _score_days_since_restriction(days: int, tables: dict) -> float:
    """Score days since last restriction (never restricted is best)."""
    if days == -1:  # Never restricted sentinel
        return float(tables["days_since_last_restriction"]["never_restricted"])
    elif days >= 90:
        return float(tables["days_since_last_restriction"]["90_plus_days"])
    elif days >= 30:
        return float(tables["days_since_last_restriction"]["30_to_90_days"])
    else:
        return float(tables["days_since_last_restriction"]["less_than_30_days"])


def _score_activity_diversity(score: int, tables: dict) -> float:
    """Score activity diversity (0-100)."""
    if score >= 85:
        return float(tables["activity_diversity_score"]["diverse"])
    elif score >= 70:
        return float(tables["activity_diversity_score"]["mostly_diverse"])
    elif score >= 50:
        return float(tables["activity_diversity_score"]["moderate"])
    elif score >= 30:
        return float(tables["activity_diversity_score"]["limited"])
    else:
        return float(tables["activity_diversity_score"]["only_applying"])


def _score_session_regularity(score: int, tables: dict) -> float:
    """Score session pattern regularity (0-100, higher = more human-like)."""
    if score >= 90:
        return float(tables["session_pattern_regularity_score"]["highly_variable"])
    elif score >= 80:
        return float(tables["session_pattern_regularity_score"]["variable_human_like"])
    elif score >= 50:
        return float(tables["session_pattern_regularity_score"]["somewhat_variable"])
    elif score >= 40:
        return float(tables["session_pattern_regularity_score"]["regular_pattern"])
    else:
        return float(tables["session_pattern_regularity_score"]["mechanical"])


def _score_connection_acceptance_rate(rate: float, tables: dict) -> float:
    """Score connection request acceptance rate (0-100%)."""
    if rate > 70:
        return float(tables["connection_request_acceptance_rate"]["over_70_percent"])
    elif rate >= 50:
        return float(tables["connection_request_acceptance_rate"]["50_to_70_percent"])
    elif rate >= 30:
        return float(tables["connection_request_acceptance_rate"]["30_to_50_percent"])
    else:
        return float(tables["connection_request_acceptance_rate"]["under_30_percent"])


def _determine_health_state(score: float, config: dict) -> tuple:
    """Determine health state (GREEN/YELLOW/ORANGE/RED) from score."""
    thresholds = config["thresholds"]
    state_defs = config["state_definitions"]

    if score >= thresholds["green_minimum"]:
        return ("GREEN", state_defs["GREEN"])
    elif score >= thresholds["yellow_minimum"]:
        return ("YELLOW", state_defs["YELLOW"])
    elif score >= thresholds["orange_minimum"]:
        return ("ORANGE", state_defs["ORANGE"])
    else:
        return ("RED", state_defs["RED"])


def _get_recommended_actions(state: str, config: dict) -> list:
    """Get recommended actions for health state."""
    return config["recommended_actions"].get(state, [])


def calculate_health(inputs: dict) -> dict:
    """
    Calculate health score for a single LinkedIn profile.

    Args:
        inputs: Dict with keys:
            - profile_id (str): Unique identifier
            - account_age_days (int): Days since profile creation
            - connection_count (int): Total number of connections
            - daily_application_count (int): Applications submitted today
            - days_since_last_restriction (int): Days since last restriction (-1 if never)
            - activity_diversity_score (float): 0-100, higher = more diverse
            - session_pattern_regularity_score (float): 0-100, higher = more human-like
            - connection_request_acceptance_rate (float): 0-100, % of sent requests accepted

    Returns:
        Dict with score, state, breakdown, actions, and metadata.
    """
    config = load_weights()
    weights = config["weights"]
    tables = config["scoring_tables"]

    # Score each factor
    age_score = _score_account_age(inputs["account_age_days"], tables)
    conn_score = _score_connection_count(inputs["connection_count"], tables)
    app_score = _score_daily_applications(inputs["daily_application_count"], tables)
    restrict_score = _score_days_since_restriction(inputs["days_since_last_restriction"], tables)
    diversity_score = _score_activity_diversity(inputs["activity_diversity_score"], tables)
    regularity_score = _score_session_regularity(inputs["session_pattern_regularity_score"], tables)
    acceptance_score = _score_connection_acceptance_rate(inputs["connection_request_acceptance_rate"], tables)

    # Weighted contributions
    age_contribution = age_score * weights["account_age"]
    conn_contribution = conn_score * weights["connection_count"]
    app_contribution = app_score * weights["daily_application_count"]
    restrict_contribution = restrict_score * weights["days_since_last_restriction"]
    diversity_contribution = diversity_score * weights["activity_diversity_score"]
    regularity_contribution = regularity_score * weights["session_pattern_regularity_score"]
    acceptance_contribution = acceptance_score * weights["connection_request_acceptance_rate"]

    # Composite score (0-100)
    composite = round(
        age_contribution
        + conn_contribution
        + app_contribution
        + restrict_contribution
        + diversity_contribution
        + regularity_contribution
        + acceptance_contribution,
        2
    )

    # Determine health state
    state, state_def = _determine_health_state(composite, config)
    actions = _get_recommended_actions(state, config)

    # Next check time (24 hours from now)
    now = datetime.now(timezone.utc)
    next_check = datetime.fromtimestamp(now.timestamp() + 86400, tz=timezone.utc)

    result = {
        "profile_id": inputs.get("profile_id", "UNKNOWN"),
        "score": composite,
        "state": state,
        "state_definition": state_def,
        "breakdown": {
            "account_age": {
                "raw_score": age_score,
                "weight": weights["account_age"],
                "contribution": round(age_contribution, 3),
                "input": inputs["account_age_days"]
            },
            "connection_count": {
                "raw_score": conn_score,
                "weight": weights["connection_count"],
                "contribution": round(conn_contribution, 3),
                "input": inputs["connection_count"]
            },
            "daily_application_count": {
                "raw_score": app_score,
                "weight": weights["daily_application_count"],
                "contribution": round(app_contribution, 3),
                "input": inputs["daily_application_count"]
            },
            "days_since_last_restriction": {
                "raw_score": restrict_score,
                "weight": weights["days_since_last_restriction"],
                "contribution": round(restrict_contribution, 3),
                "input": inputs["days_since_last_restriction"]
            },
            "activity_diversity_score": {
                "raw_score": diversity_score,
                "weight": weights["activity_diversity_score"],
                "contribution": round(diversity_contribution, 3),
                "input": inputs["activity_diversity_score"]
            },
            "session_pattern_regularity_score": {
                "raw_score": regularity_score,
                "weight": weights["session_pattern_regularity_score"],
                "contribution": round(regularity_contribution, 3),
                "input": inputs["session_pattern_regularity_score"]
            },
            "connection_request_acceptance_rate": {
                "raw_score": acceptance_score,
                "weight": weights["connection_request_acceptance_rate"],
                "contribution": round(acceptance_contribution, 3),
                "input": inputs["connection_request_acceptance_rate"]
            }
        },
        "recommended_actions": actions,
        "weights_version": config["version"],
        "next_check": next_check.isoformat(),
        "timestamp": now.isoformat()
    }

    # Log the calculation
    _log_calculation(result)

    return result


def calculate_portfolio_health(profile_list: list) -> dict:
    """
    Calculate health scores for all profiles in portfolio and return aggregate snapshot.

    Args:
        profile_list: List of profile dicts, each matching calculate_health input schema.

    Returns:
        Dict with aggregate health snapshot: state distribution, average score, tier breakdown.
    """
    results = [calculate_health(p) for p in profile_list]

    # Group by state
    state_counts = {"GREEN": 0, "YELLOW": 0, "ORANGE": 0, "RED": 0}
    state_profiles = {"GREEN": [], "YELLOW": [], "ORANGE": [], "RED": []}

    for result in results:
        state = result["state"]
        state_counts[state] += 1
        state_profiles[state].append(result["profile_id"])

    # Calculate aggregate metrics
    scores = [r["score"] for r in results]
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0
    min_score = min(scores) if scores else 0
    max_score = max(scores) if scores else 0

    now = datetime.now(timezone.utc)

    portfolio_snapshot = {
        "total_profiles": len(profile_list),
        "average_health_score": avg_score,
        "min_health_score": min_score,
        "max_health_score": max_score,
        "state_distribution": state_counts,
        "profiles_by_state": state_profiles,
        "immediate_actions": _get_critical_actions(state_profiles),
        "timestamp": now.isoformat()
    }

    return portfolio_snapshot


def _get_critical_actions(state_profiles: dict) -> list:
    """Get critical actions based on portfolio state."""
    actions = []

    if state_profiles["RED"]:
        actions.append(f"CRITICAL: {len(state_profiles['RED'])} profiles in RED state - quarantine and investigate")

    if state_profiles["ORANGE"]:
        actions.append(f"HIGH: {len(state_profiles['ORANGE'])} profiles in ORANGE state - reduce to hydration activity")

    if len(state_profiles["YELLOW"]) > len(state_profiles["GREEN"]):
        actions.append("WARNING: More profiles in YELLOW than GREEN - portfolio stress high")

    return actions


def _log_calculation(result: dict):
    """Append calculation to scoring log (append-only audit trail)."""
    log_entry = {
        "event_type": "health_calculation",
        "timestamp": result["timestamp"],
        "profile_id": result["profile_id"],
        "score": result["score"],
        "state": result["state"],
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
            results = calculate_portfolio_health(data)
        else:
            results = calculate_health(data)
        print(json.dumps(results, indent=2))
    else:
        # Demo with sample data
        print("=== SINGLE PROFILE HEALTH CALCULATION ===\n")
        sample = {
            "profile_id": "P-001",
            "account_age_days": 180,
            "connection_count": 350,
            "daily_application_count": 2,
            "days_since_last_restriction": 45,
            "activity_diversity_score": 85,
            "session_pattern_regularity_score": 90,
            "connection_request_acceptance_rate": 75
        }
        result = calculate_health(sample)
        print(json.dumps(result, indent=2))

        print("\n\n=== PORTFOLIO HEALTH SNAPSHOT ===\n")
        portfolio_samples = [
            {
                "profile_id": "P-001",
                "account_age_days": 180,
                "connection_count": 350,
                "daily_application_count": 2,
                "days_since_last_restriction": 45,
                "activity_diversity_score": 85,
                "session_pattern_regularity_score": 90,
                "connection_request_acceptance_rate": 75
            },
            {
                "profile_id": "P-002",
                "account_age_days": 90,
                "connection_count": 200,
                "daily_application_count": 4,
                "days_since_last_restriction": 15,
                "activity_diversity_score": 60,
                "session_pattern_regularity_score": 70,
                "connection_request_acceptance_rate": 55
            },
            {
                "profile_id": "P-003",
                "account_age_days": 45,
                "connection_count": 100,
                "daily_application_count": 0,
                "days_since_last_restriction": -1,
                "activity_diversity_score": 70,
                "session_pattern_regularity_score": 85,
                "connection_request_acceptance_rate": 65
            }
        ]
        portfolio = calculate_portfolio_health(portfolio_samples)
        print(json.dumps(portfolio, indent=2))
