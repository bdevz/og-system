"""
Profile Repositioning Engine for Agent Leroy
=============================================
Manages gradual, safe profile repositioning (headline, summary, skills, experience)
with enforcement of safety constraints to avoid detection.

Usage:
    from profile_lifecycle.repositioning_engine import plan_repositioning

    plan = plan_repositioning({
        "profile_id": "P-001",
        "current_positioning": {"headline": "Java Developer", ...},
        "target_positioning": {"headline": "Senior Java/Cloud Architect", ...},
        "last_major_repositioning_date": "2025-12-15",
        "current_date": "2026-02-15"
    })
"""

import json
from datetime import datetime, timedelta
from pathlib import Path


def plan_repositioning(inputs: dict) -> dict:
    """
    Plan a gradual profile repositioning over 5-7 days.

    Args:
        inputs: Dict with keys:
            - profile_id (str): Profile identifier
            - current_positioning (dict): Current headline, summary, skills, etc.
            - target_positioning (dict): Desired headline, summary, skills, etc.
            - last_major_repositioning_date (str): YYYY-MM-DD or None
            - current_date (str): YYYY-MM-DD
            - account_age_days (int, optional): For new account checks

    Returns:
        Dict with repositioning plan or block reason.
    """
    profile_id = inputs["profile_id"]
    current_date = datetime.strptime(inputs["current_date"], "%Y-%m-%d")
    last_reposition_str = inputs.get("last_major_repositioning_date")
    account_age = inputs.get("account_age_days", 100)

    # Safety check 1: Account age (min 14 days)
    if account_age < 14:
        return {
            "status": "BLOCKED",
            "reason": "Account too new for repositioning",
            "min_age_days": 14,
            "current_age_days": account_age,
            "can_reposition_after": (current_date + timedelta(days=14 - account_age)).strftime("%Y-%m-%d"),
            "profile_id": profile_id
        }

    # Safety check 2: Time since last repositioning (min 30 days)
    if last_reposition_str and last_reposition_str != "Never":
        last_date = datetime.strptime(last_reposition_str, "%Y-%m-%d")
        days_since = (current_date - last_date).days

        if days_since < 30:
            return {
                "status": "BLOCKED",
                "reason": "Recent repositioning detected",
                "last_repositioning_date": last_reposition_str,
                "days_since": days_since,
                "min_days_between": 30,
                "can_reposition_after": (last_date + timedelta(days=30)).strftime("%Y-%m-%d"),
                "profile_id": profile_id
            }

    # All checks passed - create repositioning plan
    plan = [
        {
            "day": 1,
            "date": current_date.strftime("%Y-%m-%d"),
            "changes": ["headline"],
            "details": f"Update headline from '{inputs['current_positioning'].get('headline', '')}' to '{inputs['target_positioning'].get('headline', '')}'",
            "expected_disruption": "low",
            "description": "Most visible change, people notice headline changes"
        },
        {
            "day": 2,
            "date": (current_date + timedelta(days=1)).strftime("%Y-%m-%d"),
            "changes": ["summary"],
            "details": "Expand and refocus summary/about section",
            "expected_disruption": "low",
            "description": "Summary changes appear less jarring to connections"
        },
        {
            "day": 3,
            "date": (current_date + timedelta(days=2)).strftime("%Y-%m-%d"),
            "changes": ["skills_reorder"],
            "details": "Reorder skills, promote new top 5",
            "expected_disruption": "low",
            "description": "Skill changes are normal progression, less suspicious"
        },
        {
            "day": 4,
            "date": (current_date + timedelta(days=3)).strftime("%Y-%m-%d"),
            "changes": ["featured_section"],
            "details": "Update featured projects/recommendations",
            "expected_disruption": "low",
            "description": "Featured content can change without profile alert"
        },
        {
            "day": 5,
            "date": (current_date + timedelta(days=4)).strftime("%Y-%m-%d"),
            "changes": ["experience_bullets"],
            "details": "Update recent role bullet points with new focus",
            "expected_disruption": "low",
            "description": "Experience refinements look like natural updates"
        }
    ]

    ready_date = (current_date + timedelta(days=5)).strftime("%Y-%m-%d")

    result = {
        "status": "ALLOWED",
        "profile_id": profile_id,
        "repositioning_plan": plan,
        "total_duration_days": 5,
        "ready_for_applications": ready_date,
        "validation": {
            "account_age_ok": True,
            "time_since_last_reposition_ok": True if not last_reposition_str else (current_date - datetime.strptime(last_reposition_str, "%Y-%m-%d")).days >= 30
        },
        "guidance": {
            "strategy": "Spread changes over 5 days to appear gradual",
            "headline_first": "People notice headline immediately, get it done first",
            "skills_reorder": "Skill changes are lowest-risk, do this mid-plan",
            "spacing": "24-hour gap between major changes prevents detection",
            "timing": "Changes should happen during profile owner's normal activity hours"
        },
        "timestamp": datetime.now().isoformat()
    }

    return result


