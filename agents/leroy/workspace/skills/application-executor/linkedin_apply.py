"""
LinkedIn Application Executor for Agent Leroy
==============================================
Executes LinkedIn job applications with pre-flight checks, timing simulation,
error handling, and complete audit trail.

Usage:
    from application_executor.linkedin_apply import execute_application, preflight_check

    preflight = preflight_check({
        "profile_id": "P-001",
        "health_state": "GREEN",
        "daily_app_count": 1,
        "last_app_minutes_ago": 12,
        "proxy_ip": "192.0.2.15"
    })

    if preflight["status"] == "OK":
        result = execute_application({
            "profile_id": "P-001",
            "job_id": "JOB-98765",
            "job_title": "Senior Python Developer",
            "company_name": "TechCorp",
            "z_approval_id": "SUBMIT-5678",
            "proxy_ip": "192.0.2.15"
        })
"""

import json
import random
from datetime import datetime, timezone
from pathlib import Path


def preflight_check(inputs: dict) -> dict:
    """
    Perform pre-flight checks before executing application.

    Args:
        inputs: Dict with keys:
            - profile_id (str): Profile identifier
            - health_state (str): GREEN, YELLOW, ORANGE, RED
            - daily_app_count (int): Applications submitted today already
            - last_app_minutes_ago (int): Minutes since last application
            - proxy_ip (str): Proxy IP to use

    Returns:
        Dict with check results and any blocking issues.
    """
    issues = []
    warnings = []

    # Check health state
    if inputs["health_state"] == "RED":
        issues.append("Profile in RED health state - ZERO activity allowed")

    if inputs["health_state"] == "ORANGE":
        issues.append("Profile in ORANGE health state - no applications allowed")

    if inputs["health_state"] == "YELLOW" and inputs.get("daily_app_count", 0) >= 2:
        issues.append("Profile in YELLOW state - daily app limit (2) already reached")

    # Check daily limit (GREEN = tier limit, YELLOW = 2)
    tier_limits = {"A": 5, "B": 2, "C": 1, "D": 0}
    tier = inputs.get("tier", "B")
    tier_limit = tier_limits.get(tier, 2)

    if inputs["health_state"] == "GREEN":
        if inputs.get("daily_app_count", 0) >= tier_limit:
            issues.append(f"Tier {tier} daily application limit ({tier_limit}) reached")
    elif inputs["health_state"] == "YELLOW":
        if inputs.get("daily_app_count", 0) >= 2:
            issues.append("YELLOW state: maximum 2 applications per day, limit reached")

    # Check minimum gap between applications
    if inputs.get("last_app_minutes_ago", 0) < 5:
        issues.append("Less than 5 minutes since last application - wait before proceeding")

    # Check proxy validity
    if not inputs.get("proxy_ip"):
        issues.append("No proxy IP configured")

    # Z approval required
    if not inputs.get("z_approval_id"):
        issues.append("No Z approval ID - must obtain Z approval before application")

    if inputs.get("proxy_ip") in inputs.get("ips_used_today", []):
        warnings.append("Proxy IP may have been used on another profile today - risk of pattern detection")

    status = "OK" if not issues else "BLOCKED"
    status_warnings = "WARNINGS" if warnings else "CLEAR"

    result = {
        "status": status,
        "warnings_status": status_warnings,
        "profile_id": inputs["profile_id"],
        "health_state": inputs["health_state"],
        "daily_app_count": inputs.get("daily_app_count", 0),
        "tier": tier,
        "tier_daily_limit": tier_limit,
        "issues": issues,
        "warnings": warnings,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return result


def execute_application(inputs: dict) -> dict:
    """
    Execute LinkedIn job application with full workflow simulation.

    Args:
        inputs: Dict with keys:
            - profile_id (str): Profile ID
            - job_id (str): LinkedIn job ID
            - job_title (str): Job title
            - company_name (str): Company name
            - application_package (dict, optional): Resume version, cover letter, etc.
            - z_approval_id (str): Z's approval ID
            - proxy_ip (str): Proxy IP to use
            - session_id (str): Session identifier

    Returns:
        Dict with application result, screenshot reference, and audit trail.
    """
    profile_id = inputs["profile_id"]
    job_id = inputs["job_id"]
    z_approval_id = inputs["z_approval_id"]
    proxy_ip = inputs["proxy_ip"]

    now = datetime.now(timezone.utc)

    # Simulate reading job description (30-60 seconds)
    reading_time = random.randint(30, 60)

    # Generate application ID
    application_id = f"APP-{now.strftime('%Y%m%d%H%M%S')}-{random.randint(10000, 99999)}"

    # Simulate form fields that would be filled
    form_fields_simulated = [
        {"name": "resume", "status": "filled", "version": inputs.get("application_package", {}).get("resume_version", "default")},
        {"name": "contact_email", "status": "autofilled"},
        {"name": "phone", "status": "autofilled"},
        {"name": "linkedin_profile", "status": "autofilled"}
    ]

    # Check for cover letter
    if inputs.get("application_package", {}).get("cover_letter"):
        form_fields_simulated.append({
            "name": "cover_letter",
            "status": "filled",
            "variant": "custom"
        })

    # Simulate submission timing
    submission_time = datetime.fromtimestamp(
        now.timestamp() + reading_time + random.randint(5, 15),
        tz=timezone.utc
    )

    # Generate screenshot path (simulated)
    screenshot_path = f"/tmp/leroy_screenshots/{profile_id}_{job_id}_{application_id}.png"

    # User agent (simulated)
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]

    result = {
        "status": "SUCCESS",
        "profile_id": profile_id,
        "job_id": job_id,
        "application_id": application_id,
        "company_name": inputs.get("company_name", ""),
        "job_title": inputs.get("job_title", ""),
        "z_approval_id": z_approval_id,
        "submission_timestamp": submission_time.isoformat(),
        "screenshot_path": screenshot_path,
        "preflight_checks": {
            "health_state": "GREEN",
            "daily_limit_ok": True,
            "last_app_gap_ok": True,
            "proxy_valid": True,
            "z_approved": True
        },
        "workflow": {
            "stage_1_navigation": {
                "status": "completed",
                "action": "navigate_to_job_posting",
                "duration_seconds": 3
            },
            "stage_2_reading": {
                "status": "completed",
                "action": "read_job_description",
                "duration_seconds": reading_time,
                "notes": "Simulating human reading time"
            },
            "stage_3_form_parsing": {
                "status": "completed",
                "action": "identify_form_fields",
                "fields_found": len(form_fields_simulated)
            },
            "stage_4_form_fill": {
                "status": "completed",
                "action": "fill_application_form",
                "fields_filled": form_fields_simulated,
                "duration_seconds": random.randint(10, 30)
            },
            "stage_5_submission": {
                "status": "completed",
                "action": "submit_application",
                "duration_seconds": random.randint(2, 5)
            },
            "stage_6_confirmation": {
                "status": "completed",
                "action": "capture_confirmation",
                "screenshot_captured": True,
                "screenshot_path": screenshot_path
            }
        },
        "details": {
            "form_fields_filled": len(form_fields_simulated),
            "reading_time_seconds": reading_time,
            "submission_time": submission_time.isoformat(),
            "user_agent": random.choice(user_agents),
            "proxy_ip": proxy_ip,
            "session_id": inputs.get("session_id", ""),
            "browser": "Ads Power Browser (simulated)"
        },
        "audit_trail": {
            "initiated_at": now.isoformat(),
            "completed_at": submission_time.isoformat(),
            "total_duration_seconds": int((submission_time - now).total_seconds()),
            "z_approval_id": z_approval_id,
            "profile_id": profile_id,
            "job_id": job_id
        },
        "timestamp": now.isoformat()
    }

    return result


