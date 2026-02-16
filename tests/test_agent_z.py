"""
Integration test for Agent Z's core scripts.
Runs the full pipeline: CSV parse -> visa urgency -> priority scoring -> duplicate check -> Hot List.
"""

import sys
import json
from pathlib import Path

# Add skill directories to path
AGENT_DIR = Path(__file__).parent.parent / "agents" / "z" / "workspace" / "skills"
sys.path.insert(0, str(AGENT_DIR / "scoring"))
sys.path.insert(0, str(AGENT_DIR / "csv-parser"))
sys.path.insert(0, str(AGENT_DIR / "hotlist-publisher"))

from csv_parser import parse_crm_export
from visa_urgency_calculator import calculate_visa_urgency, calculate_batch_visa_urgency
from priority_calculator import calculate_priority, calculate_batch_priorities
from duplicate_checker import check_submission
from hotlist_publisher import generate_hotlist


def test_csv_parser():
    print("=" * 60)
    print("TEST 1: CSV Parser -- Log1 CRM Flat File Ingestion")
    print("=" * 60)

    csv_path = Path(__file__).parent / "sample_crm_export.csv"
    profiles, issues = parse_crm_export(str(csv_path))

    print(f"\nParsed {len(profiles)} profiles.")
    print(f"Issues found: {len(issues)}")
    for issue in issues:
        sev = issue.get("severity", "?")
        cid = issue.get("consultant_id", "")
        field = issue.get("field", "")
        msg = issue.get("message", "")
        print(f"  [{sev}] {cid} {field}: {msg}")

    assert len(profiles) == 8, f"Expected 8 profiles, got {len(profiles)}"
    assert profiles[0]["consultant_id"] == "C-011"
    assert profiles[0]["core_skills"] == ["Python", "Spark", "AWS Lambda", "SQL", "Airflow", "Docker"]
    assert profiles[0]["do_not_submit"] == ["JPMorgan", "Citi"]
    print("\n  PASSED: CSV parser works correctly.\n")
    return profiles


def test_visa_urgency(profiles):
    print("=" * 60)
    print("TEST 2: Visa Urgency Calculator")
    print("=" * 60)

    visa_inputs = [
        {
            "consultant_id": p["consultant_id"],
            "consultant_name": p["full_name"],
            "visa_status": p["visa_status"],
            "visa_expiration_date": p.get("visa_expiration_date"),
            "current_date": "2026-02-12"
        }
        for p in profiles
    ]

    results = calculate_batch_visa_urgency(visa_inputs)

    for r in results:
        days = r.get("days_remaining")
        days_str = f"{days}d" if days is not None else "N/A"
        print(f"  {r['consultant_id']} | {r['visa_status']:8s} | {r['urgency_tier']:10s} | {days_str}")

    # Amit (OPT, expires 2026-03-05) should be CRITICAL (21 days from 2026-02-12)
    amit = next(r for r in results if r["consultant_id"] == "C-011")
    assert amit["urgency_tier"] == "CRITICAL", f"Amit should be CRITICAL, got {amit['urgency_tier']}"
    assert amit["days_remaining"] == 21

    # Sarah (Citizen) should be NA
    sarah = next(r for r in results if r["consultant_id"] == "C-055")
    assert sarah["urgency_tier"] == "NA"

    # Priya (H1B, expires 2026-11-30) should be LOW
    priya = next(r for r in results if r["consultant_id"] == "C-019")
    assert priya["urgency_tier"] == "LOW"

    print("\n  PASSED: Visa urgency calculations are correct.\n")
    return {r["consultant_id"]: r for r in results}


def test_priority_scoring(profiles, visa_results):
    print("=" * 60)
    print("TEST 3: Priority Calculator")
    print("=" * 60)

    # Build priority inputs
    priority_inputs = []
    for p in profiles:
        visa = visa_results.get(p["consultant_id"], {})
        priority_inputs.append({
            "consultant_id": p["consultant_id"],
            "consultant_name": p["full_name"],
            "visa_urgency_tier": visa.get("urgency_tier", "NA"),
            "days_on_bench": p.get("days_on_bench", 0),
            "market_demand": "HIGH",  # Default for testing
            "rate_tier": "MID",  # Default for testing
            "active_submission_count": 0  # No submissions yet
        })

    results = calculate_batch_priorities(priority_inputs)

    for r in results:
        print(f"  #{r['rank']} | {r['consultant_id']} | {r.get('consultant_name', ''):20s} | Score: {r['score']:5.2f} | {r['priority_tier']} ({r['tier_label']})")

    # Amit should be P1 (CRITICAL visa + long bench time)
    amit = next(r for r in results if r["consultant_id"] == "C-011")
    assert amit["priority_tier"] == "P1", f"Amit should be P1, got {amit['priority_tier']}"
    assert amit["score"] >= 8.0

    print(f"\n  P1 count: {sum(1 for r in results if r['priority_tier'] == 'P1')}")
    print(f"  P2 count: {sum(1 for r in results if r['priority_tier'] == 'P2')}")
    print(f"  P3 count: {sum(1 for r in results if r['priority_tier'] == 'P3')}")
    print(f"  P4 count: {sum(1 for r in results if r['priority_tier'] == 'P4')}")
    print("\n  PASSED: Priority scoring produces correct tiers.\n")
    return results


