"""
Profile Picker for Agent Rick
===============================
Selects the optimal LinkedIn profile for a candidate-job match.

A candidate may have multiple LinkedIn profiles, each with different:
- Positioning and role alignment
- Profile health status (active, banned, etc.)
- Application counts (daily and cumulative)
- Success history (interview callbacks, inbound leads)
- Recent usage patterns

This script picks the BEST profile for the specific role, considering all factors.

Usage:
    from profile_picker import pick_profile

    result = pick_profile(
        candidate_profiles_list,
        target_job_dict,
        application_history_list,
        profile_health_status_dict
    )
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path


def pick_profile(profiles: list, target_job: dict, application_history: list = None,
                 profile_health: dict = None) -> dict:
    """
    Select the optimal LinkedIn profile for a candidate-job match.

    Args:
        profiles: List of profile dicts. Each with:
            - profile_id (str): Unique identifier
            - candidate_id (str)
            - positioning (str): How profile is positioned (e.g., "Microservices Architect")
            - created_date (ISO-8601)
            - last_activity (ISO-8601, optional)

        target_job: Job posting dict with:
            - job_id (str)
            - job_title (str)
            - required_skills (list)

        application_history: List of application records:
            - application_id (str)
            - profile_id (str)
            - job_id (str)
            - submitted_date (ISO-8601)
            - status (str): PENDING / REJECTED / ACCEPTED / PLACED

        profile_health: Dict keyed by profile_id with:
            - health_status (str): GREEN / YELLOW / RED / BANNED
            - applications_today (int)
            - daily_limit (int): Usually 5
            - last_ban_date (ISO-8601, optional)
            - interview_callbacks (int)
            - inbound_leads (int)

    Returns:
        Dict with:
            - selected_profile_id (str)
            - reasoning (str)
            - score (float 0-100): Overall suitability score
            - criteria_scores: Breakdown of each selection criterion
            - warning (str, optional): Flag if less-than-ideal choice
    """
    application_history = application_history or []
    profile_health = profile_health or {}

    if not profiles:
        return {
            "selected_profile_id": None,
            "reasoning": "No profiles available for candidate",
            "score": 0,
            "criteria_scores": {},
            "error": "No profiles provided"
        }

    # Score each profile
    profile_scores = []
    for profile in profiles:
        profile_id = profile.get("profile_id", "")

        score = _score_profile(
            profile,
            target_job,
            application_history,
            profile_health.get(profile_id, {})
        )
        profile_scores.append((profile_id, score))

    # Find best profile
    if not profile_scores:
        return {
            "selected_profile_id": None,
            "reasoning": "Could not score any profiles",
            "score": 0,
            "error": "Scoring failed for all profiles"
        }

    # Sort by score descending
    profile_scores.sort(key=lambda x: x[1]["overall_score"], reverse=True)
    best_profile_id, best_score = profile_scores[0]

    # Find full profile details for reasoning
    best_profile = next((p for p in profiles if p.get("profile_id") == best_profile_id), {})

    # Check for health blockers
    best_health = profile_health.get(best_profile_id, {})
    blocker = _check_blockers(best_profile_id, best_health, application_history)

    if blocker:
        # This profile is blocked, try next best
        for alt_profile_id, alt_score in profile_scores[1:]:
            alt_health = profile_health.get(alt_profile_id, {})
            if not _check_blockers(alt_profile_id, alt_health, application_history):
                best_profile_id = alt_profile_id
                best_score = alt_score
                best_profile = next((p for p in profiles if p.get("profile_id") == best_profile_id), {})
                best_health = alt_health
                blocker = None
                break

        if blocker:
            return {
                "selected_profile_id": None,
                "reasoning": f"All profiles blocked: {blocker}",
                "score": 0,
                "error": blocker
            }

    result = {
        "selected_profile_id": best_profile_id,
        "positioning": best_profile.get("positioning", ""),
        "reasoning": _generate_reasoning(best_profile_id, best_score, profile_scores),
        "score": round(best_score["overall_score"], 1),
        "criteria_scores": {
            "role_alignment": best_score["role_alignment"],
            "profile_health": best_score["profile_health"],
            "application_count": best_score["application_count"],
            "conflict_check": best_score["conflict_check"],
            "inbound_consistency": best_score["inbound_consistency"],
            "success_history": best_score["success_history"]
        },
        "health_status": best_health.get("health_status", "UNKNOWN"),
        "applications_today": best_health.get("applications_today", 0),
        "daily_limit": best_health.get("daily_limit", 5),
        "recommended_action": "APPLY" if best_score["overall_score"] >= 60 else "DEFER",
        "alternatives": [
            {
                "profile_id": pid,
                "score": round(score["overall_score"], 1),
                "reason": score.get("reason", "")
            }
            for pid, score in profile_scores[1:3]  # Show top 2 alternatives
        ],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return result


def _score_profile(profile: dict, target_job: dict, application_history: list,
                   health: dict) -> dict:
    """
    Score a profile across 6 criteria.
    Each criterion scored 0-100, averaged for overall score.
    """

    profile_id = profile.get("profile_id", "")

    # Criterion 1: Role alignment (40% weight)
    role_alignment_score = _score_role_alignment(
        profile.get("positioning", ""),
        target_job.get("job_title", "")
    )

    # Criterion 2: Profile health (25% weight)
    profile_health_score = _score_profile_health(health)

    # Criterion 3: Application count today (20% weight)
    application_count_score = _score_application_count(profile_id, application_history, health)

    # Criterion 4: Conflict check (5% weight)
    conflict_score = _score_conflict_check(profile_id, target_job, application_history)

    # Criterion 5: Inbound consistency (5% weight)
    inbound_score = _score_inbound_consistency(profile_id, target_job, application_history)

    # Criterion 6: Success history (5% weight)
    success_score = _score_success_history(profile_id, application_history)

    # Weighted overall score
    overall = (
        role_alignment_score * 0.40 +
        profile_health_score * 0.25 +
        application_count_score * 0.20 +
        conflict_score * 0.05 +
        inbound_score * 0.05 +
        success_score * 0.05
    )

    return {
        "overall_score": overall,
        "role_alignment": role_alignment_score,
        "profile_health": profile_health_score,
        "application_count": application_count_score,
        "conflict_check": conflict_score,
        "inbound_consistency": inbound_score,
        "success_history": success_score
    }


def _score_role_alignment(positioning: str, job_title: str) -> float:
    """
    Score how well profile positioning matches target job title.
    """
    if not positioning or not job_title:
        return 50.0

    positioning_lower = positioning.lower()
    job_lower = job_title.lower()

    # Exact match
    if positioning_lower in job_lower or job_lower in positioning_lower:
        return 100.0

    # Partial matches
    alignment_keywords = {
        "microservice": ["architect", "distributed", "api", "backend"],
        "backend": ["engineer", "developer", "architect", "java", "python"],
        "frontend": ["react", "vue", "angular", "javascript"],
        "devops": ["engineer", "infrastructure", "cloud", "kubernetes"],
        "data": ["engineer", "scientist", "pipeline", "analytics"],
        "cloud": ["architect", "engineer", "aws", "gcp", "azure"],
        "lead": ["senior", "staff", "principal", "architect"],
    }

    position_words = positioning_lower.split()
    job_words = job_lower.split()

    # Count overlaps
    overlap = sum(1 for pw in position_words if pw in job_words)
    if overlap >= 2:
        return 90.0
    elif overlap == 1:
        return 70.0
    else:
        return 50.0


def _score_profile_health(health: dict) -> float:
    """
    Score profile health based on status.
    GREEN = 100, YELLOW = 70, RED = 30, BANNED = 0
    """
    status = health.get("health_status", "UNKNOWN")

    if status == "GREEN":
        return 100.0
    elif status == "YELLOW":
        return 70.0
    elif status == "RED":
        return 30.0
    elif status == "BANNED":
        return 0.0
    else:
        return 50.0


def _score_application_count(profile_id: str, application_history: list,
                              health: dict) -> float:
    """
    Score based on how many applications profile has today.
    5/day is the limit. More = lower score.
    """
    apps_today = health.get("applications_today", 0)
    daily_limit = health.get("daily_limit", 5)

    if apps_today >= daily_limit:
        return 0.0  # At limit, can't apply
    elif apps_today >= (daily_limit - 1):
        return 20.0  # Last slot
    elif apps_today >= (daily_limit - 2):
        return 50.0  # Getting close
    else:
        return 100.0  # Plenty of room


def _score_conflict_check(profile_id: str, target_job: dict,
                          application_history: list) -> float:
    """
    Check if this profile has applied to competing roles today.
    No conflict = 100. Competing application same day = 0.
    """
    today = datetime.now(timezone.utc).date()
    today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)

    target_client = target_job.get("client_name", "").lower()

    for app in application_history:
        if app.get("profile_id", "") == profile_id:
            submitted_date_str = app.get("submitted_date", "")
            try:
                submitted_date = datetime.fromisoformat(submitted_date_str)
                if submitted_date > today_start:
                    app_client = app.get("client_name", "").lower()
                    if app_client == target_client:
                        return 0.0  # Conflict: same profile to same client today

            except:
                pass

    return 100.0


def _score_inbound_consistency(profile_id: str, target_job: dict,
                                application_history: list) -> float:
    """
    If candidate has inbound leads from this role type, keep using this profile.
    Recent inbound from same job type = 100.
    No recent inbound = 50.
    """
    # Placeholder: would check if candidate got inbound from similar role in last 7 days
    # For now: neutral score
    return 50.0


def _score_success_history(profile_id: str, application_history: list) -> float:
    """
    Score based on past success rate (interviews, acceptances) with this profile.
    """
    profile_apps = [a for a in application_history if a.get("profile_id") == profile_id]

    if not profile_apps:
        return 50.0  # No history, neutral

    # Count successful outcomes
    successes = sum(1 for a in profile_apps if a.get("status") in ["ACCEPTED", "PLACED"])
    success_rate = (successes / len(profile_apps)) * 100

    return min(100.0, success_rate + 30)  # Boost based on success rate


def _check_blockers(profile_id: str, health: dict, application_history: list) -> str:
    """
    Check for hard blockers that prevent using this profile.
    Returns blocker reason if blocked, None if OK.
    """
    # Check health status
    if health.get("health_status") == "BANNED":
        return f"Profile {profile_id} is banned"

    # Check daily limit
    if health.get("applications_today", 0) >= health.get("daily_limit", 5):
        return f"Profile {profile_id} hit daily limit ({health.get('applications_today')}/{health.get('daily_limit')})"

    return None


def _generate_reasoning(selected_profile_id: str, score: dict, all_scores: list) -> str:
    """
    Generate human-readable reasoning for profile selection.
    """
    parts = []

    if score["overall_score"] >= 85:
        parts.append(f"Excellent match.")
    elif score["overall_score"] >= 70:
        parts.append(f"Good match.")
    elif score["overall_score"] >= 60:
        parts.append(f"Acceptable match.")
    else:
        parts.append(f"Marginal match (score {score['overall_score']}%).")

    # Top factor
    factors = [
        ("role_alignment", score["role_alignment"], "role alignment"),
        ("profile_health", score["profile_health"], "profile health"),
        ("application_count", score["application_count"], "available application slots"),
        ("success_history", score["success_history"], "past success history"),
    ]
    top_factor = max(factors, key=lambda x: x[1])
    parts.append(f"Strongest factor: {top_factor[2]} ({top_factor[1]}%).")

    if len(all_scores) > 1 and all_scores[1][1]["overall_score"] > 0:
        parts.append(
            f"Alternative: Profile {all_scores[1][0]} "
            f"({all_scores[1][1]['overall_score']}%)."
        )

    return " ".join(parts)


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            data = json.load(f)

        profiles = data.get("profiles", [])
        target_job = data.get("target_job", {})
        application_history = data.get("application_history", [])
        profile_health = data.get("profile_health", {})

        result = pick_profile(profiles, target_job, application_history, profile_health)
        print(json.dumps(result, indent=2))
    else:
        # Demo
        sample_profiles = [
            {
                "profile_id": "LI-042-A",
                "candidate_id": "C-042",
                "positioning": "Microservices Architect",
                "created_date": "2025-01-15T00:00:00Z"
            },
            {
                "profile_id": "LI-042-B",
                "candidate_id": "C-042",
                "positioning": "Senior Java Developer",
                "created_date": "2025-02-01T00:00:00Z"
            }
        ]
        sample_job = {
            "job_id": "J-1234",
            "job_title": "Microservices Architect",
            "client_name": "Acme Corp"
        }
        sample_health = {
            "LI-042-A": {
                "health_status": "GREEN",
                "applications_today": 2,
                "daily_limit": 5,
                "interview_callbacks": 3
            },
            "LI-042-B": {
                "health_status": "GREEN",
                "applications_today": 4,
                "daily_limit": 5,
                "interview_callbacks": 1
            }
        }
        result = pick_profile(sample_profiles, sample_job, [], sample_health)
        print(json.dumps(result, indent=2))
