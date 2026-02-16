"""
Backup Agent for EM
===================
Executes automated backups on schedule: daily, weekly, and on-change.

Usage:
    from backup_agent import execute_daily_backup, execute_weekly_backup

    execute_daily_backup()  # Back up weights + memory files
    execute_weekly_backup()  # Full agent snapshots
"""

import json
import shutil
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any


BACKUP_SCHEDULE_FILE = Path(__file__).parent / "backup_schedule.json"
BACKUPS_ROOT = Path(__file__).parent.parent.parent / "backups"
AGENTS_ROOT = Path(__file__).parent.parent.parent.parent  # Up to /agents
SYSTEM_HISTORY = Path(__file__).parent.parent.parent / "memory" / "system-history.jsonl"


def load_backup_schedule() -> Dict[str, Any]:
    """Load backup schedule from JSON config."""
    with open(BACKUP_SCHEDULE_FILE, "r") as f:
        return json.load(f)


def execute_daily_backup() -> Dict[str, Any]:
    """
    Execute daily backup of weights and memory files.

    Returns:
        Backup result with status, files backed up, etc.
    """
    schedule = load_backup_schedule()
    daily_config = schedule.get("daily_backups", {})

    backup_dir = BACKUPS_ROOT / "daily" / datetime.now(timezone.utc).strftime("%Y-%m-%d")
    backup_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "backup_type": "daily",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "backup_dir": str(backup_dir),
        "files_backed_up": 0,
        "errors": [],
        "status": "SUCCESS"
    }

    # Back up weights and memory files for each agent
    agents = ["Z", "Jay", "Rick", "Leroy"]

    for agent in agents:
        agent_path = AGENTS_ROOT / agent / "workspace"
        if not agent_path.exists():
            result["errors"].append(f"Agent {agent} path not found: {agent_path}")
            continue

        # Back up scoring weights (if exist)
        weights_patterns = ["**/priority_weights.json", "**/scoring_weights.json"]
        for pattern in weights_patterns:
            for weights_file in agent_path.glob(pattern):
                try:
                    dest = backup_dir / agent / "weights" / weights_file.name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(weights_file, dest)
                    result["files_backed_up"] += 1
                except Exception as e:
                    result["errors"].append(f"Failed to back up {weights_file}: {str(e)}")

        # Back up memory files
        memory_path = agent_path / "memory"
        if memory_path.exists():
            try:
                dest_memory = backup_dir / agent / "memory"
                if dest_memory.exists():
                    shutil.rmtree(dest_memory)
                shutil.copytree(memory_path, dest_memory)
                result["files_backed_up"] += len(list(dest_memory.glob("**/*")))
            except Exception as e:
                result["errors"].append(f"Failed to back up memory for {agent}: {str(e)}")

    # Manage retention (keep last N days)
    retention_days = daily_config.get("retention_days", 30)
    _cleanup_old_backups(BACKUPS_ROOT / "daily", retention_days)

    if result["errors"]:
        result["status"] = "PARTIAL_SUCCESS" if result["files_backed_up"] > 0 else "FAILED"

    _log_backup(result)
    return result


def execute_weekly_backup() -> Dict[str, Any]:
    """
    Execute weekly full backup of all agent snapshots.

    Returns:
        Backup result with status, agents backed up, etc.
    """
    schedule = load_backup_schedule()
    weekly_config = schedule.get("weekly_backups", {})

    week_num = datetime.now(timezone.utc).isocalendar()
    week_str = f"{week_num[0]}-W{week_num[1]:02d}"
    backup_dir = BACKUPS_ROOT / "weekly" / week_str
    backup_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "backup_type": "weekly",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "backup_dir": str(backup_dir),
        "agents_backed_up": [],
        "errors": [],
        "status": "SUCCESS"
    }

    # Back up full agent snapshots
    agents = weekly_config.get("agents", ["Z", "Jay", "Rick", "Leroy"])

    for agent in agents:
        agent_path = AGENTS_ROOT / agent / "workspace"
        if not agent_path.exists():
            result["errors"].append(f"Agent {agent} path not found: {agent_path}")
            continue

        try:
            dest_agent = backup_dir / agent
            if dest_agent.exists():
                shutil.rmtree(dest_agent)
            shutil.copytree(agent_path, dest_agent)
            result["agents_backed_up"].append(agent)
        except Exception as e:
            result["errors"].append(f"Failed to back up agent {agent}: {str(e)}")

    # Manage retention (keep last N weeks)
    retention_weeks = weekly_config.get("retention_weeks", 12)
    _cleanup_old_backups(BACKUPS_ROOT / "weekly", retention_weeks * 7)

    if result["errors"]:
        result["status"] = "PARTIAL_SUCCESS" if result["agents_backed_up"] else "FAILED"

    _log_backup(result)
    return result


