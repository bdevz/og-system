"""
Hot List Publisher for Agent Z
================================
Generates the daily Hot List in standard format for Slack publishing.
All sorting and grouping is programmatic. No AI estimation.

Usage:
    from hotlist_publisher import generate_hotlist

    hotlist = generate_hotlist(profiles, submission_stats, alerts)
"""

import json
from datetime import datetime, timezone, date
from typing import Optional


def generate_hotlist(
    prioritized_profiles: list,
    submission_stats: dict = None,
    stale_submissions: list = None,
    alerts: list = None,
    report_date: Optional[str] = None,
) -> str:
    """
    Generate the daily Hot List in standard format.

    Args:
        prioritized_profiles: List of profiles with priority scores (pre-sorted by score desc).
            Each must have: consultant_id, full_name/consultant_name, primary_category,
            visa_status, days_on_bench, active_submission_count, priority_tier, score,
            and optionally visa_urgency_tier, days_remaining (visa).
        submission_stats: Dict with total_active_submissions, interviews_scheduled,
            awaiting_feedback, new_to_bench (counts).
        stale_submissions: List of submissions with no update in 7+ days.
            Each has: consultant_name, job_title, end_client, vendor_name,
            submission_date, days_since_update.
        alerts: List of alert strings.
        report_date: Override date string (YYYY-MM-DD). Defaults to today.

    Returns:
        Formatted Hot List string ready for Slack.
    """
    if not report_date:
        report_date = date.today().isoformat()

    stats = submission_stats or {}
    stale = stale_submissions or []
    alert_list = alerts or []

    active_count = len(prioritized_profiles)
    total_subs = stats.get("total_active_submissions", 0)
    interviews = stats.get("interviews_scheduled", 0)
    awaiting = stats.get("awaiting_feedback", 0)
    new_bench = stats.get("new_to_bench", 0)

    lines = []
    lines.append(f"DAILY HOT LIST -- {report_date}")
    lines.append("=" * 40)
    lines.append("")
    lines.append(f"ACTIVE BENCH: {active_count} consultants")
    lines.append(f"ACTIVE SUBMISSIONS: {total_subs}")
    lines.append(f"INTERVIEWS SCHEDULED: {interviews}")
    lines.append(f"AWAITING FEEDBACK: {awaiting}")
    lines.append(f"NEW TO BENCH (< 7 days): {new_bench}")
    lines.append("")

    # Group by priority tier
    tiers = {"P1": [], "P2": [], "P3": [], "P4": []}
    placed_hold = []

    for p in prioritized_profiles:
        tier = p.get("priority_tier", "P4")
        status = p.get("status", "active")
        if status in ("placed", "on_hold", "hold"):
            placed_hold.append(p)
        elif tier in tiers:
            tiers[tier].append(p)
        else:
            tiers["P4"].append(p)

    lines.append("PRIORITY QUEUE FOR TODAY:")
    lines.append("-" * 40)

    rank = 1

    if tiers["P1"]:
        lines.append("P1 -- URGENT")
        for p in tiers["P1"]:
            name = p.get("consultant_name") or p.get("full_name", "Unknown")
            category = p.get("primary_category", "")
            visa = p.get("visa_status", "")
            bench_days = p.get("days_on_bench", "?")
            subs = p.get("active_submission_count", 0)
            score = p.get("score", 0)
            visa_info = ""
            if p.get("visa_urgency_tier") in ("CRITICAL", "HIGH"):
                days_rem = p.get("days_remaining")
                if days_rem is not None:
                    visa_info = f" | {visa} expires in {days_rem} days"
                else:
                    visa_info = f" | {visa} (urgency: {p.get('visa_urgency_tier', '?')})"
            else:
                visa_info = f" | {visa}"
            lines.append(f"  {rank}. [{score:.1f}] {name} | {category}{visa_info} | Bench: {bench_days}d | {subs} active subs")
            rank += 1
        lines.append("")

    if tiers["P2"]:
        lines.append("P2 -- ACTIVE")
        for p in tiers["P2"]:
            name = p.get("consultant_name") or p.get("full_name", "Unknown")
            category = p.get("primary_category", "")
            visa = p.get("visa_status", "")
            bench_days = p.get("days_on_bench", "?")
            subs = p.get("active_submission_count", 0)
            score = p.get("score", 0)
            lines.append(f"  {rank}. [{score:.1f}] {name} | {category} | {visa} | Bench: {bench_days}d | {subs} active subs")
            rank += 1
        lines.append("")

    if tiers["P3"]:
        lines.append("P3 -- MAINTENANCE")
        for p in tiers["P3"]:
            name = p.get("consultant_name") or p.get("full_name", "Unknown")
            category = p.get("primary_category", "")
            score = p.get("score", 0)
            lines.append(f"  {rank}. [{score:.1f}] {name} | {category}")
            rank += 1
        lines.append("")

    if tiers["P4"]:
        lines.append("P4 -- LOW / ON HOLD")
        for p in tiers["P4"]:
            name = p.get("consultant_name") or p.get("full_name", "Unknown")
            category = p.get("primary_category", "")
            score = p.get("score", 0)
            lines.append(f"  {rank}. [{score:.1f}] {name} | {category}")
            rank += 1
        lines.append("")

    # Placed / Hold
    if placed_hold:
        lines.append("RECENTLY PLACED / HOLD:")
        for p in placed_hold:
            name = p.get("consultant_name") or p.get("full_name", "Unknown")
            status = p.get("status", "")
            reason = p.get("hold_reason", "")
            lines.append(f"  - {name} | {status.upper()}" + (f" -- {reason}" if reason else ""))
        lines.append("")

    # Stale submissions
    if stale:
        lines.append("SUBMISSIONS NEEDING FOLLOW-UP (no update in 7+ days):")
        for s in stale:
            name = s.get("consultant_name", "Unknown")
            title = s.get("job_title", "Unknown role")
            client = s.get("end_client", "Unknown client")
            vendor = s.get("vendor_name", "Unknown vendor")
            days = s.get("days_since_update", "?")
            lines.append(f"  - {name} -> {title} at {client} via {vendor} -- {days} days since update")
        lines.append("")

    # Alerts
    if alert_list:
        lines.append("ALERTS:")
        for a in alert_list:
            lines.append(f"  ! {a}")
        lines.append("")

    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

    return "\n".join(lines)


