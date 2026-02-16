"""
Alert Generator for EM
======================
Threshold-based alerting for critical events: profile bans, visa urgency, duplicates, agent failures, data quality issues.

Usage:
    from alert_generator import generate_alert

    alert = generate_alert(
        event_type="PROFILE_BAN",
        agent="Leroy",
        details={"profile_id": "LI-001", "reason": "rate_limit_exceeded"}
    )
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional


ALERTS_LOG = Path(__file__).parent.parent.parent / "memory" / "alerts-log.jsonl"
SYSTEM_HISTORY = Path(__file__).parent.parent.parent / "memory" / "system-history.jsonl"


# Alert templates with severity, channel, and recommended action
ALERT_TEMPLATES = {
    "PROFILE_BAN": {
        "severity": "CRITICAL",
        "channel": "#og-alerts",
        "title": "LinkedIn Profile Ban Detected",
        "description": "Profile {profile_id} has been restricted or banned by LinkedIn.",
        "recommended_action": "Rotate to backup profile immediately. Review profile usage pattern for rate limit violations.",
        "escalation": True
    },
    "VISA_EXPIRING_SOON": {
        "severity": "HIGH",
        "channel": "#og-alerts",
        "title": "Visa Expiration Alert",
        "description": "Consultant {consultant_id} visa expiring in {days_remaining} days.",
        "recommended_action": "Prioritize for immediate submission. Increase research intensity.",
        "escalation": True
    },
    "DUPLICATE_SUBMISSION": {
        "severity": "CRITICAL",
        "channel": "#og-alerts",
        "title": "Duplicate Submission Detected (Data Integrity Breach)",
        "description": "Consultant {consultant_id} submitted to {client} via {vendor1} and {vendor2} within 90 days.",
        "recommended_action": "Block second submission. Analyze conflict. Report to client.",
        "escalation": True
    },
    "AGENT_DEAD": {
        "severity": "CRITICAL",
        "channel": "#og-alerts",
        "title": "Agent Unresponsive (DEAD)",
        "description": "Agent {agent_id} has no activity for >30 minutes.",
        "recommended_action": "Trigger restart from backup immediately. Verify data integrity.",
        "escalation": True
    },
    "AGENT_ERROR": {
        "severity": "HIGH",
        "channel": "#og-alerts",
        "title": "Agent Error State",
        "description": "Agent {agent_id} encountered error: {error_message}",
        "recommended_action": "Attempt auto-recovery (retry task). If persistent, escalate to human.",
        "escalation": True
    },
    "AGENT_SLOW": {
        "severity": "MEDIUM",
        "channel": "#og-em-dashboard",
        "title": "Agent Running Slow",
        "description": "Agent {agent_id} task '{task}' taking {duration}min (expected {expected}min).",
        "recommended_action": "Investigate root cause. Check queue depth and system resources.",
        "escalation": False
    },
    "DATA_QUALITY_LOW": {
        "severity": "MEDIUM",
        "channel": "#og-em-dashboard",
        "title": "Data Quality Below Threshold",
        "description": "Data quality score: {score}% (target >95%). {details}",
        "recommended_action": "Trigger audit. Identify missing/invalid fields. Schedule fixing.",
        "escalation": False
    },
    "QUOTA_MISS": {
        "severity": "HIGH",
        "channel": "#og-alerts",
        "title": "Quota Miss Alert",
        "description": "Agent {agent_id} missed quota '{quota_name}': {actual} vs {target} target.",
        "recommended_action": "Diagnose root cause. Check for input delays or processing issues.",
        "escalation": True
    },
    "CRM_DATA_STALE": {
        "severity": "HIGH",
        "channel": "#og-alerts",
        "title": "CRM Data Stale (>4 hours)",
        "description": "Z's CRM data is {age_hours} hours old. May impact downstream accuracy.",
        "recommended_action": "Trigger CRM import. Notify Z to process fresh data.",
        "escalation": True
    },
    "INBOUND_RESPONSE_SLA_MISS": {
        "severity": "MEDIUM",
        "channel": "#og-em-dashboard",
        "title": "Inbound Response SLA Miss",
        "description": "Inbound lead from {client} waiting {time_minutes}min. SLA: 60min.",
        "recommended_action": "Escalate to Rick. Prioritize positioning.",
        "escalation": False
    },
}


class Alert:
    """Represents a single alert event."""

    def __init__(
        self,
        event_type: str,
        severity: str,
        channel: str,
        title: str,
        description: str,
        agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        recommended_action: Optional[str] = None,
    ):
        self.event_type = event_type
        self.severity = severity
        self.channel = channel
        self.title = title
        self.description = description
        self.agent = agent
        self.details = details or {}
        self.recommended_action = recommended_action
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.alert_id = f"ALERT-{self.timestamp.replace(':', '').replace('-', '')}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "alert_id": self.alert_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "severity": self.severity,
            "channel": self.channel,
            "title": self.title,
            "description": self.description,
            "agent": self.agent,
            "details": self.details,
            "recommended_action": self.recommended_action,
        }

    def to_slack_message(self) -> str:
        """Format alert for Slack posting."""
        severity_emoji = {
            "CRITICAL": "🚨",
            "HIGH": "⚠️",
            "MEDIUM": "⚡",
            "LOW": "ℹ️",
        }.get(self.severity, "📢")

        message = f"{severity_emoji} **{self.title}**\n"
        message += f"{self.description}\n"
        if self.recommended_action:
            message += f"_Recommended action: {self.recommended_action}_"

        return message


def generate_alert(
    event_type: str,
    agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Optional[Alert]:
    """
    Generate an alert based on event type and details.

    Args:
        event_type: Type of event (e.g., "PROFILE_BAN", "VISA_EXPIRING_SOON")
        agent: Agent ID (if applicable)
        details: Details dict with values to interpolate in templates

    Returns:
        Alert object, or None if event_type not recognized
    """
    template = ALERT_TEMPLATES.get(event_type)
    if not template:
        return None

    details = details or {}

    # Interpolate description and recommended action with details
    description = template["description"].format(**details)
    recommended_action = template["recommended_action"].format(**details)

    alert = Alert(
        event_type=event_type,
        severity=template["severity"],
        channel=template["channel"],
        title=template["title"],
        description=description,
        agent=agent,
        details=details,
        recommended_action=recommended_action,
    )

    return alert


def should_escalate(alert: Alert) -> bool:
    """Check if alert should escalate to human (not just logged)."""
    template = ALERT_TEMPLATES.get(alert.event_type, {})
    return template.get("escalation", False) or alert.severity in ["CRITICAL", "HIGH"]


def log_alert(alert: Alert):
    """Log alert to alerts log, system history, and Slack."""
    # Write to alerts log
    with open(ALERTS_LOG, "a") as f:
        f.write(json.dumps(alert.to_dict()) + "\n")

    # Also log to system history
    history_entry = {
        "event_type": "alert",
        "timestamp": alert.timestamp,
        "alert_id": alert.alert_id,
        "event_type_source": alert.event_type,
        "severity": alert.severity,
        "agent": alert.agent,
    }

    with open(SYSTEM_HISTORY, "a") as f:
        f.write(json.dumps(history_entry) + "\n")

    # Post to Slack
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "shared"))
        from slack_client import post_alert as _post_alert
        _post_alert(alert, agent=alert.agent or "EM")
    except Exception:
        pass  # Slack posting is best-effort; local log is the source of truth


def generate_profile_ban_alert(profile_id: str, reason: str) -> Alert:
    """Generate alert for profile ban."""
    alert = generate_alert(
        "PROFILE_BAN",
        agent="Leroy",
        details={"profile_id": profile_id, "reason": reason}
    )
    log_alert(alert)
    return alert


def generate_visa_urgency_alert(consultant_id: str, days_remaining: int) -> Alert:
    """Generate alert for visa expiring soon."""
    alert = generate_alert(
        "VISA_EXPIRING_SOON",
        agent="Z",
        details={"consultant_id": consultant_id, "days_remaining": days_remaining}
    )
    log_alert(alert)
    return alert


def generate_duplicate_submission_alert(
    consultant_id: str,
    client: str,
    vendor1: str,
    vendor2: str,
    days_apart: int
) -> Alert:
    """Generate alert for duplicate submission."""
    alert = generate_alert(
        "DUPLICATE_SUBMISSION",
        agent="Z",
        details={
            "consultant_id": consultant_id,
            "client": client,
            "vendor1": vendor1,
            "vendor2": vendor2,
            "days_apart": days_apart
        }
    )
    log_alert(alert)
    return alert


def generate_agent_dead_alert(agent_id: str, last_activity: str) -> Alert:
    """Generate alert for agent DEAD."""
    alert = generate_alert(
        "AGENT_DEAD",
        agent=agent_id,
        details={"agent_id": agent_id, "last_activity": last_activity}
    )
    log_alert(alert)
    return alert


def generate_agent_error_alert(agent_id: str, error_message: str) -> Alert:
    """Generate alert for agent ERROR."""
    alert = generate_alert(
        "AGENT_ERROR",
        agent=agent_id,
        details={"agent_id": agent_id, "error_message": error_message}
    )
    log_alert(alert)
    return alert


def generate_agent_slow_alert(agent_id: str, task: str, duration: int, expected: int) -> Alert:
    """Generate alert for agent SLOW."""
    alert = generate_alert(
        "AGENT_SLOW",
        agent=agent_id,
        details={"agent_id": agent_id, "task": task, "duration": duration, "expected": expected}
    )
    log_alert(alert)
    return alert


def generate_data_quality_alert(score: float, details: str) -> Alert:
    """Generate alert for low data quality."""
    alert = generate_alert(
        "DATA_QUALITY_LOW",
        agent="Z",
        details={"score": round(score, 1), "details": details}
    )
    log_alert(alert)
    return alert


def generate_quota_miss_alert(agent_id: str, quota_name: str, actual: float, target: float) -> Alert:
    """Generate alert for quota miss."""
    alert = generate_alert(
        "QUOTA_MISS",
        agent=agent_id,
        details={"agent_id": agent_id, "quota_name": quota_name, "actual": actual, "target": target}
    )
    log_alert(alert)
    return alert


def generate_crm_stale_alert(age_hours: float) -> Alert:
    """Generate alert for stale CRM data."""
    alert = generate_alert(
        "CRM_DATA_STALE",
        agent="Z",
        details={"age_hours": round(age_hours, 1)}
    )
    log_alert(alert)
    return alert


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    # Demo: Generate a few alerts
    alert1 = generate_profile_ban_alert("LI-001", "rate_limit_exceeded")
    alert2 = generate_visa_urgency_alert("C-042", 22)
    alert3 = generate_agent_slow_alert("Jay", "researching_jobs", 45, 20)

    print("Alert 1 (Profile Ban):")
    print(json.dumps(alert1.to_dict(), indent=2))
    print("\nAlert 2 (Visa Urgency):")
    print(json.dumps(alert2.to_dict(), indent=2))
    print("\nAlert 3 (Agent Slow):")
    print(json.dumps(alert3.to_dict(), indent=2))
    print("\nSlack message for Alert 1:")
    print(alert1.to_slack_message())
