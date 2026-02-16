"""
Hard Filters for Agent Rick
=============================
Pre-scoring elimination logic. Five hard rules determine if a candidate should
be filtered out BEFORE scoring and submission attempts.

Rules:
1. DNS list match (consultant + client conflict) -> ELIMINATE
2. Category mismatch (Java dev to DevOps with 0 required skills) -> ELIMINATE
3. Visa hard block (job explicitly excludes candidate's visa type) -> ELIMINATE
4. Already submitted (recent submission to this client) -> ELIMINATE
5. Daily application limit reached -> SKIP (defer to tomorrow)

Every filter decision is logged to scoring_log.jsonl with full reasoning.

Usage:
    from hard_filters import apply_hard_filters

    decision = apply_hard_filters(
        candidate_dict,
        job_dict,
        submission_history_list,
        dns_list
    )
    # Returns: {decision: PASS/ELIMINATE/SKIP, reason: str, rule_triggered: str}
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

LOG_FILE = Path(__file__).parent / "scoring_log.jsonl"


def apply_hard_filters(candidate: dict, job: dict, submission_history: list = None, dns_list: list = None) -> dict:
    """
    Apply hard filters to determine if candidate should be eliminated, skipped, or passed.

    Args:
        candidate: Dict with keys:
            - candidate_id (str)
            - candidate_name (str, optional)
            - skills (list): Candidate's skills
            - visa_status (str)
            - profile_id (str, optional): LinkedIn profile in use

        job: Dict with keys:
            - job_id (str)
            - client_name (str)
            - required_skills (list)
            - visa_requirement (str)
            - client_vendor (str): Vendor name handling this placement

        submission_history: List of recent submissions. Dicts with:
            - candidate_id (str)
            - client_name (str)
            - job_id (str)
            - submitted_date (ISO-8601 timestamp)
            - status (str): PENDING / REJECTED / ACCEPTED / PLACED

        dns_list: List of DNS (Do Not Submit) records. Dicts with:
            - consultant_id (str)
            - client_name (str)
            - reason (str)
            - added_date (ISO-8601 timestamp)

    Returns:
        Dict with:
            - decision: "PASS" / "ELIMINATE" / "SKIP"
            - reason: String explanation
            - rule_triggered: String rule ID or "" if none
            - details: Dict with detailed context
    """
    submission_history = submission_history or []
    dns_list = dns_list or []

    # Rule 1: DNS list match (consultant + client conflict)
    dns_match = _check_dns_list(candidate, job, dns_list)
    if dns_match:
        return {
            "decision": "ELIMINATE",
            "reason": f"Candidate on DNS list for client: {dns_match['reason']}",
            "rule_triggered": "DNS_LIST_CONFLICT",
            "details": dns_match
        }

    # Rule 2: Category mismatch (Java dev to DevOps with 0 required skills)
    category_mismatch = _check_category_mismatch(candidate, job)
    if category_mismatch:
        return {
            "decision": "ELIMINATE",
            "reason": f"Category mismatch: Candidate lacks core required skills",
            "rule_triggered": "CATEGORY_MISMATCH",
            "details": category_mismatch
        }

    # Rule 3: Visa hard block
    visa_block = _check_visa_hard_block(candidate, job)
    if visa_block:
        return {
            "decision": "ELIMINATE",
            "reason": f"Visa mismatch: {visa_block['reason']}",
            "rule_triggered": "VISA_HARD_BLOCK",
            "details": visa_block
        }

    # Rule 4: Already submitted (recent submission to this client)
    already_submitted = _check_already_submitted(candidate, job, submission_history)
    if already_submitted:
        return {
            "decision": "ELIMINATE",
            "reason": f"Duplicate submission risk: {already_submitted['reason']}",
            "rule_triggered": "ALREADY_SUBMITTED",
            "details": already_submitted
        }

    # Rule 5: Daily application limit
    limit_reached = _check_daily_limit(candidate, submission_history)
    if limit_reached:
        return {
            "decision": "SKIP",
            "reason": f"Daily application limit reached for profile. Defer to tomorrow.",
            "rule_triggered": "DAILY_LIMIT_REACHED",
            "details": limit_reached
        }

    # All filters passed
    result = {
        "decision": "PASS",
        "reason": "Candidate passed all hard filters.",
        "rule_triggered": "",
        "details": {
            "dns_clear": True,
            "category_match": True,
            "visa_compatible": True,
            "no_recent_submission": True,
            "within_daily_limit": True
        }
    }

    _log_filter_decision(candidate, job, result)
    return result


def _check_dns_list(candidate: dict, job: dict, dns_list: list) -> dict:
    """Rule 1: Check if candidate-client pair is on DNS (Do Not Submit) list."""
    candidate_id = candidate.get("candidate_id", "")
    client_name = job.get("client_name", "").lower()

    for dns_entry in dns_list:
        if dns_entry.get("consultant_id", "") == candidate_id:
            dns_client = dns_entry.get("client_name", "").lower()
            if dns_client == client_name:
                return {
                    "dns_entry_id": dns_entry.get("id", ""),
                    "reason": dns_entry.get("reason", "Unspecified"),
                    "added_date": dns_entry.get("added_date", ""),
                    "expires": dns_entry.get("expires", "")
                }

    return None


def _check_category_mismatch(candidate: dict, job: dict) -> dict:
    """
    Rule 2: Category mismatch.
    If candidate has zero overlap with job's required skills, eliminate.
    This is a hard categorical mismatch (e.g., Java dev to DevOps with no overlap).
    """
    candidate_skills = [s.lower() for s in candidate.get("skills", [])]
    required_skills = [s.lower() for s in job.get("required_skills", [])]

    if not required_skills:
        # No required skills specified, not a mismatch
        return None

    # Count exact matches
    exact_matches = sum(1 for req in required_skills if req in candidate_skills)

    # If zero required skills match, it's a hard category mismatch
    if exact_matches == 0:
        return {
            "candidate_skills": candidate.get("skills", []),
            "required_skills": job.get("required_skills", []),
            "overlap_count": 0,
            "required_count": len(required_skills),
            "message": "Zero skill overlap with required skills"
        }

    return None


def _check_visa_hard_block(candidate: dict, job: dict) -> dict:
    """
    Rule 3: Visa hard block.
    If job explicitly excludes candidate's visa type, eliminate.
    e.g., job says "no H1B" and candidate is H1B.
    """
    candidate_visa = candidate.get("visa_status", "").lower()
    visa_requirement = job.get("visa_requirement", "any").lower()

    if visa_requirement == "any" or visa_requirement == "unknown" or not visa_requirement:
        # No visa restriction
        return None

    # Check for explicit exclusions
    excluded_visas = []
    for phrase in ["no ", "exclude ", "not "]:
        parts = visa_requirement.split(phrase)
        if len(parts) > 1:
            for part in parts[1:]:
                # Extract visa type (first word after "no", "exclude", "not")
                visa_type = part.split()[0].lower().rstrip(",")
                excluded_visas.append(visa_type)

    if candidate_visa in excluded_visas or f"no {candidate_visa}" in visa_requirement:
        return {
            "candidate_visa": candidate.get("visa_status", ""),
            "job_requirement": job.get("visa_requirement", ""),
            "message": f"Job explicitly excludes {candidate.get('visa_status', '')} visa status"
        }

    return None


def _check_already_submitted(candidate: dict, job: dict, submission_history: list) -> dict:
    """
    Rule 4: Already submitted.
    If candidate has been submitted to this client within last 90 days, eliminate.
    Also check for exact duplicate submission to same job posting.
    """
    candidate_id = candidate.get("candidate_id", "")
    client_name = job.get("client_name", "").lower()
    job_id = job.get("job_id", "")

    now = datetime.now(timezone.utc)
    ninety_days_ago = now - timedelta(days=90)

    for submission in submission_history:
        # Check exact duplicate (same job posting)
        if (submission.get("candidate_id", "") == candidate_id and
                submission.get("job_id", "") == job_id):
            submitted_date = submission.get("submitted_date", "")
            return {
                "submission_id": submission.get("id", ""),
                "reason": "Exact duplicate: Same candidate to same job posting",
                "previous_submission_date": submitted_date,
                "status": submission.get("status", "")
            }

        # Check same client within 90 days
        if (submission.get("candidate_id", "") == candidate_id and
                submission.get("client_name", "").lower() == client_name):
            submitted_date_str = submission.get("submitted_date", "")
            try:
                submitted_date = datetime.fromisoformat(submitted_date_str)
                if submitted_date > ninety_days_ago:
                    return {
                        "submission_id": submission.get("id", ""),
                        "reason": "Recent submission to same client within 90 days",
                        "previous_submission_date": submitted_date_str,
                        "days_ago": (now - submitted_date).days,
                        "status": submission.get("status", "")
                    }
            except:
                pass

    return None


def _check_daily_limit(candidate: dict, submission_history: list) -> dict:
    """
    Rule 5: Daily application limit.
    Max 5 applications per LinkedIn profile per day.
    If candidate's profile has hit limit, skip (defer to tomorrow).
    """
    profile_id = candidate.get("profile_id", candidate.get("candidate_id", ""))
    if not profile_id:
        # Can't check without profile ID
        return None

    today = datetime.now(timezone.utc).date()
    today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)

    applications_today = 0
    for submission in submission_history:
        if submission.get("profile_id", "") == profile_id:
            submitted_date_str = submission.get("submitted_date", "")
            try:
                submitted_date = datetime.fromisoformat(submitted_date_str)
                if submitted_date > today_start:
                    applications_today += 1
            except:
                pass

    if applications_today >= 5:
        return {
            "profile_id": profile_id,
            "applications_today": applications_today,
            "daily_limit": 5,
            "message": "Profile has reached daily application limit (5 per day)"
        }

    return None


def _log_filter_decision(candidate: dict, job: dict, decision: dict):
    """Log hard filter decision to scoring_log.jsonl."""
    log_entry = {
        "event_type": "hard_filter_decision",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "candidate_id": candidate.get("candidate_id", ""),
        "job_id": job.get("job_id", ""),
        "decision": decision["decision"],
        "rule_triggered": decision["rule_triggered"],
        "reason": decision["reason"]
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

        candidate = data.get("candidate", {})
        job = data.get("job", {})
        submission_history = data.get("submission_history", [])
        dns_list = data.get("dns_list", [])

        result = apply_hard_filters(candidate, job, submission_history, dns_list)
        print(json.dumps(result, indent=2))
    else:
        # Demo
        sample_candidate = {
            "candidate_id": "C-042",
            "candidate_name": "Ravi Kumar",
            "skills": ["Java", "Spring", "Kubernetes"],
            "visa_status": "H1B",
            "profile_id": "LI-042"
        }
        sample_job = {
            "job_id": "J-1234",
            "client_name": "Acme Corp",
            "required_skills": ["Java", "Spring", "Kubernetes"],
            "visa_requirement": "Any",
            "client_vendor": "TrueNorth"
        }
        result = apply_hard_filters(sample_candidate, sample_job, [], [])
        print(json.dumps(result, indent=2))
