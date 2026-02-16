"""
Match Calculator for Agent Rick
=================================
Computes candidate-job match scores using deterministic weighted scoring.
AI gathers inputs. This script does the math. Every calculation is logged.

Usage:
    from match_calculator import calculate_match, calculate_match_matrix

    result = calculate_match({
        "candidate_id": "C-042",
        "candidate_name": "Ravi Kumar",
        "skills": ["Java", "Spring", "Microservices", "Kubernetes"],
        "years_experience": 7,
        "rate": 85,
        "location": "Remote",
        "visa_status": "H1B"
    }, {
        "job_id": "J-1234",
        "job_title": "Microservices Architect",
        "required_skills": ["Java", "Spring", "Kubernetes"],
        "preferred_skills": ["Docker", "AWS"],
        "years_required": "5-8",
        "posted_rate": 90,
        "location": "Remote",
        "visa_requirement": "Any",
        "posting_freshness_hours": 18,
        "vendor_tier": "tier_1"
    })
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path


WEIGHTS_FILE = Path(__file__).parent / "match_weights.json"
LOG_FILE = Path(__file__).parent / "scoring_log.jsonl"


def load_weights() -> dict:
    """Load weights from the human-editable JSON config."""
    with open(WEIGHTS_FILE, "r") as f:
        return json.load(f)


def _calculate_skill_overlap_required(candidate_skills: list, required_skills: list, equivalencies: dict) -> float:
    """
    Calculate skill overlap for required skills.
    Returns percentage of required skills candidate has (with equivalency credit).
    """
    if not required_skills:
        return 1.0

    matched = 0.0
    for req_skill in required_skills:
        req_lower = req_skill.lower()

        # Check exact match
        if any(cs.lower() == req_lower for cs in candidate_skills):
            matched += 1.0
        else:
            # Check equivalency mapping
            for candidate_skill in candidate_skills:
                cand_lower = candidate_skill.lower()
                if req_lower in equivalencies and cand_lower in equivalencies[req_lower]:
                    equivalency_score = equivalencies[req_lower][cand_lower]
                    matched += equivalency_score
                    break

    return min(1.0, matched / len(required_skills))


def _calculate_skill_overlap_preferred(candidate_skills: list, preferred_skills: list, equivalencies: dict) -> float:
    """
    Calculate bonus for preferred skills (capped at 1.0).
    Candidates who have preferred skills get bonus points.
    """
    if not preferred_skills:
        return 0.0

    matched = 0.0
    for pref_skill in preferred_skills:
        pref_lower = pref_skill.lower()

        # Check exact match
        if any(cs.lower() == pref_lower for cs in candidate_skills):
            matched += 1.0
        else:
            # Check equivalency
            for candidate_skill in candidate_skills:
                cand_lower = candidate_skill.lower()
                if pref_lower in equivalencies and cand_lower in equivalencies[pref_lower]:
                    equivalency_score = equivalencies[pref_lower][cand_lower]
                    matched += equivalency_score
                    break

    # Bonus: each preferred skill is worth 1/len(preferred_skills), capped at 1.0
    bonus = min(1.0, matched / len(preferred_skills) if preferred_skills else 0.0)
    return bonus


def _calculate_experience_alignment(candidate_years: int, required_range: str, brackets: dict) -> float:
    """
    Score experience alignment based on required years.
    required_range format: "5-8" or "3+" or "any"
    """
    if required_range.lower() == "any" or not required_range:
        return 1.0

    try:
        if "+" in required_range:
            min_years = int(required_range.split("+")[0])
            max_years = None
        else:
            parts = required_range.split("-")
            min_years = int(parts[0])
            max_years = int(parts[1]) if len(parts) > 1 else None

        # Calculate gap
        if candidate_years >= min_years and (max_years is None or candidate_years <= max_years):
            # Within range
            return 1.0
        elif candidate_years < min_years:
            gap = min_years - candidate_years
            if gap <= 2:
                return float(brackets.get("yrs_under_minus_1_to_2", 0.70))
            else:
                return float(brackets.get("yrs_under_minus_3", 0.30))
        else:
            # Overqualified
            gap = candidate_years - (max_years or min_years)
            if gap <= 3:
                return float(brackets.get("yrs_over_plus_1_to_3", 0.90))
            else:
                return float(brackets.get("yrs_over_plus_4_plus", 0.70))
    except:
        return 0.5


def _calculate_rate_compatibility(candidate_rate: float, posted_rate: float, brackets: dict) -> float:
    """
    Score rate compatibility.
    Candidate rate >= posted_rate = 100%.
    Candidate rate 90-100% of posted = 50%.
    Candidate rate < 90% of posted = 10%.
    """
    if candidate_rate >= posted_rate:
        return float(brackets.get("meets_min", 1.0))

    pct_of_posted = candidate_rate / posted_rate
    if pct_of_posted >= 0.90:
        return float(brackets.get("within_10_pct_below", 0.50))
    else:
        return float(brackets.get("more_than_10_pct_below", 0.10))


def _calculate_location_match(candidate_location: str, candidate_remote: bool, job_location: str, job_remote: bool, brackets: dict) -> float:
    """
    Score location and remote preference match.
    Exact match = 100%.
    Remote + hybrid mix = 70%.
    Mismatch = 20%.
    """
    cand_loc_lower = candidate_location.lower()
    job_loc_lower = job_location.lower()

    if cand_loc_lower == job_loc_lower:
        return float(brackets.get("exact_match", 1.0))

    if candidate_remote and (job_remote or "hybrid" in job_loc_lower):
        return float(brackets.get("remote_plus_hybrid", 0.70))

    if "remote" in cand_loc_lower and "remote" in job_loc_lower:
        return float(brackets.get("exact_match", 1.0))

    return float(brackets.get("mismatch", 0.20))


def _calculate_visa_compatibility(candidate_visa: str, job_visa_requirement: str, brackets: dict) -> float:
    """
    Score visa compatibility.
    Job accepts candidate's visa type = 100%.
    Job visa requirement unknown = 50%.
    Job explicitly excludes candidate's visa = 0%.
    """
    if job_visa_requirement.lower() in ["any", "unknown", ""]:
        return float(brackets.get("unknown", 0.50))

    allowed = [v.strip().lower() for v in job_visa_requirement.split(",")]
    cand_visa_lower = candidate_visa.lower()

    if cand_visa_lower in allowed or "any" in allowed:
        return float(brackets.get("accepted", 1.0))
    elif f"no {cand_visa_lower}" in " ".join(allowed) or f"exclude {cand_visa_lower}" in " ".join(allowed):
        return float(brackets.get("excluded", 0.0))
    else:
        # Unknown but candidate visa not explicitly excluded
        return float(brackets.get("unknown", 0.50))


def _calculate_posting_freshness(freshness_hours: int, brackets: dict) -> float:
    """
    Score based on posting freshness.
    < 24 hours = 100% (hot posting).
    1-3 days = 70%.
    3-7 days = 40%.
    Older = assume 40%.
    """
    if freshness_hours < 24:
        return float(brackets.get("less_than_24h", 1.0))
    elif freshness_hours < 72:  # 3 days
        return float(brackets.get("1_to_3_days", 0.70))
    else:
        return float(brackets.get("3_to_7_days", 0.40))


def _calculate_vendor_tier(vendor_tier: str, brackets: dict) -> float:
    """
    Score based on vendor tier quality.
    tier_1 = 100% (established vendor).
    tier_2 = 70% (decent vendor).
    tier_3 = 40% (newer/smaller vendor).
    """
    tier_key = vendor_tier.lower().replace(" ", "_")
    return float(brackets.get(tier_key, 0.40))


def calculate_match(candidate: dict, job: dict) -> dict:
    """
    Calculate match score for a single candidate-job pair.

    Args:
        candidate: Dict with keys:
            - candidate_id (str): Unique identifier
            - candidate_name (str, optional): For readability
            - skills (list): Candidate's skills/technologies
            - years_experience (int): Total years in field
            - rate (float): Candidate's rate in $/hr or K/yr
            - location (str): City or "Remote"
            - remote_preference (bool, optional): Can work remote
            - visa_status (str): H1B, OPT, CPT, GC, Citizen, TN, L1, etc.

        job: Dict with keys:
            - job_id (str): Unique identifier
            - job_title (str): Role title
            - required_skills (list): Must-have skills
            - preferred_skills (list, optional): Nice-to-have skills
            - years_required (str): "5-8" or "3+" or "any"
            - posted_rate (float): Job posting rate
            - location (str): City or "Remote"
            - remote_allowed (bool, optional): Job allows remote
            - visa_requirement (str): "Any" or comma-separated visa types or "no H1B" etc.
            - posting_freshness_hours (int): Hours since posted
            - vendor_tier (str): "tier_1", "tier_2", or "tier_3"

    Returns:
        Dict with score, breakdown, recommendation, and full details.
    """
    config = load_weights()
    weights = config["weights"]
    brackets = {
        "experience": config.get("experience_brackets", {}),
        "rate": config.get("rate_brackets", {}),
        "location": config.get("location_brackets", {}),
        "visa": config.get("visa_brackets", {}),
        "freshness": config.get("posting_freshness_brackets", {}),
        "vendor": config.get("vendor_tier_brackets", {})
    }
    equivalencies = config.get("skill_equivalency", {})
    thresholds = config.get("thresholds", {})

    # Score each factor
    required_skills_score = _calculate_skill_overlap_required(
        candidate.get("skills", []),
        job.get("required_skills", []),
        equivalencies
    )
    preferred_skills_score = _calculate_skill_overlap_preferred(
        candidate.get("skills", []),
        job.get("preferred_skills", []),
        equivalencies
    )
    experience_score = _calculate_experience_alignment(
        candidate.get("years_experience", 0),
        job.get("years_required", "any"),
        brackets["experience"]
    )
    rate_score = _calculate_rate_compatibility(
        candidate.get("rate", 0),
        job.get("posted_rate", 0),
        brackets["rate"]
    )
    location_score = _calculate_location_match(
        candidate.get("location", ""),
        candidate.get("remote_preference", False),
        job.get("location", ""),
        job.get("remote_allowed", False),
        brackets["location"]
    )
    visa_score = _calculate_visa_compatibility(
        candidate.get("visa_status", ""),
        job.get("visa_requirement", "any"),
        brackets["visa"]
    )
    freshness_score = _calculate_posting_freshness(
        job.get("posting_freshness_hours", 168),
        brackets["freshness"]
    )
    vendor_score = _calculate_vendor_tier(
        job.get("vendor_tier", "tier_3"),
        brackets["vendor"]
    )

    # Weighted contributions
    required_contribution = required_skills_score * weights["skill_overlap_required"]
    preferred_contribution = preferred_skills_score * weights["skill_overlap_preferred"]
    experience_contribution = experience_score * weights["experience_alignment"]
    rate_contribution = rate_score * weights["rate_compatibility"]
    location_contribution = location_score * weights["location_remote_match"]
    visa_contribution = visa_score * weights["visa_compatibility"]
    freshness_contribution = freshness_score * weights["posting_freshness"]
    vendor_contribution = vendor_score * weights["vendor_tier_quality"]

    # Composite score (0-100)
    composite = round(
        (required_contribution + preferred_contribution + experience_contribution +
         rate_contribution + location_contribution + visa_contribution +
         freshness_contribution + vendor_contribution) * 100,
        2
    )

    # Determine recommendation
    if composite >= thresholds.get("strong_match", 80):
        recommendation = "STRONG"
        recommendation_label = "Strong match. Submit with confidence."
    elif composite >= thresholds.get("good_match", 70):
        recommendation = "GOOD"
        recommendation_label = "Good match. Submit."
    elif composite >= thresholds.get("borderline_match", 60):
        recommendation = "BORDERLINE"
        recommendation_label = "Borderline match. Flag for human review."
    else:
        recommendation = "WEAK"
        recommendation_label = "Weak match. Block unless exceptional circumstances."

    result = {
        "candidate_id": candidate.get("candidate_id", "UNKNOWN"),
        "candidate_name": candidate.get("candidate_name", ""),
        "job_id": job.get("job_id", "UNKNOWN"),
        "job_title": job.get("job_title", ""),
        "score": composite,
        "recommendation": recommendation,
        "recommendation_label": recommendation_label,
        "breakdown": {
            "skill_overlap_required": {
                "raw_score": round(required_skills_score, 3),
                "weight": weights["skill_overlap_required"],
                "contribution": round(required_contribution * 100, 3),
                "matched_skills": [s for s in candidate.get("skills", []) if any(r.lower() == s.lower() or r.lower() in str(equivalencies).lower() for r in job.get("required_skills", []))]
            },
            "skill_overlap_preferred": {
                "raw_score": round(preferred_skills_score, 3),
                "weight": weights["skill_overlap_preferred"],
                "contribution": round(preferred_contribution * 100, 3)
            },
            "experience_alignment": {
                "raw_score": round(experience_score, 3),
                "weight": weights["experience_alignment"],
                "contribution": round(experience_contribution * 100, 3),
                "candidate_years": candidate.get("years_experience", 0),
                "required_years": job.get("years_required", "any")
            },
            "rate_compatibility": {
                "raw_score": round(rate_score, 3),
                "weight": weights["rate_compatibility"],
                "contribution": round(rate_contribution * 100, 3),
                "candidate_rate": candidate.get("rate", 0),
                "posted_rate": job.get("posted_rate", 0)
            },
            "location_remote_match": {
                "raw_score": round(location_score, 3),
                "weight": weights["location_remote_match"],
                "contribution": round(location_contribution * 100, 3),
                "candidate_location": candidate.get("location", ""),
                "job_location": job.get("location", "")
            },
            "visa_compatibility": {
                "raw_score": round(visa_score, 3),
                "weight": weights["visa_compatibility"],
                "contribution": round(visa_contribution * 100, 3),
                "candidate_visa": candidate.get("visa_status", ""),
                "job_requirement": job.get("visa_requirement", "any")
            },
            "posting_freshness": {
                "raw_score": round(freshness_score, 3),
                "weight": weights["posting_freshness"],
                "contribution": round(freshness_contribution * 100, 3),
                "freshness_hours": job.get("posting_freshness_hours", 168)
            },
            "vendor_tier_quality": {
                "raw_score": round(vendor_score, 3),
                "weight": weights["vendor_tier_quality"],
                "contribution": round(vendor_contribution * 100, 3),
                "vendor_tier": job.get("vendor_tier", "tier_3")
            }
        },
        "weights_version": config["version"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Log the calculation
    _log_calculation(result)

    return result


def calculate_match_matrix(candidates: list, jobs: list) -> list:
    """
    Calculate match scores for all candidate-job pairs and return sorted by score descending.

    Args:
        candidates: List of candidate dicts.
        jobs: List of job dicts.

    Returns:
        List of all results sorted by score descending (best matches first).
    """
    results = []
    for candidate in candidates:
        for job in jobs:
            result = calculate_match(candidate, job)
            results.append(result)

    results.sort(key=lambda x: x["score"], reverse=True)

    # Add rank
    for i, r in enumerate(results):
        r["rank"] = i + 1

    return results


def _log_calculation(result: dict):
    """Append calculation to scoring log (append-only audit trail)."""
    log_entry = {
        "event_type": "match_calculation",
        "timestamp": result["timestamp"],
        "candidate_id": result["candidate_id"],
        "job_id": result["job_id"],
        "score": result["score"],
        "recommendation": result["recommendation"],
        "breakdown": {k: v["raw_score"] for k, v in result["breakdown"].items()},
        "weights_version": result["weights_version"]
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Read input from file
        with open(sys.argv[1], "r") as f:
            data = json.load(f)
        if isinstance(data, dict) and "candidates" in data and "jobs" in data:
            results = calculate_match_matrix(data["candidates"], data["jobs"])
        elif isinstance(data, list):
            # List of [candidate, job] pairs
            results = [calculate_match(pair[0], pair[1]) for pair in data]
        else:
            # Single candidate-job pair
            results = calculate_match(data.get("candidate", {}), data.get("job", {}))
        print(json.dumps(results, indent=2))
    else:
        # Demo with sample data
        sample_candidate = {
            "candidate_id": "C-042",
            "candidate_name": "Ravi Kumar",
            "skills": ["Java", "Spring", "Spring Boot", "Microservices", "Kubernetes", "Docker", "AWS"],
            "years_experience": 7,
            "rate": 85,
            "location": "Remote",
            "remote_preference": True,
            "visa_status": "H1B"
        }
        sample_job = {
            "job_id": "J-1234",
            "job_title": "Microservices Architect",
            "required_skills": ["Java", "Spring", "Kubernetes"],
            "preferred_skills": ["Docker", "AWS", "CI/CD"],
            "years_required": "5-8",
            "posted_rate": 90,
            "location": "Remote",
            "remote_allowed": True,
            "visa_requirement": "Any",
            "posting_freshness_hours": 18,
            "vendor_tier": "tier_1"
        }
        result = calculate_match(sample_candidate, sample_job)
        print(json.dumps(result, indent=2))
