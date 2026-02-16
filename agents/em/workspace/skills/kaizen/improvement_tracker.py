"""
Improvement Tracker for EM
==========================
Logs daily Kaizen observations and tracks improvements.

Usage:
    from improvement_tracker import log_kaizen_observation

    observation = {
        "category": "PROCESS",
        "observation": "Hot List publication time increased to 06:55 (added validation)",
        "root_cause": "Extra validation step protecting against data errors",
        "proposed_action": "Parallelize validation or refactor validation logic",
        "evidence": "Z's validation logs show +10min latency on large imports",
    }

    result = log_kaizen_observation(observation)
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any


KAIZEN_JOURNAL = Path(__file__).parent.parent.parent / "memory" / "kaizen-journal.md"
KAIZEN_LOG = Path(__file__).parent.parent.parent / "memory" / "kaizen-log.jsonl"
SYSTEM_HISTORY = Path(__file__).parent.parent.parent / "memory" / "system-history.jsonl"


CATEGORIES = ["PROCESS", "QUALITY", "SPEED", "COST", "RISK"]
STATUSES = ["PROPOSED", "APPROVED", "IMPLEMENTED", "REJECTED"]


def log_kaizen_observation(observation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Log a Kaizen observation.

    Args:
        observation_data: Dict with keys:
            - category: PROCESS, QUALITY, SPEED, COST, RISK
            - observation: What did we notice?
            - root_cause: Why does it matter?
            - proposed_action: What could we try?
            - evidence: Data supporting this

    Returns:
        Kaizen entry dict with metadata
    """
    timestamp = datetime.now(timezone.utc)
    date = timestamp.strftime("%Y-%m-%d")

    # Validate category
    category = observation_data.get("category", "PROCESS").upper()
    if category not in CATEGORIES:
        return {"error": f"Invalid category: {category}"}

    # Create Kaizen entry
    entry = {
        "date": date,
        "timestamp": timestamp.isoformat(),
        "kaizen_id": f"KZ-{date}-{timestamp.strftime('%H%M%S')}",
        "category": category,
        "observation": observation_data.get("observation", ""),
        "root_cause": observation_data.get("root_cause", ""),
        "proposed_action": observation_data.get("proposed_action", ""),
        "evidence": observation_data.get("evidence", ""),
        "status": "PROPOSED",
        "approval_date": None,
        "implementation_date": None,
        "result": None,
    }

    # Log to JSON log (for structured querying)
    _log_kaizen_json(entry)

    # Log to markdown journal (for human reading)
    _log_kaizen_markdown(entry)

    # Log to system history
    _log_to_system_history(entry)

    return entry


