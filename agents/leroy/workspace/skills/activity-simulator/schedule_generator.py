"""
Activity Schedule Generator for Agent Leroy
=============================================
Generates randomized daily activity schedules per profile that simulate human-like
LinkedIn behavior while respecting tier-based constraints.

Usage:
    from activity_simulator.schedule_generator import generate_schedule, generate_batch_schedules

    schedule = generate_schedule({
        "profile_id": "P-001",
        "tier": "A",
        "date": "2026-02-15",
        "health_state": "GREEN",
        "primary_timezone": "EST"
    })
"""

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


BEHAVIOR_FILE = Path(__file__).parent / "behavior_profiles.json"


def load_behavior_profiles() -> dict:
    """Load tier behavior profiles from config."""
    with open(BEHAVIOR_FILE, "r") as f:
        return json.load(f)


def _get_login_windows(tier: str, primary_timezone: str) -> list:
    """Get login time windows for tier in given timezone."""
    # Base windows (EDT/EST)
    windows = {
        "A": [
            {"start": "07:30", "end": "09:30", "name": "morning"},
            {"start": "12:00", "end": "14:30", "name": "afternoon"},
            {"start": "16:00", "end": "18:30", "name": "evening"}
        ],
        "B": [
            {"start": "08:00", "end": "10:00", "name": "morning"},
            {"start": "13:00", "end": "15:00", "name": "afternoon"}
        ],
        "C": [
            {"start": "09:00", "end": "11:00", "name": "morning"},
        ],
        "D": []
    }
    return windows.get(tier, [])


def _random_time_in_window(date_str: str, window_start: str, window_end: str, tz: str = "EST") -> datetime:
    """Generate random time within a window."""
    base_date = datetime.strptime(date_str, "%Y-%m-%d")

    # Parse window times
    start_h, start_m = map(int, window_start.split(":"))
    end_h, end_m = map(int, window_end.split(":"))

    # Random minute within window
    start_total_min = start_h * 60 + start_m
    end_total_min = end_h * 60 + end_m
    random_min = random.randint(start_total_min, end_total_min)

    hour = random_min // 60
    minute = random_min % 60

    dt = base_date.replace(hour=hour, minute=minute, second=random.randint(0, 59))
    return dt


def _random_duration(min_secs: int, max_secs: int) -> int:
    """Generate random duration in seconds."""
    return random.randint(min_secs, max_secs)


def _random_activity_count(min_count: int, max_count: int) -> int:
    """Generate random activity count."""
    return random.randint(min_count, max_count)