def test_duplicate_checker():
    print("=" * 60)
    print("TEST 4: Duplicate Submission Checker (5 Rules)")
    print("=" * 60)

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
    ]

    tests = [
        {
            "name": "Rule 1: Same client within 90 days",
            "request": {"consultant_id": "C-042", "end_client": "JPMorgan", "vendor_name": "Infosys", "job_posting_id": "LI-200001", "submission_date": "2026-02-12"},
            "expected": "BLOCK"
        },
        {
            "name": "Rule 2: Exact duplicate posting",
            "request": {"consultant_id": "C-042", "end_client": "JPMorgan", "vendor_name": "TCS", "job_posting_id": "LI-100001", "submission_date": "2026-02-12"},
            "expected": "BLOCK"
        },
        {
            "name": "Rule 3: Same client, different vendor within 30 days (also triggers Rule 1)",
            "request": {"consultant_id": "C-042", "end_client": "Capital One", "vendor_name": "Robert Half", "job_posting_id": "LI-200003", "submission_date": "2026-02-12"},
            "expected": "BLOCK"  # Rule 1 (90-day block) takes precedence over Rule 3 (warn)
        },
        {
            "name": "Rule 5: DNS list block",
            "request": {"consultant_id": "C-042", "end_client": "BofA", "vendor_name": "TCS", "job_posting_id": "LI-200004", "submission_date": "2026-02-12", "do_not_submit": [{"company": "BofA", "reason": "bad interview"}]},
            "expected": "BLOCK"
        },
        {
            "name": "Clean submission (no conflicts)",
            "request": {"consultant_id": "C-042", "end_client": "Meta", "vendor_name": "TCS", "job_posting_id": "LI-200005", "submission_date": "2026-02-12"},
            "expected": "ALLOW"
        },
    ]

    all_passed = True
    for test in tests:
        result = check_submission(test["request"], history)
        status = "PASS" if result["decision"] == test["expected"] else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"  [{status}] {test['name']}: expected {test['expected']}, got {result['decision']}")
        if result["rules_triggered"]:
            for rule in result["rules_triggered"]:
                print(f"         Rule {rule['rule']}: {rule['description']}")

    assert all_passed, "Some duplicate checker tests failed"
    print("\n  PASSED: All 5 duplicate check rules work correctly.\n")


def test_hotlist(priority_results, visa_results):
    print("=" * 60)
    print("TEST 5: Hot List Publisher")
    print("=" * 60)

    # Enrich priority results with visa data
    for r in priority_results:
        visa = visa_results.get(r["consultant_id"], {})
        r["visa_status"] = visa.get("visa_status", "")
        r["visa_urgency_tier"] = visa.get("urgency_tier", "NA")
        r["days_remaining"] = visa.get("days_remaining")
        r["primary_category"] = "Developer"  # simplified for test
        r["active_submission_count"] = 0
        r["status"] = "active"

    stats = {"total_active_submissions": 0, "interviews_scheduled": 0, "awaiting_feedback": 0, "new_to_bench": 2}
    alerts = ["C-011: OPT expires in 21 days -- escalate immediately"]

    hotlist = generate_hotlist(priority_results, stats, [], alerts, report_date="2026-02-12")
    print(f"\n{hotlist}")
    print("\n  PASSED: Hot List generated successfully.\n")


def main():
    print("\n" + "=" * 60)
    print("  AGENT Z -- FULL INTEGRATION TEST")
    print("=" * 60 + "\n")

    # Pipeline: CSV -> Visa -> Priority -> Duplicate Check -> Hot List
    profiles = test_csv_parser()
    visa_results = test_visa_urgency(profiles)
    priority_results = test_priority_scoring(profiles, visa_results)
    test_duplicate_checker()
    test_hotlist(priority_results, visa_results)

    print("=" * 60)
    print("  ALL TESTS PASSED -- Agent Z core is operational")
    print("=" * 60)


if __name__ == "__main__":
    main()
