"""
Heartbeat Poller for EM
=======================
Monitors agent health every 15 minutes during business hours.
Checks: responsiveness, current task, task duration, errors/warnings.

Usage:
    from heartbeat_poller import poll_agent_health

    health = poll_agent_health("Z")
    # health = {
    #   "agent": "Z",
    #   "state": "ACTIVE",
    #   "last_activity": "2025-02-15T09:00:00Z",
    #   "time_since_activity_minutes": 5,
    #   "current_task": "processing_crm_data",
    #   "task_duration_minutes": 8,
    #   "expected_duration_minutes": 120,
    #   "errors": [],
    #   "recommended_action": "continue_monitoring"
    # }
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any


AGENT_ACTIVITY_LOG = Path(__file__).parent.parent.parent / "memory" / "agent-activity-log.jsonl"
SYSTEM_HISTORY = Path(__file__).parent.parent.parent / "memory" / "system-history.jsonl"

# Expected task durations (in minutes) as baseline
EXPECTED_DURATIONS = {
    "Z": {
        "processing_crm_data": 120,
        "publishing_hotlist": 30,
        "validating_submission": 5,
    },
    "Jay": {
        "researching_jobs": 180,
        "generating_submission_request": 15,
    },
    "Rick": {
        "matching_cycle": 360,
        "positioning_application": 10,
        "trifecta_verification": 5,
    },
    "Leroy": {
        "executing_application": 3,
        "profile_health_check": 60,
        "inbound_lead_detection": 1,
    },
}


class AgentHealth:
    """Represents health status of an agent."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.state = "UNKNOWN"  # ACTIVE, IDLE, BUSY, SLOW, ERROR, DEAD
        self.last_activity = None
        self.time_since_activity_minutes = None
        self.current_task = None
        self.task_duration_minutes = None
        self.expected_duration_minutes = None
        self.errors = []
        self.warnings = []
        self.recommended_action = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "agent": self.agent_id,
            "state": self.state,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "time_since_activity_minutes": self.time_since_activity_minutes,
            "current_task": self.current_task,
            "task_duration_minutes": self.task_duration_minutes,
            "expected_duration_minutes": self.expected_duration_minutes,
            "errors": self.errors,
            "warnings": self.warnings,
            "recommended_action": self.recommended_action,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


def read_agent_activity_log(agent_id: str, last_n_entries: int = 10) -> List[Dict[str, Any]]:
    """Read recent activity log entries for an agent."""
    if not AGENT_ACTIVITY_LOG.exists():
        return []

    entries = []
    try:
        with open(AGENT_ACTIVITY_LOG, "r") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    if entry.get("agent") == agent_id:
                        entries.append(entry)

        # Return last N entries
        return entries[-last_n_entries:]
    except Exception as e:
        return []


