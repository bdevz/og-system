"""
Duplicate Submission Checker for Agent Z
==========================================
Rule-based submission conflict detection. Five hard rules, deterministic,
every check logged with reason.

Usage:
    from duplicate_checker import check_submission

    result = check_submission({
        "consultant_id": "C-042",
        "end_client": "JPMorgan",
        "vendor_name": "TCS",
        "job_posting_id": "LI-389201",
        "submission_date": "2026-02-12"
    }, submission_history)
"""

import json
from datetime import datetime, timezone, date, timedelta
from pathlib import Path


LOG_FILE = Path(__file__).parent / "scoring_log.jsonl"


def check_submission(request: dict, submission_history: list, dns_list: list = None) -> dict:
    """
    Check a submission request against history for conflicts.

    Five hard rules (from architecture spec):
    1. Same consultant + same end client + last 90 days = BLOCK
    2. Same consultant + same job posting ID = BLOCK
    3. Same consultant + same client + different vendor within 30 days = WARN
    4. Different consultant + same role + same vendor = ALLOW (but LOG)
    5. Consultant on do-not-submit for this client = BLOCK

    Args:
        request: Dict with:
            - consultant_id (str)
            - end_client (str)
            - end_client_confidence (str, optional): HIGH/MEDIUM/LOW/UNKNOWN
            - vendor_name (str)
            - job_posting_id (str)
            - submission_date (str): ISO date
            - do_not_submit (list, optional): DNS entries for this consultant
        submission_history: List of past submission records, each with:
            - consultant_id, end_client, vendor_name, job_posting_id, submission_date, status
        dns_list: Optional master DNS list (list of dicts with consultant_id, company, vendor, reason)

    Returns:
        Dict with decision (ALLOW/BLOCK/WARN), rules_triggered, conflicts, explanation.
    """
    consultant_id = request["consultant_id"]
    end_client = request.get("end_client", "").upper().strip()
    vendor_name = request.get("vendor_name", "").upper().strip()
    job_posting_id = request.get("job_posting_id", "")
    submission_date = date.fromisoformat(request["submission_date"])
    consultant_dns = request.get("do_not_submit", [])

    rules_triggered = []
    conflicts = []
    decision = "ALLOW"

    # --- Rule 5: Do-not-submit list check (check first, it's fastest) ---
    # Check consultant-level DNS
    for dns_entry in consultant_dns:
        dns_company = dns_entry if isinstance(dns_entry, str) else dns_entry.get("company", "")
        dns_vendor = dns_entry.get("vendor", "") if isinstance(dns_entry, dict) else ""

        if dns_company.upper().strip() == end_client:
            # Check if it's vendor-specific or company-wide
            if dns_vendor and dns_vendor.upper().strip() != vendor_name:
                continue  # DNS is for a different vendor, this one is OK
            rules_triggered.append({
                "rule": 5,
                "description": "Consultant on do-not-submit for this client",
                "severity": "BLOCK",
                "detail": f"DNS entry: {dns_company}" + (f" (vendor: {dns_vendor})" if dns_vendor else " (company-wide)")
            })
            decision = "BLOCK"

    # Also check master DNS list if provided
    if dns_list:
        for entry in dns_list:
            if entry.get("consultant_id") == consultant_id:
                entry_company = entry.get("company", "").upper().strip()
                entry_vendor = entry.get("vendor", "").upper().strip()
                if entry_company == end_client:
                    if entry_vendor and entry_vendor != vendor_name:
                        continue
                    rules_triggered.append({
                        "rule": 5,
                        "description": "Consultant on master do-not-submit list",
                        "severity": "BLOCK",
                        "detail": f"Master DNS: {entry_company}, reason: {entry.get('reason', 'N/A')}"
                    })
                    decision = "BLOCK"

    # --- Rule 2: Same consultant + same job posting ID = BLOCK ---
    for record in submission_history:
        if (record.get("consultant_id") == consultant_id
                and record.get("job_posting_id") == job_posting_id):
            rules_triggered.append({
                "rule": 2,
                "description": "Same consultant + same job posting ID (exact duplicate)",
                "severity": "BLOCK",
                "conflicting_record": record,
                "detail": f"Already submitted on {record.get('submission_date')}"
            })
            conflicts.append(record)
            decision = "BLOCK"

    # --- Rule 1: Same consultant + same end client + last 90 days = BLOCK ---
    ninety_days_ago = submission_date - timedelta(days=90)
    for record in submission_history:
        if record.get("consultant_id") != consultant_id:
            continue
        record_client = record.get("end_client", "").upper().strip()
        if record_client != end_client:
            continue
        if record_client == "" or end_client == "":
            continue  # Can't compare if client is unknown
        record_date = date.fromisoformat(record["submission_date"]) if record.get("submission_date") else None
        if record_date and record_date >= ninety_days_ago:
            # Avoid double-counting rule 2
            if record.get("job_posting_id") != job_posting_id:
                rules_triggered.append({
                    "rule": 1,
                    "description": "Same consultant + same end client within 90 days (right-to-represent risk)",
                    "severity": "BLOCK",
                    "conflicting_record": record,
                    "detail": f"Submitted to {record_client} on {record.get('submission_date')} via {record.get('vendor_name')} ({(submission_date - record_date).days} days ago)"
                })
                conflicts.append(record)
                decision = "BLOCK"

    # --- Rule 3: Same consultant + same client + different vendor within 30 days = WARN ---
    thirty_days_ago = submission_date - timedelta(days=30)
    for record in submission_history:
        if record.get("consultant_id") != consultant_id:
            continue
        record_client = record.get("end_client", "").upper().strip()
        record_vendor = record.get("vendor_name", "").upper().strip()
        if record_client != end_client or record_client == "":
            continue
        if record_vendor == vendor_name:
            continue  # Same vendor, rule 1 covers this
        record_date = date.fromisoformat(record["submission_date"]) if record.get("submission_date") else None
        if record_date and record_date >= thirty_days_ago:
            rules_triggered.append({
                "rule": 3,
                "description": "Same consultant + same client + different vendor within 30 days (vendor dispute risk)",
                "severity": "WARN",
                "conflicting_record": record,
                "detail": f"Submitted to {record_client} via {record_vendor} on {record.get('submission_date')} ({(submission_date - record_date).days} days ago). Current request via {vendor_name}."
            })
            conflicts.append(record)
            if decision == "ALLOW":
                decision = "WARN"

    # --- Rule 4: Different consultant + same role + same vendor = ALLOW but LOG ---
    for record in submission_history:
        if record.get("consultant_id") == consultant_id:
            continue  # Same consultant, other rules handle this
        if (record.get("job_posting_id") == job_posting_id
                and record.get("vendor_name", "").upper().strip() == vendor_name):
            rules_triggered.append({
                "rule": 4,
                "description": "Different consultant submitted to same role via same vendor (allowed, logged)",
                "severity": "LOG",
                "conflicting_record": record,
                "detail": f"Consultant {record.get('consultant_id')} already submitted to this role via {vendor_name}"
            })
            # This doesn't change the decision -- it's informational

    # Build explanation
    if decision == "BLOCK":
        block_rules = [r for r in rules_triggered if r["severity"] == "BLOCK"]
        explanation = f"BLOCKED: {len(block_rules)} rule(s) violated. " + " | ".join(r["detail"] for r in block_rules)
    elif decision == "WARN":
        warn_rules = [r for r in rules_triggered if r["severity"] == "WARN"]
        explanation = f"WARNING: {len(warn_rules)} advisory rule(s). " + " | ".join(r["detail"] for r in warn_rules)
    else:
        explanation = "No conflicts detected. Submission cleared."

    result = {
        "decision": decision,
        "consultant_id": consultant_id,
        "end_client": end_client,
        "vendor_name": vendor_name,
        "job_posting_id": job_posting_id,
        "rules_triggered": rules_triggered,
        "conflicts": conflicts,
        "explanation": explanation,
        "rules_checked": 5,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    _log_check(result)
    return result


def _log_check(result: dict):
    """Append check to scoring log."""
    log_entry = {
        "event_type": "duplicate_check",
        "timestamp": result["timestamp"],
        "consultant_id": result["consultant_id"],
        "decision": result["decision"],
        "rules_triggered_count": len(result["rules_triggered"]),
        "end_client": result["end_client"],
        "vendor_name": result["vendor_name"],
        "job_posting_id": result["job_posting_id"]
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


if __name__ == "__main__":
    # Demo: test all 5 rules
    history = [
        {
            "consultant_id": "C-042",
            "end_client": "JPMORGAN",
            "vendor_name": "TCS",
            "job_posting_id": "LI-100001",
            "submission_date": "2026-01-20",
            "status": "Submitted"
        },
        {
            "consultant_id": "C-042",
            "end_client": "CAPITAL ONE",
            "vendor_name": "INSIGHT GLOBAL",
            "job_posting_id": "LI-100002",
            "submission_date": "2026-02-01",
            "status": "Submitted"
        },
        {
            "consultant_id": "C-055",
            "end_client": "GOOGLE",
            "vendor_name": "ROBERT HALF",
            "job_posting_id": "LI-100003",
            "submission_date": "2026-02-10",
            "status": "Submitted"
        },
    ]

    # Test: should BLOCK (rule 1: same client within 90 days)
    test1 = check_submission({
        "consultant_id": "C-042",
        "end_client": "JPMorgan",
        "vendor_name": "Infosys",
        "job_posting_id": "LI-200001",
        "submission_date": "2026-02-12"
    }, history)
    print(f"Test 1 (Rule 1 - same client 90d): {test1['decision']}")
    print(f"  {test1['explanation']}\n")

    # Test: should ALLOW
    test2 = check_submission({
        "consultant_id": "C-042",
        "end_client": "Meta",
        "vendor_name": "TCS",
        "job_posting_id": "LI-200002",
        "submission_date": "2026-02-12"
    }, history)
    print(f"Test 2 (clean): {test2['decision']}")
    print(f"  {test2['explanation']}\n")

    # Test: should BLOCK (rule 5: DNS list)
    test3 = check_submission({
        "consultant_id": "C-042",
        "end_client": "BofA",
        "vendor_name": "TCS",
        "job_posting_id": "LI-200003",
        "submission_date": "2026-02-12",
        "do_not_submit": [{"company": "BofA", "reason": "bad interview"}]
    }, history)
    print(f"Test 3 (Rule 5 - DNS): {test3['decision']}")
    print(f"  {test3['explanation']}\n")

    # Test: should BLOCK (rule 2: exact duplicate posting)
    test4 = check_submission({
        "consultant_id": "C-042",
        "end_client": "JPMorgan",
        "vendor_name": "TCS",
        "job_posting_id": "LI-100001",
        "submission_date": "2026-02-12"
    }, history)
    print(f"Test 4 (Rule 2 - exact dup): {test4['decision']}")
    print(f"  {test4['explanation']}\n")