def handle_error(error_type: str, context: dict) -> dict:
    """
    Handle application errors with appropriate escalation.

    Args:
        error_type: Type of error (unexpected_field, external_ats, profile_warning, rate_limit, network_error)
        context: Error context dict

    Returns:
        Error result with handling recommendation.
    """
    now = datetime.now(timezone.utc)

    error_handlers = {
        "unexpected_field": {
            "severity": "MEDIUM",
            "action": "flag_and_escalate",
            "message": "Unexpected form field encountered - manual review needed"
        },
        "external_ats": {
            "severity": "LOW",
            "action": "log_and_continue",
            "message": "Application redirected to external ATS - proceeding with submission"
        },
        "profile_warning": {
            "severity": "CRITICAL",
            "action": "stop_and_quarantine",
            "message": "LinkedIn warning banner detected - quarantine profile immediately"
        },
        "rate_limit": {
            "severity": "HIGH",
            "action": "backoff_and_retry",
            "message": "Rate limited - will retry after backoff or defer to next day"
        },
        "network_error": {
            "severity": "MEDIUM",
            "action": "retry_3_times",
            "message": "Network error - attempting retry (up to 3 times)"
        }
    }

    handler = error_handlers.get(error_type, {
        "severity": "MEDIUM",
        "action": "escalate",
        "message": f"Unknown error type: {error_type}"
    })

    result = {
        "status": "ERROR",
        "error_type": error_type,
        "severity": handler["severity"],
        "action": handler["action"],
        "message": handler["message"],
        "profile_id": context.get("profile_id"),
        "job_id": context.get("job_id"),
        "escalate_to": "EM" if handler["severity"] in ["CRITICAL", "HIGH"] else "log",
        "timestamp": now.isoformat()
    }

    return result


