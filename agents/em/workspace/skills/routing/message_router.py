"""
Message Router for EM
=====================
Routes messages between agents (Jay, Z, Rick, Leroy) based on dependency graph and business rules.
All inter-agent communication flows through EM. EM is the message broker.

Usage:
    from message_router import route_message, SystemState

    state = SystemState()
    decision = route_message(envelope, state)
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any


RULES_FILE = Path(__file__).parent / "routing_rules.json"
ROUTING_LOG_FILE = Path(__file__).parent.parent.parent / "memory" / "routing-log.jsonl"
AGENT_FEED_FILE = Path(__file__).parent.parent.parent / "memory" / "agent-feed.jsonl"


class SystemState:
    """Represents the current system state (agent states, queues, data freshness)."""

    def __init__(self):
        self.agent_states = {
            "Z": {"state": "ACTIVE", "last_activity": datetime.now(timezone.utc), "queue_depth": 0},
            "Jay": {"state": "ACTIVE", "last_activity": datetime.now(timezone.utc), "queue_depth": 0},
            "Rick": {"state": "ACTIVE", "last_activity": datetime.now(timezone.utc), "queue_depth": 0},
            "Leroy": {"state": "ACTIVE", "last_activity": datetime.now(timezone.utc), "queue_depth": 0},
        }
        self.data_freshness = {
            "Z_data_age_minutes": 0,  # How old is Z's CRM data?
        }
        self.message_queue = {}  # Per-agent message queues for holding

    def agent_is_healthy(self, agent_id: str) -> bool:
        """Check if agent is responsive and not in error state."""
        agent = self.agent_states.get(agent_id, {})
        state = agent.get("state", "UNKNOWN")
        last_activity = agent.get("last_activity", datetime.now(timezone.utc))

        # DEAD if no activity in >30 min
        if (datetime.now(timezone.utc) - last_activity).total_seconds() > 1800:
            return False

        # Not healthy if ERROR
        if state in ["ERROR", "DEAD"]:
            return False

        return True

    def agent_queue_depth(self, agent_id: str) -> int:
        """Get queue depth for agent."""
        return self.agent_states.get(agent_id, {}).get("queue_depth", 0)

    def z_data_is_fresh(self, max_age_minutes: int = 240) -> bool:
        """Check if Z's data is recent (<4 hours by default)."""
        return self.data_freshness.get("Z_data_age_minutes", 0) <= max_age_minutes

    def update_agent_activity(self, agent_id: str, timestamp: datetime = None):
        """Record agent activity timestamp."""
        if agent_id in self.agent_states:
            self.agent_states[agent_id]["last_activity"] = timestamp or datetime.now(timezone.utc)


def load_rules() -> Dict[str, Any]:
    """Load routing rules from JSON config."""
    with open(RULES_FILE, "r") as f:
        return json.load(f)


def evaluate_dependency_graph(from_agent: str, to_agent: str, message_type: str, rules: Dict) -> tuple[bool, str]:
    """
    Check if message can be routed given dependency graph.
    Returns (can_route: bool, reason: str).
    """
    dep_graph = rules.get("dependency_graph", {})

    if to_agent not in dep_graph:
        return False, f"Unknown target agent: {to_agent}"

    target_agent_config = dep_graph[to_agent]

    # Check if message type matches expected input
    expected_inputs = target_agent_config.get("inputs", [])

    # For submission requests, check if inputs are ready
    if message_type == "SUBMISSION_REQUEST":
        # Rick expects input from Jay + Z's approval
        if to_agent == "Rick":
            expected = "Jay.SUBMISSION_REQUESTS + Z approval"
            return True, f"Rick can accept submission requests from {from_agent}"

        # Leroy expects input from Rick + Z approval
        if to_agent == "Leroy":
            expected = "Rick.POSITIONED_APPLICATIONS + Z approval"
            return True, f"Leroy can accept approved applications"

    return True, f"Dependency check passed for {from_agent} → {to_agent}"


def check_z_safety_gate(state: SystemState) -> tuple[bool, str]:
    """
    Z is a critical safety gate. If Z is DEAD/ERROR, no submissions can be routed.
    Returns (can_route: bool, reason: str).
    """
    z_state = state.agent_states.get("Z", {}).get("state", "UNKNOWN")

    if z_state in ["DEAD", "ERROR"]:
        return False, f"Z is in {z_state} state. Cannot route submissions without data validation gate."

    return True, "Z safety gate check passed"