def poll_agent_health(agent_id: str) -> AgentHealth:
    """
    Poll health of a single agent.

    Returns AgentHealth object with state, last activity, current task, recommended action.
    """
    health = AgentHealth(agent_id)

    # Read recent activity log
    activities = read_agent_activity_log(agent_id, last_n_entries=5)

    if not activities:
        # No activity found
        health.state = "DEAD"
        health.last_activity = datetime.now(timezone.utc) - timedelta(hours=1)
        health.time_since_activity_minutes = 60
        health.errors = ["No activity detected in log"]
        health.recommended_action = "CRITICAL: Trigger restart from backup"
        return health

    # Latest activity
    latest = activities[-1]
    health.last_activity = datetime.fromisoformat(latest.get("timestamp", datetime.now(timezone.utc).isoformat()))
    time_since = (datetime.now(timezone.utc) - health.last_activity).total_seconds() / 60
    health.time_since_activity_minutes = round(time_since)

    # Determine state based on time since last activity
    if time_since < 15:
        health.state = "ACTIVE"
    elif time_since < 45:
        health.state = "IDLE"
    elif time_since < 90:
        health.state = "BUSY"
    elif time_since < 180:
        health.state = "SLOW"
    else:
        health.state = "ERROR"

    # Extract current task info
    health.current_task = latest.get("action", "unknown")
    health.task_duration_minutes = latest.get("duration_minutes", None)

    # Get expected duration baseline
    expected = EXPECTED_DURATIONS.get(agent_id, {}).get(health.current_task, None)
    health.expected_duration_minutes = expected

    # Check for task duration anomalies
    if expected and health.task_duration_minutes:
        if health.task_duration_minutes > expected * 2:
            health.state = "SLOW"
            health.warnings.append(f"Task '{health.current_task}' taking {health.task_duration_minutes}min (expected {expected}min)")

    # Extract errors
    if latest.get("status") == "ERROR":
        health.errors = latest.get("errors", ["Unknown error"])
        health.state = "ERROR"

    # Recommend action
    if health.state == "ACTIVE":
        health.recommended_action = "Continue monitoring"
    elif health.state == "IDLE":
        health.recommended_action = "Normal (waiting for input)"
    elif health.state == "BUSY":
        health.recommended_action = "Monitor closely (task in progress)"
    elif health.state == "SLOW":
        health.recommended_action = "HIGH: Investigate root cause, notify human if >1 hour"
    elif health.state == "ERROR":
        health.recommended_action = "HIGH: Attempt auto-recovery (retry task), escalate if persistent"
    else:
        health.recommended_action = "CRITICAL: Trigger restart from backup"

    return health


def poll_all_agents() -> Dict[str, AgentHealth]:
    """Poll health of all agents."""
    agents = ["Z", "Jay", "Rick", "Leroy"]
    health_report = {}

    for agent_id in agents:
        health_report[agent_id] = poll_agent_health(agent_id)

    return health_report


def _log_health_check(health_dict: Dict[str, Any]):
    """Log health check to system history."""
    log_entry = {
        "event_type": "health_check",
        "timestamp": health_dict["timestamp"],
        "agent": health_dict["agent"],
        "state": health_dict["state"],
        "last_activity": health_dict["last_activity"],
        "time_since_activity_minutes": health_dict["time_since_activity_minutes"],
        "errors": health_dict["errors"],
        "warnings": health_dict["warnings"],
        "recommended_action": health_dict["recommended_action"]
    }

    with open(SYSTEM_HISTORY, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def check_and_alert(health_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Given a health check result, determine if alerts should be raised.
    Returns list of alerts.
    """
    alerts = []

    agent = health_dict["agent"]
    state = health_dict["state"]
    warnings = health_dict.get("warnings", [])
    errors = health_dict.get("errors", [])

    # CRITICAL: Agent is DEAD
    if state == "DEAD":
        alerts.append({
            "severity": "CRITICAL",
            "agent": agent,
            "event": "AGENT_DEAD",
            "message": f"{agent} has no activity for >30 minutes. Trigger restart immediately.",
            "channel": "#alerts",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    # HIGH: Agent is in ERROR state
    if state == "ERROR":
        alerts.append({
            "severity": "HIGH",
            "agent": agent,
            "event": "AGENT_ERROR",
            "message": f"{agent} is in ERROR state. Errors: {errors}. Attempt auto-recovery.",
            "channel": "#alerts",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    # MEDIUM: Agent is SLOW >30 min
    if state == "SLOW" and health_dict.get("time_since_activity_minutes", 0) > 30:
        alerts.append({
            "severity": "MEDIUM",
            "agent": agent,
            "event": "AGENT_SLOW",
            "message": f"{agent} is SLOW (>2x expected duration). Investigate root cause.",
            "channel": "#em-dashboard",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    # Log warnings
    for warning in warnings:
        alerts.append({
            "severity": "MEDIUM",
            "agent": agent,
            "event": "AGENT_WARNING",
            "message": warning,
            "channel": "#em-dashboard",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    return alerts


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Poll specific agent
        agent_id = sys.argv[1]
        health = poll_agent_health(agent_id)
        print(json.dumps(health.to_dict(), indent=2))
    else:
        # Poll all agents
        report = poll_all_agents()
        result = {
            agent_id: health.to_dict()
            for agent_id, health in report.items()
        }
        print(json.dumps(result, indent=2))
