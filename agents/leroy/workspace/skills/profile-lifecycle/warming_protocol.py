"""
Profile Warming Protocol for Agent Leroy
=========================================
Generates warming schedules for new Tier C profiles to build trust and
account legitimacy through progressive engagement.

Usage:
    from profile_lifecycle.warming_protocol import get_warming_schedule

    schedule = get_warming_schedule({
        "profile_id": "P-001",
        "account_age_days": 10,
        "current_date": "2026-02-15",
        "target_connection_count": 150
    })
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def get_warming_schedule(inputs: dict) -> dict:
    """
    Get warming schedule for a new profile.

    Args:
        inputs: Dict with keys:
            - profile_id (str): Profile identifier
            - account_age_days (int): Days since account creation
            - current_date (str): YYYY-MM-DD
            - target_connection_count (int): Target connections (default 150)

    Returns:
        Dict with warming phase, daily targets, milestones, next phase date.
    """
    profile_id = inputs["profile_id"]
    account_age_days = inputs["account_age_days"]
    current_date = datetime.strptime(inputs["current_date"], "%Y-%m-%d")
    target_conn = inputs.get("target_connection_count", 150)

    # Determine warming phase based on age
    if account_age_days < 14:
        phase = "Week1"
        phase_name = "Foundation"
        daily_targets = {
            "profile_views": 5,
            "profile_view_responses": 2,
            "connection_requests": 3,
            "reactions": 2,
            "group_joins": 1,
            "browse_time_minutes": 5,
            "applications": 0
        }
        phase_end_date = current_date + timedelta(days=14 - account_age_days)
    elif account_age_days < 28:
        phase = "Week3"
        phase_name = "Trust Building"
        daily_targets = {
            "profile_views": 8,
            "profile_view_responses": 3,
            "connection_requests": 5,
            "reactions": 3,
            "comments": 1,
            "group_joins": 0,
            "browse_time_minutes": 8,
            "applications": 0
        }
        phase_end_date = current_date + timedelta(days=28 - account_age_days)
    elif account_age_days < 60:
        phase = "Month2"
        phase_name = "Presence Building"
        daily_targets = {
            "profile_views": 10,
            "profile_view_responses": 4,
            "connection_requests": 6,
            "reactions": 4,
            "comments": 2,
            "group_activity": 1,
            "browse_time_minutes": 10,
            "applications": 0
        }
        phase_end_date = current_date + timedelta(days=60 - account_age_days)
    else:
        phase = "Month4"
        phase_name = "Maturation"
        daily_targets = {
            "profile_views": 8,
            "profile_view_responses": 3,
            "connection_requests": 5,
            "reactions": 3,
            "comments": 1,
            "group_activity": 1,
            "browse_time_minutes": 8,
            "applications": 1
        }
        phase_end_date = current_date + timedelta(days=180 - account_age_days)

    # Calculate expected milestones
    week1_connections = 50
    week2_connections = 100
    month1_connections = 150

    milestones = {
        "week_1_target": f"{week1_connections} connections + 10 reactions + presence established",
        "week_2_target": f"{week2_connections} connections + basic engagement history visible",
        "month_1_target": f"{month1_connections} connections + consistent activity pattern",
        "ready_for_tier_b": "Mature account appearance, ready for application acceleration"
    }

    result = {
        "profile_id": profile_id,
        "warming_phase": phase,
        "phase_name": phase_name,
        "warming_week": int(account_age_days / 7) + 1,
        "account_age_days": account_age_days,
        "daily_targets": daily_targets,
        "milestones": milestones,
        "expected_connections_by_phase": {
            "week_1": week1_connections,
            "week_2": week2_connections,
            "month_1": month1_connections,
            "ready_for_tier_b": target_conn
        },
        "next_phase_date": phase_end_date.strftime("%Y-%m-%d"),
        "tier_b_readiness_date": (current_date + timedelta(days=180)).strftime("%Y-%m-%d"),
        "guidance": {
            "week1_focus": "Establish presence, light activity, initial network",
            "week2_focus": "Increase engagement, industry participation, skill visibility",
            "month2_focus": "Consistent activity, thought leadership, community participation",
            "month4_focus": "Ready for Tier B, can handle 1-2 applications per week"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return result


def get_weekly_warming_metrics(inputs: dict) -> dict:
    """
    Get expected metrics for the current warming week.

    Args:
        inputs: Dict with keys:
            - profile_id (str)
            - account_age_days (int)
            - current_date (str): YYYY-MM-DD

    Returns:
        Dict with weekly targets and progress tracking.
    """
    account_age = inputs["account_age_days"]
    current_date = datetime.strptime(inputs["current_date"], "%Y-%m-%d")

    warming_week = (account_age // 7) + 1

    # Define metrics by week
    weekly_metrics = {
        1: {
            "week": 1,
            "target_connections": 50,
            "target_reactions": 10,
            "target_sessions": 7,
            "expected_acceptance_rate": 0.40,
            "focus": "Establish presence and initial network"
        },
        2: {
            "week": 2,
            "target_connections": 50,
            "target_reactions": 12,
            "target_sessions": 7,
            "expected_acceptance_rate": 0.45,
            "focus": "Increase engagement and skill visibility"
        },
        3: {
            "week": 3,
            "target_connections": 50,
            "target_reactions": 15,
            "target_sessions": 7,
            "expected_acceptance_rate": 0.50,
            "focus": "Build trust and establish patterns"
        },
        4: {
            "week": 4,
            "target_connections": 50,
            "target_reactions": 15,
            "target_sessions": 7,
            "expected_acceptance_rate": 0.50,
            "focus": "Maintain momentum and consistency"
        }
    }

    metrics = weekly_metrics.get(warming_week, weekly_metrics[4])

    result = {
        "profile_id": inputs["profile_id"],
        "warming_week": warming_week,
        "current_date": inputs["current_date"],
        "week_start_date": (current_date - timedelta(days=(current_date.weekday()))).strftime("%Y-%m-%d"),
        "week_end_date": (current_date + timedelta(days=(6 - current_date.weekday()))).strftime("%Y-%m-%d"),
        "metrics": metrics,
        "cumulative_targets": {
            "total_connections": metrics["target_connections"] * warming_week,
            "total_reactions": sum([weekly_metrics[w]["target_reactions"] for w in range(1, warming_week + 1)]),
            "total_sessions": metrics["target_sessions"] * warming_week
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return result


def check_warming_progress(inputs: dict) -> dict:
    """
    Check if profile is on track with warming schedule.

    Args:
        inputs: Dict with keys:
            - profile_id (str)
            - account_age_days (int)
            - current_connections (int)
            - total_reactions (int)
            - sessions_this_week (int)
            - current_date (str): YYYY-MM-DD

    Returns:
        Dict with progress status and recommendations.
    """
    profile_id = inputs["profile_id"]
    account_age = inputs["account_age_days"]
    current_connections = inputs.get("current_connections", 0)
    total_reactions = inputs.get("total_reactions", 0)
    sessions = inputs.get("sessions_this_week", 0)

    # Get expected metrics
    expected = get_weekly_warming_metrics(inputs)
    metrics = expected["metrics"]
    cumulative = expected["cumulative_targets"]

    # Calculate progress
    connection_rate = (current_connections / cumulative["total_connections"]) * 100 if cumulative["total_connections"] > 0 else 0
    reaction_rate = (total_reactions / cumulative["total_reactions"]) * 100 if cumulative["total_reactions"] > 0 else 0
    session_rate = (sessions / cumulative["total_sessions"]) * 100 if cumulative["total_sessions"] > 0 else 0

    # Determine status
    if connection_rate >= 90 and reaction_rate >= 85:
        status = "ON_TRACK"
        recommendations = ["Continue current activity pattern", "Prepare for next phase"]
    elif connection_rate >= 70:
        status = "SLIGHTLY_BEHIND"
        recommendations = ["Increase daily connection requests by 1-2", "Boost engagement with more reactions"]
    else:
        status = "BEHIND_SCHEDULE"
        recommendations = ["Increase daily activity significantly", "Check if profile is getting blocked", "May need to extend warming period"]

    result = {
        "profile_id": profile_id,
        "account_age_days": account_age,
        "warming_status": status,
        "progress": {
            "connections": {
                "current": current_connections,
                "expected": cumulative["total_connections"],
                "percentage": round(connection_rate, 1)
            },
            "reactions": {
                "current": total_reactions,
                "expected": cumulative["total_reactions"],
                "percentage": round(reaction_rate, 1)
            },
            "sessions": {
                "current": sessions,
                "expected": cumulative["total_sessions"],
                "percentage": round(session_rate, 1)
            }
        },
        "recommendations": recommendations,
        "next_action": "CONTINUE_WARMING" if status in ["ON_TRACK", "SLIGHTLY_BEHIND"] else "INVESTIGATE",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return result


# --- CLI interface for testing ---
if __name__ == "__main__":
    print("=== WARMING SCHEDULE: WEEK 1 ===\n")
    week1 = get_warming_schedule({
        "profile_id": "P-001",
        "account_age_days": 5,
        "current_date": "2026-02-15",
        "target_connection_count": 150
    })
    print(json.dumps(week1, indent=2))

    print("\n\n=== WARMING SCHEDULE: WEEK 3 ===\n")
    week3 = get_warming_schedule({
        "profile_id": "P-002",
        "account_age_days": 20,
        "current_date": "2026-02-15",
        "target_connection_count": 200
    })
    print(json.dumps(week3, indent=2))

    print("\n\n=== WEEKLY METRICS ===\n")
    metrics = get_weekly_warming_metrics({
        "profile_id": "P-001",
        "account_age_days": 10,
        "current_date": "2026-02-15"
    })
    print(json.dumps(metrics, indent=2))

    print("\n\n=== WARMING PROGRESS CHECK: ON TRACK ===\n")
    progress = check_warming_progress({
        "profile_id": "P-001",
        "account_age_days": 14,
        "current_connections": 45,
        "total_reactions": 9,
        "sessions_this_week": 7,
        "current_date": "2026-02-15"
    })
    print(json.dumps(progress, indent=2))