def execute_on_change_backup(trigger_reason: str) -> Dict[str, Any]:
    """
    Execute backup when system config is changed (human approval required).

    Args:
        trigger_reason: Why backup was triggered (e.g., "weight_adjustment", "rule_added")

    Returns:
        Backup result
    """
    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    backup_dir = BACKUPS_ROOT / "on-change" / timestamp_str
    backup_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "backup_type": "on-change",
        "trigger_reason": trigger_reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "backup_dir": str(backup_dir),
        "agents_backed_up": [],
        "errors": [],
        "status": "SUCCESS"
    }

    # Back up all agents (full snapshots)
    agents = ["Z", "Jay", "Rick", "Leroy"]

    for agent in agents:
        agent_path = AGENTS_ROOT / agent / "workspace"
        if not agent_path.exists():
            result["errors"].append(f"Agent {agent} path not found: {agent_path}")
            continue

        try:
            dest_agent = backup_dir / agent
            shutil.copytree(agent_path, dest_agent)
            result["agents_backed_up"].append(agent)
        except Exception as e:
            result["errors"].append(f"Failed to back up agent {agent}: {str(e)}")

    # Manage retention (keep last 10)
    _cleanup_old_on_change_backups(BACKUPS_ROOT / "on-change", max_backups=10)

    if result["errors"]:
        result["status"] = "PARTIAL_SUCCESS" if result["agents_backed_up"] else "FAILED"

    _log_backup(result)
    return result


def restore_agent_from_backup(agent_id: str, backup_type: str = "daily") -> Dict[str, Any]:
    """
    Restore an agent from most recent backup.

    Args:
        agent_id: Agent to restore
        backup_type: "daily" or "weekly"

    Returns:
        Restore result
    """
    backup_dir = _find_most_recent_backup(backup_type)

    if not backup_dir:
        return {
            "status": "FAILED",
            "error": f"No {backup_type} backup found"
        }

    agent_backup = backup_dir / agent_id / "workspace"
    agent_target = AGENTS_ROOT / agent_id / "workspace"

    if not agent_backup.exists():
        return {
            "status": "FAILED",
            "error": f"Agent {agent_id} not found in backup {backup_dir}"
        }

    try:
        # Backup current state first (before overwriting)
        current_backup = BACKUPS_ROOT / "pre-restore" / datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S") / agent_id
        if agent_target.exists():
            current_backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(agent_target, current_backup)

        # Restore from backup
        if agent_target.exists():
            shutil.rmtree(agent_target)
        shutil.copytree(agent_backup, agent_target)

        result = {
            "status": "SUCCESS",
            "agent": agent_id,
            "restored_from": str(agent_backup),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pre_restore_backup": str(current_backup) if current_backup.exists() else None
        }

        _log_backup(result)
        return result

    except Exception as e:
        return {
            "status": "FAILED",
            "error": f"Restore failed: {str(e)}"
        }


def _find_most_recent_backup(backup_type: str) -> Path:
    """Find most recent backup directory of given type."""
    backup_root = BACKUPS_ROOT / backup_type
    if not backup_root.exists():
        return None

    backups = sorted(backup_root.glob("*"), key=lambda x: x.name, reverse=True)
    return backups[0] if backups else None


def _cleanup_old_backups(backup_root: Path, retention_days: int):
    """Delete backups older than retention_days."""
    if not backup_root.exists():
        return

    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)

    for backup_dir in backup_root.glob("*"):
        try:
            # Try to parse directory name as date
            dir_date = datetime.strptime(backup_dir.name, "%Y-%m-%d")
            if dir_date.replace(tzinfo=timezone.utc) < cutoff:
                shutil.rmtree(backup_dir)
        except (ValueError, OSError):
            pass


def _cleanup_old_on_change_backups(backup_root: Path, max_backups: int = 10):
    """Keep only the most recent N on-change backups."""
    if not backup_root.exists():
        return

    backups = sorted(backup_root.glob("*"), key=lambda x: x.name, reverse=True)

    for old_backup in backups[max_backups:]:
        try:
            shutil.rmtree(old_backup)
        except OSError:
            pass


def _log_backup(result: Dict[str, Any]):
    """Log backup event to system history."""
    log_entry = {
        "event_type": "backup",
        "timestamp": result.get("timestamp", datetime.now(timezone.utc).isoformat()),
        "backup_type": result.get("backup_type", "unknown"),
        "status": result.get("status", "UNKNOWN"),
        "files_or_agents": result.get("files_backed_up") or result.get("agents_backed_up", 0),
        "errors_count": len(result.get("errors", []))
    }

    with open(SYSTEM_HISTORY, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "daily":
            result = execute_daily_backup()
            print(json.dumps(result, indent=2))
        elif command == "weekly":
            result = execute_weekly_backup()
            print(json.dumps(result, indent=2))
        elif command == "restore" and len(sys.argv) > 2:
            agent_id = sys.argv[2]
            result = restore_agent_from_backup(agent_id)
            print(json.dumps(result, indent=2))
    else:
        print("Usage: python backup_agent.py [daily|weekly|restore AGENT_ID]")
