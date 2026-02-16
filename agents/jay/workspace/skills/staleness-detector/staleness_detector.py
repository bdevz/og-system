"""
Staleness Detector for Agent Jay
==================================
Detects stale, dead, or low-quality postings.
Input: posting metadata. Output: staleness score, red flags, recommendation.

Usage:
    from staleness_detector import detect_staleness

    result = detect_staleness({
        "posting_age_days": 45,
        "applicant_count": 520,
        "company": "TechCorp",
        "title": "Senior Java Developer"
    })
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


def _score_posting_age(days_old: int) -> Tuple[float, str]:
    """
    Score posting age. Newer is better.
    Returns: (score 0-10, age_category)
    """
    if days_old <= 1:
        return 10, "fresh"
    elif days_old <= 3:
        return 8, "recent"
    elif days_old <= 7:
        return 6, "week_old"
    elif days_old <= 14:
        return 4, "two_weeks"
    elif days_old <= 30:
        return 2, "month_old"
    else:
        return 0, "stale"


def _score_applicant_count(count: int) -> Tuple[float, str]:
    """
    Score applicant count. Too many = likely stale, too few = might be niche.
    Returns: (score 0-10, volume_category)
    """
    if count < 10:
        return 9, "very_low_volume"
    elif count < 25:
        return 10, "low_volume"
    elif count < 100:
        return 8, "moderate_volume"
    elif count < 200:
        return 6, "high_volume"
    elif count < 500:
        return 3, "very_high_volume"
    else:
        return 1, "extremely_high_volume"


def _detect_red_flags(metadata: dict) -> List[str]:
    """
    Detect red flags in posting metadata.
    Returns list of red flag strings.
    """
    red_flags = []

    # Posting age red flags
    if metadata.get("posting_age_days", 0) > 30:
        red_flags.append("posting_older_than_30_days")
    if metadata.get("posting_age_days", 0) > 60:
        red_flags.append("posting_older_than_60_days")

    # Applicant volume red flags
    if metadata.get("applicant_count", 0) > 500:
        red_flags.append("extremely_high_applicant_count")
    if metadata.get("applicant_count", 0) > 200:
        red_flags.append("very_high_applicant_count")

    # JD quality red flags
    if metadata.get("has_contradictory_tech", False):
        red_flags.append("contradictory_technologies")
    if metadata.get("has_unrealistic_experience", False):
        red_flags.append("unrealistic_experience_requirements")
    if metadata.get("jd_text_length", 0) < 200:
        red_flags.append("vague_jd_too_short")
    if not metadata.get("technologies_specified", True):
        red_flags.append("no_technologies_specified")
    if not metadata.get("experience_years_specified", True):
        red_flags.append("no_experience_years_specified")

    # Posting quality red flags
    if metadata.get("is_duplicate_posting", False):
        red_flags.append("likely_duplicate_posting")
    if metadata.get("missing_salary", False):
        red_flags.append("missing_salary_information")
    if metadata.get("missing_location", False):
        red_flags.append("missing_location_information")
    if metadata.get("vague_company_name", False):
        red_flags.append("vague_or_hidden_company")

    # Re-posting pattern red flags
    if metadata.get("posted_same_role_multiple_times", False):
        red_flags.append("same_role_reposted_multiple_times")
    if metadata.get("days_since_last_posting", 0) < 7:
        red_flags.append("reposted_within_7_days")

    return red_flags


def detect_staleness(posting_metadata: dict) -> dict:
    """
    Detect staleness and quality issues in a job posting.

    Args:
        posting_metadata: Dict with keys:
            - posting_age_days (int): Days since posted
            - applicant_count (int): Number of applicants
            - company (str, optional): Company name
            - title (str, optional): Job title
            - has_contradictory_tech (bool, optional): Contradictions found
            - has_unrealistic_experience (bool, optional): Experience requirements unrealistic
            - jd_text_length (int, optional): Length of JD text
            - technologies_specified (bool, optional): Tech stack clear
            - experience_years_specified (bool, optional): Years requirement clear
            - is_duplicate_posting (bool, optional): Likely duplicate
            - missing_salary (bool, optional): No salary info
            - missing_location (bool, optional): No location info
            - vague_company_name (bool, optional): Company hidden or vague
            - posted_same_role_multiple_times (bool, optional): Reposting pattern
            - days_since_last_posting (int, optional): Days since previous same-role posting

    Returns:
        Dict with staleness score, red flags, and recommendation.
    """
    # Score posting age
    age_score, age_category = _score_posting_age(posting_metadata.get("posting_age_days", 0))

    # Score applicant volume
    volume_score, volume_category = _score_applicant_count(posting_metadata.get("applicant_count", 0))

    # Detect red flags
    red_flags = _detect_red_flags(posting_metadata)

    # Composite staleness score
    # Posting age carries more weight for staleness detection
    staleness_score = round((age_score * 0.6 + volume_score * 0.4), 2)

    # Apply red flag penalties
    red_flag_penalty = len(red_flags) * 0.5
    staleness_score = max(0, staleness_score - red_flag_penalty)

    # Determine staleness recommendation
    if staleness_score >= 8:
        staleness_status = "FRESH"
        recommendation = "Green light. High-quality recent posting."
    elif staleness_score >= 6:
        staleness_status = "ACCEPTABLE"
        recommendation = "Yellow light. Acceptable but not fresh. Check red flags."
    elif staleness_score >= 4:
        staleness_status = "AGING"
        recommendation = "Orange light. Posting is aging. Recommend human review before submission."
    else:
        staleness_status = "STALE"
        recommendation = "Red flag. Posting likely dead or low quality. Recommend auto-skip."

    return {
        "posting_metadata": {
            "company": posting_metadata.get("company", "unknown"),
            "title": posting_metadata.get("title", "unknown"),
            "posting_age_days": posting_metadata.get("posting_age_days", 0),
            "applicant_count": posting_metadata.get("applicant_count", 0),
        },
        "staleness_score": staleness_score,
        "staleness_status": staleness_status,
        "recommendation": recommendation,
        "age_analysis": {
            "age_days": posting_metadata.get("posting_age_days", 0),
            "age_score": age_score,
            "age_category": age_category
        },
        "volume_analysis": {
            "applicant_count": posting_metadata.get("applicant_count", 0),
            "volume_score": volume_score,
            "volume_category": volume_category
        },
        "red_flags": red_flags,
        "red_flag_count": len(red_flags),
        "is_dead": staleness_status == "STALE",
        "needs_human_review": staleness_status in ["AGING", "STALE"] or len(red_flags) > 2,
        "timestamp": datetime.now().isoformat()
    }


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Read metadata from file (JSON)
        with open(sys.argv[1], "r") as f:
            metadata = json.load(f)
        result = detect_staleness(metadata)
        print(json.dumps(result, indent=2))
    else:
        # Demo with sample postings
        print("=== DEMO 1: Fresh, High-Quality Posting ===\n")
        fresh_posting = {
            "posting_age_days": 1,
            "applicant_count": 18,
            "company": "TechCorp",
            "title": "Senior Java Developer",
            "has_contradictory_tech": False,
            "has_unrealistic_experience": False,
            "jd_text_length": 500,
            "technologies_specified": True,
            "experience_years_specified": True,
            "is_duplicate_posting": False,
            "missing_salary": False,
            "missing_location": False,
        }
        result = detect_staleness(fresh_posting)
        print(json.dumps(result, indent=2))

        print("\n\n=== DEMO 2: Stale Posting with High Volume ===\n")
        stale_posting = {
            "posting_age_days": 60,
            "applicant_count": 520,
            "company": "Unknown Corp",
            "title": "Java Developer",
            "has_contradictory_tech": True,
            "has_unrealistic_experience": True,
            "jd_text_length": 150,
            "technologies_specified": False,
            "experience_years_specified": False,
            "is_duplicate_posting": True,
            "missing_salary": True,
            "missing_location": False,
        }
        result = detect_staleness(stale_posting)
        print(json.dumps(result, indent=2))

        print("\n\n=== DEMO 3: Aging Posting, Some Red Flags ===\n")
        aging_posting = {
            "posting_age_days": 15,
            "applicant_count": 150,
            "company": "BigTech",
            "title": "ML Engineer",
            "has_contradictory_tech": False,
            "has_unrealistic_experience": True,
            "jd_text_length": 300,
            "technologies_specified": True,
            "experience_years_specified": True,
            "is_duplicate_posting": False,
            "missing_salary": False,
            "missing_location": False,
        }
        result = detect_staleness(aging_posting)
        print(json.dumps(result, indent=2))