def get_error_recovery_action(error_result: dict) -> str:
    """
    Determine recovery action based on error result.

    Args:
        error_result: Result from handle_error

    Returns:
        Recovery action string.
    """
    action_map = {
        "flag_and_escalate": "ESCALATE_TO_EM",
        "stop_and_quarantine": "QUARANTINE_PROFILE_ALERT_Z",
        "log_and_continue": "LOG_AND_CONTINUE",
        "backoff_and_retry": "RETRY_LATER",
        "retry_3_times": "RETRY_NOW",
        "escalate": "ESCALATE_TO_EM"
    }

    return action_map.get(error_result.get("action"), "ESCALATE_TO_EM")


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    print("=== PREFLIGHT CHECK: PASS ===\n")
    preflight_ok = preflight_check({
        "profile_id": "P-001",
        "health_state": "GREEN",
        "tier": "A",
        "daily_app_count": 1,
        "last_app_minutes_ago": 12,
        "proxy_ip": "192.0.2.15",
        "z_approval_id": "SUBMIT-5678"
    })
    print(json.dumps(preflight_ok, indent=2))

    print("\n\n=== APPLICATION EXECUTION: SUCCESS ===\n")
    app_result = execute_application({
        "profile_id": "P-001",
        "job_id": "JOB-98765",
        "job_title": "Senior Python Developer",
        "company_name": "TechCorp",
        "application_package": {
            "resume_version": "v3-techcorp",
            "cover_letter": "custom"
        },
        "z_approval_id": "SUBMIT-5678",
        "proxy_ip": "192.0.2.15",
        "session_id": "SES-2026-02-15-001"
    })
    print(json.dumps(app_result, indent=2))

    print("\n\n=== ERROR HANDLING: PROFILE WARNING ===\n")
    error_result = handle_error("profile_warning", {
        "profile_id": "P-001",
        "job_id": "JOB-98765"
    })
    print(json.dumps(error_result, indent=2))
    print(f"\nRecovery action: {get_error_recovery_action(error_result)}")

    print("\n\n=== PREFLIGHT CHECK: BLOCKED ===\n")
    preflight_blocked = preflight_check({
        "profile_id": "P-002",
        "health_state": "RED",
        "tier": "B",
        "daily_app_count": 0,
        "last_app_minutes_ago": 30,
        "proxy_ip": "192.0.2.16",
        "z_approval_id": None
    })
    print(json.dumps(preflight_blocked, indent=2))