def generate_schedule(inputs: dict) -> dict:
    """
    Generate randomized daily activity schedule for a single profile.

    Args:
        inputs: Dict with keys:
            - profile_id (str): Profile identifier
            - tier (str): A, B, C, or D
            - date (str): YYYY-MM-DD
            - health_state (str): GREEN, YELLOW, ORANGE, RED
            - primary_timezone (str): EST, CST, PST, etc.

    Returns:
        Dict with daily schedule of sessions and activities.
    """
    if inputs["health_state"] == "RED":
        # RED state = zero activity
        return {
            "profile_id": inputs["profile_id"],
            "date": inputs["date"],
            "tier": inputs["tier"],
            "health_state": "RED",
            "schedule": [],
            "total_sessions": 0,
            "total_duration_minutes": 0,
            "activities_summary": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    behavior = load_behavior_profiles()
    tier = inputs["tier"]
    date_str = inputs["date"]
    health_state = inputs["health_state"]
    tz = inputs.get("primary_timezone", "EST")

    tier_behavior = behavior.get(tier, {})
    if not tier_behavior:
        return {"error": f"Unknown tier: {tier}"}

    # Get sessions per day for this tier
    if tier == "D":
        return {
            "profile_id": inputs["profile_id"],
            "date": date_str,
            "tier": "D",
            "health_state": health_state,
            "schedule": [],
            "total_sessions": 0,
            "total_duration_minutes": 0,
            "activities_summary": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    # For Tier C, skip 40% of days (activity every 2-3 days)
    if tier == "C" and random.random() < 0.4:
        return {
            "profile_id": inputs["profile_id"],
            "date": date_str,
            "tier": "C",
            "health_state": health_state,
            "schedule": [],
            "total_sessions": 0,
            "total_duration_minutes": 0,
            "skip_reason": "Tier C schedule (activity every 2-3 days)",
            "activities_summary": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    # Get login windows for this tier
    login_windows = _get_login_windows(tier, tz)

    # Determine number of sessions
    num_sessions = tier_behavior["sessions_per_day"]
    if isinstance(num_sessions, dict):
        num_sessions = random.randint(num_sessions["min"], num_sessions["max"])

    sessions = []
    login_times = []

    for session_num in range(num_sessions):
        window = login_windows[session_num]
        login_time = _random_time_in_window(date_str, window["start"], window["end"], tz)
        login_times.append(login_time)

        # Session duration
        duration_range = tier_behavior["session_duration_minutes"]
        duration = random.randint(duration_range["min"], duration_range["max"])

        # Activities for this session
        activities = []

        # Browsing
        browse_min = tier_behavior["activities"]["browse"]["min"]
        browse_max = tier_behavior["activities"]["browse"]["max"]
        browse_count = 1  # One browse per session
        activities.append({
            "activity": "browse",
            "duration": random.randint(browse_min, browse_max),
            "count": browse_count
        })

        # Reactions
        reactions_range = tier_behavior["activities"]["reactions"]
        if reactions_range["min"] > 0 or reactions_range["max"] > 0:
            reactions_count = random.randint(reactions_range["min"], reactions_range["max"])
            if reactions_count > 0:
                activities.append({
                    "activity": "reactions",
                    "count": reactions_count
                })

        # Profile views
        views_range = tier_behavior["activities"]["profile_views"]
        if views_range["min"] > 0 or views_range["max"] > 0:
            views_count = random.randint(views_range["min"], views_range["max"])
            if views_count > 0:
                activities.append({
                    "activity": "profile_views",
                    "count": views_count
                })

        # Comments
        comments_range = tier_behavior["activities"]["comments"]
        if comments_range["min"] > 0 or comments_range["max"] > 0:
            comments_count = random.randint(comments_range["min"], comments_range["max"])
            if comments_count > 0:
                activities.append({
                    "activity": "comments",
                    "count": comments_count
                })

        # Connection requests
        conn_range = tier_behavior["activities"]["connection_requests"]
        if conn_range["min"] > 0 or conn_range["max"] > 0:
            conn_count = random.randint(conn_range["min"], conn_range["max"])
            if conn_count > 0:
                activities.append({
                    "activity": "connection_requests",
                    "count": conn_count
                })

        # Applications (only if GREEN health state for Tier A/B, or per tier defaults)
        app_range = tier_behavior["activities"]["applications"]
        if health_state == "GREEN":
            app_count = random.randint(app_range["min"], app_range["max"])
        elif health_state == "YELLOW":
            # YELLOW caps at 2 total per day
            app_count = 0  # Let outer logic handle YELLOW cap
        else:
            app_count = 0

        if app_count > 0:
            activities.append({
                "activity": "applications",
                "count": app_count
            })

        session = {
            "session": session_num + 1,
            "login_time": login_time.isoformat(),
            "duration_minutes": duration,
            "activities": activities
        }
        sessions.append(session)

    # Calculate total duration
    total_duration = sum(s["duration_minutes"] for s in sessions)

    # Summarize activities
    activities_summary = {}
    for session in sessions:
        for activity in session["activities"]:
            act_name = activity["activity"]
            if act_name not in activities_summary:
                activities_summary[act_name] = 0
            activities_summary[act_name] += activity.get("count", 1)

    # If YELLOW health, cap applications to 2 total
    if health_state == "YELLOW" and "applications" in activities_summary:
        activities_summary["applications"] = min(2, activities_summary["applications"])

    result = {
        "profile_id": inputs["profile_id"],
        "date": date_str,
        "tier": tier,
        "health_state": health_state,
        "schedule": sessions,
        "total_sessions": len(sessions),
        "total_duration_minutes": total_duration,
        "activities_summary": activities_summary,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return result


def generate_batch_schedules(profile_list: list, date: str) -> list:
    """
    Generate schedules for entire portfolio for a single date.

    Args:
        profile_list: List of profile dicts with profile_id, tier, health_state, timezone
        date: YYYY-MM-DD date string

    Returns:
        List of schedule dicts.
    """
    schedules = []
    for profile in profile_list:
        schedule = generate_schedule({
            "profile_id": profile["profile_id"],
            "tier": profile["tier"],
            "date": date,
            "health_state": profile.get("health_state", "GREEN"),
            "primary_timezone": profile.get("primary_timezone", "EST")
        })
        schedules.append(schedule)

    return schedules


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Read input from file
        with open(sys.argv[1], "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            results = generate_batch_schedules(data, "2026-02-15")
        else:
            results = generate_schedule(data)
        print(json.dumps(results, indent=2))
    else:
        # Demo with sample profiles
        print("=== TIER A PROFILE (GREEN) ===\n")
        tier_a = {
            "profile_id": "P-001",
            "tier": "A",
            "date": "2026-02-15",
            "health_state": "GREEN",
            "primary_timezone": "EST"
        }
        result_a = generate_schedule(tier_a)
        print(json.dumps(result_a, indent=2))

        print("\n\n=== TIER C PROFILE (GREEN) ===\n")
        tier_c = {
            "profile_id": "P-002",
            "tier": "C",
            "date": "2026-02-15",
            "health_state": "GREEN",
            "primary_timezone": "EST"
        }
        result_c = generate_schedule(tier_c)
        print(json.dumps(result_c, indent=2))

        print("\n\n=== TIER A PROFILE (YELLOW) ===\n")
        tier_a_yellow = {
            "profile_id": "P-003",
            "tier": "A",
            "date": "2026-02-15",
            "health_state": "YELLOW",
            "primary_timezone": "EST"
        }
        result_a_yellow = generate_schedule(tier_a_yellow)
        print(json.dumps(result_a_yellow, indent=2))