def post_hotlist_to_slack(
    prioritized_profiles: list,
    submission_stats: dict = None,
    stale_submissions: list = None,
    alerts: list = None,
    report_date: Optional[str] = None,
) -> bool:
    """
    Generate the Hot List and post to #og-daily-hotlist via Slack API.
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "shared"))

    hotlist = generate_hotlist(prioritized_profiles, submission_stats, stale_submissions, alerts, report_date)

    try:
        from slack_client import post_message
        post_message("og-daily-hotlist", hotlist, agent="Z")
        return True
    except Exception as e:
        print(f"Slack posting failed: {e}")
        return False


if __name__ == "__main__":
    # Demo with sample data
    sample_profiles = [
        {"consultant_id": "C-011", "consultant_name": "Amit Patel", "primary_category": "Python Developer", "visa_status": "OPT", "visa_urgency_tier": "CRITICAL", "days_remaining": 22, "days_on_bench": 45, "active_submission_count": 0, "priority_tier": "P1", "score": 9.15, "status": "active"},
        {"consultant_id": "C-023", "consultant_name": "Wei Chen", "primary_category": "DevOps Engineer", "visa_status": "H1B", "visa_urgency_tier": "HIGH", "days_remaining": 65, "days_on_bench": 30, "active_submission_count": 1, "priority_tier": "P1", "score": 8.2, "status": "active"},
        {"consultant_id": "C-042", "consultant_name": "Ravi Kumar", "primary_category": "Java Developer", "visa_status": "GC", "visa_urgency_tier": "NA", "days_remaining": None, "days_on_bench": 15, "active_submission_count": 2, "priority_tier": "P2", "score": 6.5, "status": "active"},
        {"consultant_id": "C-055", "consultant_name": "Sarah Johnson", "primary_category": "Cloud Architect", "visa_status": "Citizen", "visa_urgency_tier": "NA", "days_remaining": None, "days_on_bench": 8, "active_submission_count": 3, "priority_tier": "P2", "score": 5.8, "status": "active"},
        {"consultant_id": "C-019", "consultant_name": "Priya Sharma", "primary_category": "AI-ML Engineer", "visa_status": "GC", "visa_urgency_tier": "NA", "days_remaining": None, "days_on_bench": 2, "active_submission_count": 0, "priority_tier": "P3", "score": 4.1, "status": "active"},
    ]

    sample_stats = {"total_active_submissions": 42, "interviews_scheduled": 3, "awaiting_feedback": 8, "new_to_bench": 1}
    sample_stale = [{"consultant_name": "Ravi Kumar", "job_title": "Senior Java Dev", "end_client": "BofA", "vendor_name": "TCS", "days_since_update": 12}]
    sample_alerts = ["C-011: OPT expires in 22 days -- escalate immediately", "C-023: H1B transfer pending, 65 days remaining"]

    print(generate_hotlist(sample_profiles, sample_stats, sample_stale, sample_alerts))