def evaluate_rules(envelope: Dict[str, Any], state: SystemState, rules: Dict) -> Dict[str, Any]:
    """
    Evaluate routing rules against message envelope and system state.
    Returns routing decision.
    """
    from_agent = envelope.get("from", "UNKNOWN")
    to_agent = envelope.get("to", "UNKNOWN")
    message_type = envelope.get("type", "REQUEST")
    priority = envelope.get("priority", "NORMAL")

    # Rule 1: Check Z safety gate for submissions
    if message_type == "SUBMISSION_REQUEST":
        can_route, reason = check_z_safety_gate(state)
        if not can_route:
            return {
                "routing_decision": "ESCALATE_TO_HUMAN",
                "reason": reason,
                "severity": "CRITICAL",
                "target": "human"
            }

    # Rule 2: URGENT messages always route immediately (if target is healthy)
    if priority == "URGENT":
        if state.agent_is_healthy(to_agent):
            return {
                "routing_decision": "ROUTE_IMMEDIATELY",
                "reason": f"URGENT priority message from {from_agent} and target {to_agent} is healthy",
                "target": to_agent
            }
        else:
            return {
                "routing_decision": "ESCALATE_TO_HUMAN",
                "reason": f"URGENT message to {to_agent} but target is not healthy",
                "severity": "CRITICAL",
                "target": "human"
            }

    # Rule 3: ALERT messages route to human immediately
    if message_type == "ALERT":
        severity = envelope.get("payload", {}).get("severity", "MEDIUM")
        if severity in ["CRITICAL", "HIGH"]:
            return {
                "routing_decision": "ESCALATE_TO_HUMAN",
                "reason": f"{severity} severity alert from {from_agent}",
                "severity": severity,
                "target": "human",
                "channel": "#alerts"
            }

    # Rule 4: Check if target agent is healthy
    if not state.agent_is_healthy(to_agent):
        return {
            "routing_decision": "ESCALATE_TO_HUMAN",
            "reason": f"Target agent {to_agent} is not healthy. Last activity: {state.agent_states[to_agent].get('last_activity')}",
            "severity": "HIGH",
            "target": "human"
        }

    # Rule 5: Check dependencies
    can_route, reason = evaluate_dependency_graph(from_agent, to_agent, message_type, rules)
    if not can_route:
        return {
            "routing_decision": "HOLD_PENDING_INPUT",
            "reason": reason,
            "target": to_agent
        }

    # Rule 6: Check queue depth (don't overload Rick)
    if to_agent == "Rick" and state.agent_queue_depth("Rick") > 30:
        return {
            "routing_decision": "HOLD_PENDING_CAPACITY",
            "reason": f"Rick queue depth ({state.agent_queue_depth('Rick')}) exceeds threshold (30)",
            "target": "Rick"
        }

    # Rule 7: Check Z data freshness before routing submissions
    if to_agent == "Z" and message_type == "SUBMISSION_REQUEST":
        if not state.z_data_is_fresh(max_age_minutes=240):  # 4 hours
            return {
                "routing_decision": "HOLD_PENDING_INPUT",
                "reason": f"Z data is too old ({state.data_freshness['Z_data_age_minutes']} min). Hold until fresh data available.",
                "target": "Z"
            }

    # Default: route immediately
    return {
        "routing_decision": "ROUTE_IMMEDIATELY",
        "reason": f"All checks passed. Route {from_agent} → {to_agent}",
        "target": to_agent
    }


def route_message(envelope: Dict[str, Any], state: SystemState = None) -> Dict[str, Any]:
    """
    Main routing function. Takes a message envelope and returns routing decision.

    Args:
        envelope: Message with keys: from, to, type, priority, timestamp, reference, payload, context
        state: SystemState object. If None, creates a default state.

    Returns:
        Routing decision dict with keys: routing_decision, target, reason, timestamp, etc.
    """
    if state is None:
        state = SystemState()

    rules = load_rules()

    # Get routing decision
    decision = evaluate_rules(envelope, state, rules)

    # Add metadata
    decision["message_id"] = f"MSG-{datetime.now(timezone.utc).strftime('%s')}"
    decision["original_from"] = envelope.get("from", "UNKNOWN")
    decision["original_to"] = envelope.get("to", "UNKNOWN")
    decision["message_type"] = envelope.get("type", "REQUEST")
    decision["priority"] = envelope.get("priority", "NORMAL")
    decision["reference"] = envelope.get("reference", "")
    decision["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Set SLA expectation
    if decision.get("routing_decision") == "ROUTE_IMMEDIATELY":
        if envelope.get("priority") == "URGENT":
            decision["sla"] = "Response within 15 minutes"
        elif envelope.get("priority") == "HIGH":
            decision["sla"] = "Response within 30 minutes"
        else:
            decision["sla"] = "Response within 4 hours"

    # Log decision
    _log_routing_decision(decision, envelope)

    # Update system state
    state.update_agent_activity(envelope.get("from", "UNKNOWN"), datetime.fromisoformat(envelope.get("timestamp", datetime.now(timezone.utc).isoformat())))

    return decision


def _log_routing_decision(decision: Dict[str, Any], envelope: Dict[str, Any]):
    """Log routing decision to routing log and agent feed."""

    # Write to routing log
    log_entry = {
        "event_type": "routing_decision",
        "timestamp": decision["timestamp"],
        "message_id": decision.get("message_id", ""),
        "from": envelope.get("from", ""),
        "to": envelope.get("to", ""),
        "routing_decision": decision.get("routing_decision", ""),
        "reason": decision.get("reason", ""),
        "reference": envelope.get("reference", "")
    }

    with open(ROUTING_LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Write to agent feed (for transparency/audit trail)
    feed_entry = {
        "event_type": "message",
        "timestamp": decision["timestamp"],
        "from": envelope.get("from", ""),
        "to": envelope.get("to", ""),
        "type": envelope.get("type", ""),
        "priority": envelope.get("priority", ""),
        "routing_decision": decision.get("routing_decision", ""),
        "reference": envelope.get("reference", "")
    }

    with open(AGENT_FEED_FILE, "a") as f:
        f.write(json.dumps(feed_entry) + "\n")


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    # Demo: Route a sample submission request
    state = SystemState()

    envelope = {
        "from": "Jay",
        "to": "Z",
        "type": "SUBMISSION_REQUEST",
        "priority": "NORMAL",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reference": "SUBM-C042-001",
        "payload": {
            "consultant_id": "C-042",
            "job_posting_id": "LI-9876",
            "vendor": "TrueBlue",
            "end_client": "Microsoft",
            "confidence_score": 8.2
        },
        "context": "Jay completed research, confidence >6.5"
    }

    decision = route_message(envelope, state)
    print(json.dumps(decision, indent=2))