def update_kaizen_status(kaizen_id: str, new_status: str, notes: str = "") -> Dict[str, Any]:
    """
    Update status of a Kaizen observation (human approval/rejection).

    Args:
        kaizen_id: KZ-YYYY-MM-DD-HHMMSS
        new_status: PROPOSED, APPROVED, IMPLEMENTED, REJECTED
        notes: Optional notes

    Returns:
        Updated entry
    """
    if new_status not in STATUSES:
        return {"error": f"Invalid status: {new_status}"}

    # Read JSON log, find and update entry
    if not KAIZEN_LOG.exists():
        return {"error": "Kaizen log not found"}

    entries = []
    found = False

    try:
        with open(KAIZEN_LOG, "r") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    if entry.get("kaizen_id") == kaizen_id:
                        entry["status"] = new_status
                        if new_status == "APPROVED":
                            entry["approval_date"] = datetime.now(timezone.utc).isoformat()
                        elif new_status == "IMPLEMENTED":
                            entry["implementation_date"] = datetime.now(timezone.utc).isoformat()
                        if notes:
                            entry["notes"] = notes
                        found = True
                    entries.append(entry)
    except Exception as e:
        return {"error": f"Failed to update kaizen: {str(e)}"}

    if not found:
        return {"error": f"Kaizen ID not found: {kaizen_id}"}

    # Rewrite log
    try:
        with open(KAIZEN_LOG, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
    except Exception as e:
        return {"error": f"Failed to write kaizen log: {str(e)}"}

    return entries[-1] if entries else {}


def get_week_kaizen(days: int = 7) -> List[Dict[str, Any]]:
    """Get Kaizen observations from the past N days."""
    if not KAIZEN_LOG.exists():
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    observations = []

    try:
        with open(KAIZEN_LOG, "r") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    if datetime.fromisoformat(entry["timestamp"]) >= cutoff:
                        observations.append(entry)
    except Exception:
        pass

    return observations


def generate_kaizen_summary(days: int = 7) -> str:
    """Generate a markdown summary of Kaizen observations."""
    observations = get_week_kaizen(days)

    # Categorize
    by_category = {cat: [] for cat in CATEGORIES}
    for obs in observations:
        cat = obs.get("category", "PROCESS")
        by_category[cat].append(obs)

    summary = f"# Kaizen Log Summary (Last {days} Days)\n\n"

    for category in CATEGORIES:
        items = by_category[category]
        if items:
            summary += f"## {category}\n"
            for item in items:
                summary += f"- **{item['date']}:** {item['observation']}\n"
                summary += f"  Proposed: {item['proposed_action']}\n"
                summary += f"  Status: {item['status']}\n"
            summary += "\n"

    return summary


def _log_kaizen_json(entry: Dict[str, Any]):
    """Log Kaizen entry to JSON log (append-only)."""
    with open(KAIZEN_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _log_kaizen_markdown(entry: Dict[str, Any]):
    """Log Kaizen entry to markdown journal (for human reading)."""
    markdown_entry = f"""
### {entry['date']} | {entry['category']}

**Observation:** {entry['observation']}

**Root Cause:** {entry['root_cause']}

**Proposed Action:** {entry['proposed_action']}

**Evidence:** {entry['evidence']}

**Status:** {entry['status']}

---
"""

    with open(KAIZEN_JOURNAL, "a") as f:
        f.write(markdown_entry)


def _log_to_system_history(entry: Dict[str, Any]):
    """Log to system history."""
    history_entry = {
        "event_type": "kaizen",
        "timestamp": entry["timestamp"],
        "kaizen_id": entry["kaizen_id"],
        "category": entry["category"],
        "status": entry["status"]
    }

    system_history_file = Path(__file__).parent.parent.parent / "memory" / "system-history.jsonl"
    with open(system_history_file, "a") as f:
        f.write(json.dumps(history_entry) + "\n")


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys
    from datetime import timedelta

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "log":
            observation = {
                "category": "PROCESS",
                "observation": "Hot List publication time increased to 06:55 (added validation)",
                "root_cause": "Extra validation step protecting against data errors",
                "proposed_action": "Parallelize validation or refactor validation logic",
                "evidence": "Z's validation logs show +10min latency on large imports",
            }
            result = log_kaizen_observation(observation)
            print(json.dumps(result, indent=2))

        elif command == "summary":
            summary = generate_kaizen_summary(days=7)
            print(summary)

    else:
        # Demo: log a few observations
        observations = [
            {
                "category": "SPEED",
                "observation": "Rick's matching cycle hit 09:12 Wednesday. Sequential processing bottleneck.",
                "root_cause": "Trifecta checks are sequential, can't parallelize easily with current design",
                "proposed_action": "Refactor to parallel trifecta checking",
                "evidence": "Queue backlog 18 items, processing time >2x baseline"
            },
            {
                "category": "QUALITY",
                "observation": "Two duplicate submission near-misses this week (caught by Z)",
                "root_cause": "90-day rule requires querying full history, easy to miss edge cases",
                "proposed_action": "Add ML model to predict duplicate likelihood before submission",
                "evidence": "Z caught both before submission, but requires human vigilance"
            },
            {
                "category": "COST",
                "observation": "Jay's end-client deduction accuracy is 100%",
                "root_cause": "Jay carefully verifies company type and role relevance",
                "proposed_action": "Continue current process, measure cost savings",
                "evidence": "Cost saved by preventing bad-fit submissions: ~$2K/week"
            }
        ]

        for obs in observations:
            result = log_kaizen_observation(obs)
            print(f"Logged: {result.get('kaizen_id')}")

        print("\n" + "=" * 60 + "\n")
        summary = generate_kaizen_summary(days=7)
        print(summary)
