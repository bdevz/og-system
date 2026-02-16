"""
Anti-Cannibalization Engine for Agent Rick
===============================================
Prevents Rick's own submissions from competing and sabotaging conversion rates.

Rules:
1. One candidate per job posting (no duplicate profiles to same job)
2. One candidate per client per vendor per week (no competing submissions from same agency)
3. One profile per client ever (consistency over time)
4. Diversify across clients (don't burn all 5 daily apps on one client)

Every cannibalization decision is logged to scoring_log.jsonl.

Usage:
    from anti_cannibalization import check_cannibalization

    decision = check_cannibalization(
        proposed_application_dict,
        application_history_list
    )
    # Returns: {decision: ALLOW/BLOCK, rule_triggered: str, explanation: str}
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

LOG_FILE = Path(__file__).parent / "scoring_log.jsonl"


def check_cannibalization(proposed_app: dict, application_history: list = None) -> dict:
    """
    Check if proposed application would cannibalize a recent submission.

    Args:
        proposed_app: Dict with keys:
            - candidate_id (str): Unique candidate identifier
            - profile_id (str): LinkedIn profile being used
            - job_id (str): Job posting ID
            - client_name (str): Client company name
            - vendor_name (str): Recruitment vendor/agency

        application_history: List of recent applications. Dicts with:
            - application_id (str)
            - candidate_id (str)
            - profile_id (str)
            - job_id (str)
            - client_name (str)
            - vendor_name (str)
            - submitted_date (ISO-8601 timestamp)
            - status (str): PENDING / REJECTED / ACCEPTED / PLACED

    Returns:
        Dict with:
            - decision: "ALLOW" or "BLOCK"
            - rule_triggered: "" or rule ID
            - explanation: String
            - details: Dict with context
    """
    application_history = application_history or []

    # Rule 1: One candidate per job posting
    rule1 = _check_rule_1_duplicate_job_posting(proposed_app, application_history)
    if rule1["blocks"]:
        return {
            "decision": "BLOCK",
            "rule_triggered": "ONE_CANDIDATE_PER_JOB",
            "explanation": rule1["explanation"],
            "details": rule1
        }

    # Rule 2: One candidate per client per vendor per week
    rule2 = _check_rule_2_competing_submissions(proposed_app, application_history)
    if rule2["blocks"]:
        return {
            "decision": "BLOCK",
            "rule_triggered": "ONE_CANDIDATE_PER_CLIENT_PER_VENDOR_PER_WEEK",
            "explanation": rule2["explanation"],
            "details": rule2
        }

    # Rule 3: One profile per client ever
    rule3 = _check_rule_3_profile_consistency(proposed_app, application_history)
    if rule3["blocks"]:
        return {
            "decision": "BLOCK",
            "rule_triggered": "ONE_PROFILE_PER_CLIENT_EVER",
            "explanation": rule3["explanation"],
            "details": rule3
        }

    # Rule 4: Diversify across clients (check daily concentration)
    rule4 = _check_rule_4_diversify_clients(proposed_app, application_history)
    if rule4["blocks"]:
        return {
            "decision": "BLOCK",
            "rule_triggered": "DIVERSIFY_ACROSS_CLIENTS",
            "explanation": rule4["explanation"],
            "details": rule4
        }

    # All rules passed
    result = {
        "decision": "ALLOW",
        "rule_triggered": "",
        "explanation": "Application does not cannibalize recent submissions.",
        "details": {
            "rule_1_pass": True,
            "rule_2_pass": True,
            "rule_3_pass": True,
            "rule_4_pass": True
        }
    }

    _log_cannibalization_decision(proposed_app, result)
    return result


def _check_rule_1_duplicate_job_posting(proposed_app: dict, application_history: list) -> dict:
    """
    Rule 1: One candidate per job posting.
    No two profiles of the same candidate should apply to the same job.
    """
    proposed_candidate = proposed_app.get("candidate_id", "")
    proposed_job = proposed_app.get("job_id", "")

    for app in application_history:
        if (app.get("candidate_id", "") == proposed_candidate and
                app.get("job_id", "") == proposed_job):
            # Same candidate already applied to this job
            return {
                "blocks": True,
                "explanation": f"Candidate {proposed_candidate} already submitted to job {proposed_job}",
                "previous_application_id": app.get("application_id", ""),
                "previous_submitted_date": app.get("submitted_date", ""),
                "previous_profile_id": app.get("profile_id", ""),
                "previous_status": app.get("status", "")
            }

    return {"blocks": False, "explanation": ""}


def _check_rule_2_competing_submissions(proposed_app: dict, application_history: list) -> dict:
    """
    Rule 2: One candidate per client per vendor per week.
    No two applications from the same agency to the same client within 7 days.
    """
    proposed_candidate = proposed_app.get("candidate_id", "")
    proposed_client = proposed_app.get("client_name", "").lower()
    proposed_vendor = proposed_app.get("vendor_name", "").lower()

    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)

    for app in application_history:
        app_candidate = app.get("candidate_id", "")
        app_client = app.get("client_name", "").lower()
        app_vendor = app.get("vendor_name", "").lower()

        if (app_candidate == proposed_candidate and
                app_client == proposed_client and
                app_vendor == proposed_vendor):

            submitted_date_str = app.get("submitted_date", "")
            try:
                submitted_date = datetime.fromisoformat(submitted_date_str)
                if submitted_date > seven_days_ago:
                    days_ago = (now - submitted_date).days
                    return {
                        "blocks": True,
                        "explanation": f"Competing submission from same vendor to same client {days_ago} days ago",
                        "previous_application_id": app.get("application_id", ""),
                        "previous_submitted_date": submitted_date_str,
                        "days_ago": days_ago,
                        "candidate_id": proposed_candidate,
                        "client_name": proposed_client,
                        "vendor_name": proposed_vendor
                    }
            except:
                pass

    return {"blocks": False, "explanation": ""}


def _check_rule_3_profile_consistency(proposed_app: dict, application_history: list) -> dict:
    """
    Rule 3: One profile per client ever.
    Never apply to the same client using different profiles of the same candidate.
    Maintains consistency in recruiter relationships.
    """
    proposed_candidate = proposed_app.get("candidate_id", "")
    proposed_client = proposed_app.get("client_name", "").lower()
    proposed_profile = proposed_app.get("profile_id", "")

    for app in application_history:
        app_candidate = app.get("candidate_id", "")
        app_client = app.get("client_name", "").lower()
        app_profile = app.get("profile_id", "")

        if (app_candidate == proposed_candidate and
                app_client == proposed_client):

            if app_profile and proposed_profile and app_profile != proposed_profile:
                # Same candidate to same client, but with different profile IDs
                return {
                    "blocks": True,
                    "explanation": f"Candidate {proposed_candidate} already submitted to {proposed_client} using different profile",
                    "previous_application_id": app.get("application_id", ""),
                    "previous_profile_id": app_profile,
                    "proposed_profile_id": proposed_profile,
                    "previous_submitted_date": app.get("submitted_date", ""),
                    "candidate_id": proposed_candidate,
                    "client_name": proposed_client,
                    "message": "Profile consistency violation"
                }

    return {"blocks": False, "explanation": ""}


def _check_rule_4_diversify_clients(proposed_app: dict, application_history: list) -> dict:
    """
    Rule 4: Diversify across clients.
    Don't submit all 5 daily applications to the same client.
    If candidate already has 3+ applications to same client today, block.
    """
    proposed_candidate = proposed_app.get("candidate_id", "")
    proposed_client = proposed_app.get("client_name", "").lower()

    today = datetime.now(timezone.utc).date()
    today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)

    apps_to_client_today = 0
    for app in application_history:
        if (app.get("candidate_id", "") == proposed_candidate and
                app.get("client_name", "").lower() == proposed_client):

            submitted_date_str = app.get("submitted_date", "")
            try:
                submitted_date = datetime.fromisoformat(submitted_date_str)
                if submitted_date > today_start:
                    apps_to_client_today += 1
            except:
                pass

    # If already 3+ apps to same client today, block this one
    if apps_to_client_today >= 3:
        return {
            "blocks": True,
            "explanation": f"Already {apps_to_client_today} applications to {proposed_client} today. Diversify.",
            "applications_to_client_today": apps_to_client_today,
            "limit": 3,
            "candidate_id": proposed_candidate,
            "client_name": proposed_client,
            "message": "Concentration too high. Spread applications across different clients."
        }

    return {"blocks": False, "explanation": ""}


def _log_cannibalization_decision(proposed_app: dict, decision: dict):
    """Log cannibalization decision to scoring_log.jsonl."""
    log_entry = {
        "event_type": "cannibalization_check",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "candidate_id": proposed_app.get("candidate_id", ""),
        "job_id": proposed_app.get("job_id", ""),
        "client_name": proposed_app.get("client_name", ""),
        "decision": decision["decision"],
        "rule_triggered": decision["rule_triggered"],
        "explanation": decision["explanation"]
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

        proposed_app = data.get("proposed_app", {})
        application_history = data.get("application_history", [])

        result = check_cannibalization(proposed_app, application_history)
        print(json.dumps(result, indent=2))
    else:
        # Demo
        sample_proposed = {
            "candidate_id": "C-042",
            "profile_id": "LI-042-A",
            "job_id": "J-1234",
            "client_name": "Acme Corp",
            "vendor_name": "TrueNorth"
        }
        sample_history = [
            {
                "application_id": "APP-001",
                "candidate_id": "C-042",
                "profile_id": "LI-042-A",
                "job_id": "J-5678",
                "client_name": "Acme Corp",
                "vendor_name": "TrueNorth",
                "submitted_date": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "status": "PENDING"
            }
        ]
        result = check_cannibalization(sample_proposed, sample_history)
        print(json.dumps(result, indent=2))