def validate_repositioning_changes(inputs: dict) -> dict:
    """
    Validate that repositioning changes are not too drastic.

    Args:
        inputs: Dict with keys:
            - current_positioning (dict): Current profile state
            - target_positioning (dict): Target profile state

    Returns:
        Dict with validation results and risk assessment.
    """
    current = inputs.get("current_positioning", {})
    target = inputs.get("target_positioning", {})

    changes = {}
    risk_level = "LOW"

    # Check headline change
    if current.get("headline") != target.get("headline"):
        change = {
            "from": current.get("headline"),
            "to": target.get("headline"),
            "risk": "MEDIUM"
        }
        changes["headline"] = change
        if risk_level == "LOW":
            risk_level = "MEDIUM"

    # Check summary/about
    if current.get("summary") != target.get("summary"):
        changes["summary"] = {
            "changed": True,
            "risk": "LOW"
        }

    # Check skills
    current_skills = set(current.get("skills", []))
    target_skills = set(target.get("skills", []))
    removed_skills = current_skills - target_skills
    added_skills = target_skills - current_skills

    if removed_skills or added_skills:
        changes["skills"] = {
            "added": list(added_skills),
            "removed": list(removed_skills),
            "risk": "LOW" if len(removed_skills) <= 2 else "MEDIUM"
        }

    # Overall risk assessment
    if len(changes) > 2:
        risk_level = "HIGH"

    result = {
        "profile_id": inputs.get("profile_id"),
        "changes": changes,
        "total_changes": len(changes),
        "risk_level": risk_level,
        "is_valid": risk_level != "HIGH",
        "validation_message": "Changes look gradual and natural" if risk_level == "LOW" else
                            "Moderate changes, spread over several days" if risk_level == "MEDIUM" else
                            "Too many major changes at once - reduce scope",
        "timestamp": datetime.now().isoformat()
    }

    return result


def get_repositioning_history(inputs: dict) -> dict:
    """
    Get repositioning history for a profile.

    Args:
        inputs: Dict with keys:
            - profile_id (str)
            - history (list, optional): Previous repositioning records

    Returns:
        Dict with repositioning history and trend analysis.
    """
    profile_id = inputs["profile_id"]
    history = inputs.get("history", [])

    if not history:
        return {
            "profile_id": profile_id,
            "total_repositionings": 0,
            "frequency": "Never repositioned",
            "last_repositioning": None,
            "next_eligible_date": datetime.now().strftime("%Y-%m-%d")
        }

    # Analyze history
    dates = [datetime.strptime(h.get("date"), "%Y-%m-%d") for h in history if "date" in h]
    dates.sort()

    gaps = []
    for i in range(1, len(dates)):
        gap = (dates[i] - dates[i-1]).days
        gaps.append(gap)

    avg_gap = sum(gaps) / len(gaps) if gaps else 0

    result = {
        "profile_id": profile_id,
        "total_repositionings": len(history),
        "repositioning_dates": [d.strftime("%Y-%m-%d") for d in dates],
        "last_repositioning": dates[-1].strftime("%Y-%m-%d") if dates else None,
        "next_eligible_date": (dates[-1] + timedelta(days=30)).strftime("%Y-%m-%d") if dates else None,
        "average_gap_days": round(avg_gap),
        "frequency": "Very frequent (every 7-14 days)" if avg_gap < 15 else
                    "Frequent (every 2-4 weeks)" if avg_gap < 30 else
                    "Normal (monthly or less)",
        "trend": "SUSPICIOUS" if avg_gap < 14 else "NORMAL"
    }

    return result


# --- CLI interface for testing ---
if __name__ == "__main__":
    print("=== REPOSITIONING PLAN: ALLOWED ===\n")
    plan = plan_repositioning({
        "profile_id": "P-001",
        "current_positioning": {
            "headline": "Java Developer",
            "summary": "Experienced Java developer...",
            "skills": ["Java", "Spring", "SQL"]
        },
        "target_positioning": {
            "headline": "Senior Java/Cloud Architect",
            "summary": "Cloud architect with Java expertise...",
            "skills": ["Java", "Spring", "AWS", "Kubernetes"]
        },
        "last_major_repositioning_date": "2025-12-15",
        "current_date": "2026-02-15",
        "account_age_days": 180
    })
    print(json.dumps(plan, indent=2))

    print("\n\n=== REPOSITIONING PLAN: BLOCKED (TOO RECENT) ===\n")
    blocked = plan_repositioning({
        "profile_id": "P-002",
        "current_positioning": {"headline": "Java Developer"},
        "target_positioning": {"headline": "Senior Java Architect"},
        "last_major_repositioning_date": "2026-02-10",
        "current_date": "2026-02-15",
        "account_age_days": 180
    })
    print(json.dumps(blocked, indent=2))

    print("\n\n=== VALIDATE CHANGES ===\n")
    validation = validate_repositioning_changes({
        "profile_id": "P-001",
        "current_positioning": {
            "headline": "Java Developer",
            "summary": "Experienced Java developer...",
            "skills": ["Java", "Spring", "SQL", "Maven", "Jenkins"]
        },
        "target_positioning": {
            "headline": "Senior Java/Cloud Architect",
            "summary": "Cloud architect with Java expertise...",
            "skills": ["Java", "Spring", "AWS", "Kubernetes", "Docker"]
        }
    })
    print(json.dumps(validation, indent=2))
