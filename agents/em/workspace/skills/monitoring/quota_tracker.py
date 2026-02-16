"""
Quota Tracker for EM
====================
Tracks agent performance against daily quotas.
Implements 4-level intervention ladder: OBSERVE -> DIAGNOSE -> INTERVENE -> REBUILD.

Usage:
    from quota_tracker import calculate_quota_compliance

    compliance = calculate_quota_compliance("Jay", daily_metrics)
    # compliance = {
    #   "agent": "Jay",
    #   "date": "2025-02-15",
    #   "quotas": [
    #     {
    #       "metric": "jobs_researched",
    #       "target": 20,
    #       "actual": 18,
    #       "status": "MISS",
    #       "pct_of_target": 90
    #     },
    #     ...
    #   ],
    #   "overall_status": "MISS",
    #   "intervention_level": "OBSERVE"
    # }
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any


QUOTA_CONFIG_FILE = Path(__file__).parent / "quota_config.json"
QUOTA_PERFORMANCE_LOG = Path(__file__).parent.parent.parent / "memory" / "quota-performance.jsonl"
SYSTEM_HISTORY = Path(__file__).parent.parent.parent / "memory" / "system-history.jsonl"


QUOTA_DEFINITIONS = {
    "Jay": {
        "jobs_researched": {"target": 20, "unit": "jobs/day", "weight": 0.4},
        "avg_confidence_score": {"target": 6.5, "unit": "score", "weight": 0.3},
        "staleness_detection": {"target": 90, "unit": "%", "weight": 0.2},
        "end_client_deduction": {"target": 70, "unit": "%", "weight": 0.1},
    },
    "Z": {
        "crm_update_latency": {"target": 4, "unit": "hours", "weight": 0.3},
        "duplicate_detection_rate": {"target": 1, "unit": "%", "weight": 0.2},
        "hotlist_publication_time": {"target": "07:00", "unit": "time", "weight": 0.25},
        "data_completeness": {"target": 95, "unit": "%", "weight": 0.25},
    },
    "Rick": {
        "matching_cycle_completion": {"target": "08:30", "unit": "time", "weight": 0.25},
        "avg_match_score": {"target": 75, "unit": "score", "weight": 0.3},
        "trifecta_pass_rate": {"target": 95, "unit": "%", "weight": 0.25},
        "inbound_response_time": {"target": 60, "unit": "minutes", "weight": 0.2},
    },
    "Leroy": {
        "apps_executed_eod": {"target": 100, "unit": "%", "weight": 0.3},
        "profiles_green_state": {"target": 80, "unit": "%", "weight": 0.25},
        "inbound_detection_latency": {"target": 15, "unit": "minutes", "weight": 0.25},
        "execution_errors": {"target": 0, "unit": "errors/week", "weight": 0.2},
    },
}


def load_quota_config() -> Dict[str, Any]:
    """Load quota configuration (can be overridden by human approval)."""
    if QUOTA_CONFIG_FILE.exists():
        with open(QUOTA_CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"quotas": QUOTA_DEFINITIONS, "version": "1.0"}


def calculate_quota_compliance(agent_id: str, daily_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate quota compliance for a single agent on a given day.

    Args:
        agent_id: "Jay", "Z", "Rick", or "Leroy"
        daily_metrics: Dict with actual values for each quota metric.
            Example: {"jobs_researched": 18, "avg_confidence_score": 7.1, ...}

    Returns:
        Compliance report with: agent, date, quotas (each with target/actual/status), overall status, intervention level
    """
    config = load_quota_config()
    quotas_def = config["quotas"].get(agent_id, {})

    compliance_report = {
        "agent": agent_id,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "quotas": [],
        "overall_status": "MET",
        "intervention_level": "NONE"
    }

    met_count = 0
    miss_count = 0

    for metric_name, metric_def in quotas_def.items():
        target = metric_def["target"]
        actual = daily_metrics.get(metric_name, None)
        unit = metric_def.get("unit", "")

        if actual is None:
            status = "NO_DATA"
            pct_of_target = None
        else:
            # Determine if metric was met (logic depends on metric type)
            if "latency" in metric_name or "time" in metric_name:
                # For latency/time, lower is better
                if isinstance(actual, str) and isinstance(target, str):
                    # Time string comparison (HH:MM)
                    status = "MET" if actual <= target else "MISS"
                else:
                    # Numeric latency
                    status = "MET" if actual <= target else "MISS"
                pct_of_target = round((target / actual * 100), 1) if actual > 0 else None
            elif "error" in metric_name:
                # For error counts, lower is better (zero is ideal)
                status = "MET" if actual <= target else "MISS"
                pct_of_target = round((target / actual * 100), 1) if actual > 0 else None
            else:
                # For rates/percentages/counts, higher is better
                if metric_name == "duplicate_detection_rate":
                    # Special case: lower detection rate is worse
                    status = "MET" if actual <= target else "MISS"
                else:
                    status = "MET" if actual >= target else "MISS"
                pct_of_target = round((actual / target * 100), 1) if target > 0 else None

            if status == "MET":
                met_count += 1
            else:
                miss_count += 1

        quota_entry = {
            "metric": metric_name,
            "target": target,
            "actual": actual,
            "unit": unit,
            "status": status,
            "pct_of_target": pct_of_target
        }
        compliance_report["quotas"].append(quota_entry)

    # Overall status
    if miss_count > 0:
        compliance_report["overall_status"] = "MISS"
    else:
        compliance_report["overall_status"] = "MET"

    # Intervention level (determined separately, outside this function)
    compliance_report["intervention_level"] = "PENDING_HISTORICAL_ANALYSIS"

    return compliance_report


def calculate_intervention_level(agent_id: str, compliance_history: List[Dict[str, Any]]) -> str:
    """
    Determine intervention level based on historical compliance.

    4-level ladder:
    1. OBSERVE: First miss
    2. DIAGNOSE: 2 consecutive or 3 in week
    3. INTERVENE: Persistent problem (4+ in week or 3+ consecutive)
    4. REBUILD: Fundamental failure (5+ in week)

    Args:
        agent_id: Agent ID
        compliance_history: List of compliance reports (ordered by date, most recent last)

    Returns:
        Intervention level string
    """
    if not compliance_history:
        return "NONE"

    # Count misses in recent history
    recent_misses = [c for c in compliance_history[-7:] if c.get("overall_status") == "MISS"]
    miss_count = len(recent_misses)

    if miss_count == 0:
        return "NONE"
    elif miss_count == 1:
        return "OBSERVE"
    elif miss_count <= 3:
        # Check if consecutive
        last_3 = compliance_history[-3:]
        consecutive_misses = sum(1 for c in last_3 if c.get("overall_status") == "MISS")
        if consecutive_misses >= 2:
            return "DIAGNOSE"
        else:
            return "OBSERVE"
    elif miss_count <= 4:
        return "INTERVENE"
    else:
        return "REBUILD"


def generate_daily_compliance_report() -> Dict[str, Any]:
    """
    Generate compliance report for all agents (run daily at 17:00).

    Returns:
        Dict with per-agent compliance and recommended interventions
    """
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "agents": {},
        "interventions_needed": [],
        "summary": ""
    }

    agents = ["Jay", "Z", "Rick", "Leroy"]

    for agent_id in agents:
        # For demo: use placeholder metrics
        # In production, these come from agent activity logs
        daily_metrics = _get_daily_metrics(agent_id)
        compliance = calculate_quota_compliance(agent_id, daily_metrics)

        # Get historical compliance (for intervention level)
        history = _load_compliance_history(agent_id, days=7)
        intervention_level = calculate_intervention_level(agent_id, history)
        compliance["intervention_level"] = intervention_level

        report["agents"][agent_id] = compliance

        # Add to interventions list if needed
        if intervention_level in ["DIAGNOSE", "INTERVENE", "REBUILD"]:
            report["interventions_needed"].append({
                "agent": agent_id,
                "level": intervention_level,
                "status": compliance["overall_status"],
                "misses_this_week": len([c for c in history[-7:] if c.get("overall_status") == "MISS"])
            })

        # Log compliance
        _log_compliance(compliance)

    return report


def _get_daily_metrics(agent_id: str) -> Dict[str, Any]:
    """Placeholder: fetch daily metrics from agent logs. In production, parse activity logs."""
    # Demo data
    demo_metrics = {
        "Jay": {
            "jobs_researched": 22,
            "avg_confidence_score": 7.3,
            "staleness_detection": 92,
            "end_client_deduction": 75,
        },
        "Z": {
            "crm_update_latency": 2.5,
            "duplicate_detection_rate": 0.5,
            "hotlist_publication_time": "06:55",
            "data_completeness": 96,
        },
        "Rick": {
            "matching_cycle_completion": "08:20",
            "avg_match_score": 78,
            "trifecta_pass_rate": 96,
            "inbound_response_time": 40,
        },
        "Leroy": {
            "apps_executed_eod": 100,
            "profiles_green_state": 85,
            "inbound_detection_latency": 10,
            "execution_errors": 0,
        },
    }
    return demo_metrics.get(agent_id, {})


def _load_compliance_history(agent_id: str, days: int = 7) -> List[Dict[str, Any]]:
    """Load compliance history for an agent (last N days)."""
    if not QUOTA_PERFORMANCE_LOG.exists():
        return []

    history = []
    try:
        with open(QUOTA_PERFORMANCE_LOG, "r") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    if entry.get("agent") == agent_id:
                        history.append(entry)

        # Filter to last N days
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        history = [
            h for h in history
            if datetime.fromisoformat(h.get("timestamp", "")) >= cutoff
        ]

        return history
    except Exception as e:
        return []


def _log_compliance(compliance: Dict[str, Any]):
    """Log compliance report to quota performance log."""
    log_entry = {
        "event_type": "quota_compliance",
        "timestamp": compliance["timestamp"],
        "agent": compliance["agent"],
        "date": compliance["date"],
        "overall_status": compliance["overall_status"],
        "intervention_level": compliance["intervention_level"],
        "quotas": compliance["quotas"]
    }

    with open(QUOTA_PERFORMANCE_LOG, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Also log to system history
    history_entry = {
        "event_type": "quota_check",
        "timestamp": compliance["timestamp"],
        "agent": compliance["agent"],
        "status": compliance["overall_status"],
        "intervention_level": compliance["intervention_level"]
    }

    with open(SYSTEM_HISTORY, "a") as f:
        f.write(json.dumps(history_entry) + "\n")


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Calculate compliance for specific agent
        agent_id = sys.argv[1]
        metrics = _get_daily_metrics(agent_id)
        compliance = calculate_quota_compliance(agent_id, metrics)
        print(json.dumps(compliance, indent=2))
    else:
        # Generate daily compliance report for all agents
        report = generate_daily_compliance_report()
        print(json.dumps(report, indent=2))
