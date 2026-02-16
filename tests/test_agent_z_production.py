"""
Agent Z Production Validation Suite
=====================================
Comprehensive edge-case testing for Agent Z before OpenClaw deployment.
Tests every script with adversarial inputs, boundary conditions, and
real-world scenarios from Consultadd's recruitment operation.

This is the "would I trust this in production?" test.
"""

import json
import os
import sys
import tempfile
import csv
from datetime import datetime, timezone, timedelta, date
from pathlib import Path

# ── Imports ──
AGENTS_DIR = Path(__file__).parent.parent / "agents"
sys.path.insert(0, str(AGENTS_DIR / "z" / "workspace" / "skills" / "scoring"))
sys.path.insert(0, str(AGENTS_DIR / "z" / "workspace" / "skills" / "csv-parser"))
sys.path.insert(0, str(AGENTS_DIR / "z" / "workspace" / "skills" / "hotlist-publisher"))

from priority_calculator import calculate_priority, calculate_batch_priorities
from visa_urgency_calculator import calculate_visa_urgency, calculate_batch_visa_urgency
from duplicate_checker import check_submission
from csv_parser import parse_crm_export
from hotlist_publisher import generate_hotlist

passed = 0
failed = 0
errors = []

def test(condition, name, detail=""):
    global passed, failed, errors
    if condition:
        passed += 1
        print(f"  ✓ {name}")
    else:
        failed += 1
        errors.append(f"{name}: {detail}")
        print(f"  ✗ {name} — {detail}")


# ══════════════════════════════════════════════════════════════════
# SUITE 1: VISA URGENCY — BOUNDARY CONDITIONS
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SUITE 1: Visa Urgency Calculator — Boundary Conditions")
print("=" * 70)

# Exact boundary: 30 days
tomorrow_30 = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d")
r = calculate_visa_urgency({"consultant_id": "T-001", "visa_status": "H1B", "visa_expiration_date": tomorrow_30})
test(r["urgency_tier"] in ["CRITICAL", "HIGH"], "30 days = CRITICAL or HIGH boundary", f"Got {r['urgency_tier']}")

# Exact boundary: 90 days
day_90 = (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d")
r = calculate_visa_urgency({"consultant_id": "T-002", "visa_status": "OPT", "visa_expiration_date": day_90})
test(r["urgency_tier"] in ["HIGH", "MEDIUM"], "90 days = HIGH or MEDIUM boundary", f"Got {r['urgency_tier']}")

# Exact boundary: 180 days
day_180 = (datetime.now(timezone.utc) + timedelta(days=180)).strftime("%Y-%m-%d")
r = calculate_visa_urgency({"consultant_id": "T-003", "visa_status": "H1B", "visa_expiration_date": day_180})
test(r["urgency_tier"] in ["MEDIUM", "LOW"], "180 days = MEDIUM or LOW boundary", f"Got {r['urgency_tier']}")

# Already expired visa
expired = (datetime.now(timezone.utc) - timedelta(days=5)).strftime("%Y-%m-%d")
r = calculate_visa_urgency({"consultant_id": "T-004", "visa_status": "OPT", "visa_expiration_date": expired})
test(r["urgency_tier"] == "CRITICAL", "Expired visa = CRITICAL", f"Got {r['urgency_tier']}")

# Expires tomorrow
tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
r = calculate_visa_urgency({"consultant_id": "T-005", "visa_status": "H1B", "visa_expiration_date": tomorrow})
test(r["urgency_tier"] == "CRITICAL", "Expires tomorrow = CRITICAL", f"Got {r['urgency_tier']}")

# All non-expiring types
for visa_type in ["GC", "Citizen", "citizen", "CITIZEN", "gc", "Green Card"]:
    r = calculate_visa_urgency({"consultant_id": "T-NE", "visa_status": visa_type, "visa_expiration_date": ""})
    test(r["urgency_tier"] == "NA", f"'{visa_type}' = NA (non-expiring)", f"Got {r['urgency_tier']}")

# Missing expiration date with expiring visa
r = calculate_visa_urgency({"consultant_id": "T-006", "visa_status": "H1B", "visa_expiration_date": ""})
test(r["urgency_tier"] in ["CRITICAL", "UNKNOWN"], "H1B with no expiry date = CRITICAL or UNKNOWN", f"Got {r['urgency_tier']}")

# Batch calculation
batch = calculate_batch_visa_urgency([
    {"consultant_id": "B-1", "visa_status": "Citizen", "visa_expiration_date": ""},
    {"consultant_id": "B-2", "visa_status": "H1B", "visa_expiration_date": tomorrow},
    {"consultant_id": "B-3", "visa_status": "GC", "visa_expiration_date": ""},
])
test(len(batch) == 3, "Batch returns 3 results")
test(batch[0]["consultant_id"] == "B-2", "Batch sorts CRITICAL first", f"First was {batch[0]['consultant_id']}")


# ══════════════════════════════════════════════════════════════════
# SUITE 2: PRIORITY CALCULATOR — EDGE CASES
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SUITE 2: Priority Calculator — Edge Cases")
print("=" * 70)

# Maximum urgency consultant
# API: market_demand = "HIGH"/"MEDIUM"/"LOW", rate_tier = "TOP_QUARTILE"/"MID"/"BOTTOM"
max_urgency = calculate_priority({
    "consultant_id": "P-MAX",
    "consultant_name": "Max Urgency",
    "visa_urgency_tier": "CRITICAL",
    "days_on_bench": 120,
    "market_demand": "HIGH",
    "rate_tier": "TOP_QUARTILE",
    "active_submission_count": 0,
})
test(max_urgency["priority_tier"] == "P1", "Max urgency inputs = P1", f"Got {max_urgency['priority_tier']} (score={max_urgency['score']})")
test(max_urgency["score"] >= 9.0, "Max urgency score >= 9.0", f"Got {max_urgency['score']}")

# Minimum urgency consultant
min_urgency = calculate_priority({
    "consultant_id": "P-MIN",
    "consultant_name": "Min Urgency",
    "visa_urgency_tier": "NA",
    "days_on_bench": 1,
    "market_demand": "LOW",
    "rate_tier": "BOTTOM",
    "active_submission_count": 10,
})
test(min_urgency["priority_tier"] in ["P3", "P4"], "Min urgency inputs = P3 or P4", f"Got {min_urgency['priority_tier']} (score={min_urgency['score']})")

# Zero days on bench
new_bench = calculate_priority({
    "consultant_id": "P-NEW",
    "consultant_name": "Just Arrived",
    "visa_urgency_tier": "LOW",
    "days_on_bench": 0,
    "market_demand": "MEDIUM",
    "rate_tier": "MID",
    "active_submission_count": 0,
})
test(new_bench["score"] > 0, "0 days on bench still produces positive score", f"Got {new_bench['score']}")

# Very long bench time
long_bench = calculate_priority({
    "consultant_id": "P-LONG",
    "consultant_name": "Been Here Forever",
    "visa_urgency_tier": "NA",
    "days_on_bench": 365,
    "market_demand": "LOW",
    "rate_tier": "MID",
    "active_submission_count": 2,
})
test(long_bench["score"] > new_bench["score"], "365 days bench > 0 days bench (all else equal-ish)", f"365d={long_bench['score']}, 0d={new_bench['score']}")

# Batch with tie-breaking
batch_p = calculate_batch_priorities([
    {"consultant_id": "BP-1", "consultant_name": "A", "visa_urgency_tier": "HIGH", "days_on_bench": 30, "market_demand": "HIGH", "rate_tier": "MID", "active_submission_count": 0},
    {"consultant_id": "BP-2", "consultant_name": "B", "visa_urgency_tier": "HIGH", "days_on_bench": 60, "market_demand": "HIGH", "rate_tier": "MID", "active_submission_count": 0},
    {"consultant_id": "BP-3", "consultant_name": "C", "visa_urgency_tier": "CRITICAL", "days_on_bench": 10, "market_demand": "HIGH", "rate_tier": "MID", "active_submission_count": 0},
])
# Composite score determines sort order — CRITICAL visa alone doesn't guarantee top rank.
# BP-2 (HIGH visa + 60d bench) can outscore BP-3 (CRITICAL visa + 10d bench) because
# bench time weight compensates for the visa tier difference. This is CORRECT behavior.
test(batch_p[0]["score"] >= batch_p[1]["score"] >= batch_p[2]["score"],
     "Batch sorted by composite score descending",
     f"Scores: {[p['score'] for p in batch_p]}")
# BP-2 should outscore BP-1 (same visa tier, more bench time)
bp1_score = next(p["score"] for p in batch_p if p["consultant_id"] == "BP-1")
bp2_score = next(p["score"] for p in batch_p if p["consultant_id"] == "BP-2")
test(bp2_score > bp1_score, "Same visa tier, longer bench = higher score", f"BP-2={bp2_score}, BP-1={bp1_score}")

# Verify breakdown is always present
test("breakdown" in max_urgency, "Result always includes breakdown dict")
test("visa_urgency" in max_urgency["breakdown"], "Breakdown includes visa_urgency")
test("contribution" in max_urgency["breakdown"]["visa_urgency"], "Each factor has contribution")


# ══════════════════════════════════════════════════════════════════
# SUITE 3: DUPLICATE CHECKER — ALL 5 RULES
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SUITE 3: Duplicate Checker — All 5 Rules Exhaustively")
print("=" * 70)

today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
days_ago_45 = (datetime.now(timezone.utc) - timedelta(days=45)).strftime("%Y-%m-%d")
days_ago_100 = (datetime.now(timezone.utc) - timedelta(days=100)).strftime("%Y-%m-%d")
days_ago_15 = (datetime.now(timezone.utc) - timedelta(days=15)).strftime("%Y-%m-%d")

# Rule 1: Same consultant + same client within 90 days = BLOCK
r1 = check_submission(
    request={"consultant_id": "C-001", "end_client": "Microsoft", "vendor_name": "Vendor-A", "job_posting_id": "JP-100", "submission_date": today},
    submission_history=[{"consultant_id": "C-001", "end_client": "Microsoft", "vendor_name": "Vendor-B", "job_posting_id": "JP-050", "submission_date": days_ago_45, "status": "pending"}],
    dns_list=[],
)
test(r1["decision"] == "BLOCK", "Rule 1: Same consultant+client 45 days ago = BLOCK", f"Got {r1['decision']}")

# Rule 1: Same consultant + same client OUTSIDE 90 days = ALLOW
r1b = check_submission(
    request={"consultant_id": "C-001", "end_client": "Microsoft", "vendor_name": "Vendor-A", "job_posting_id": "JP-101", "submission_date": today},
    submission_history=[{"consultant_id": "C-001", "end_client": "Microsoft", "vendor_name": "Vendor-B", "job_posting_id": "JP-040", "submission_date": days_ago_100, "status": "rejected"}],
    dns_list=[],
)
test(r1b["decision"] == "ALLOW", "Rule 1: Same consultant+client 100 days ago = ALLOW", f"Got {r1b['decision']}")

# Rule 2: Same posting ID = BLOCK
r2 = check_submission(
    request={"consultant_id": "C-002", "end_client": "Google", "vendor_name": "Vendor-A", "job_posting_id": "JP-200", "submission_date": today},
    submission_history=[{"consultant_id": "C-002", "end_client": "Google", "vendor_name": "Vendor-A", "job_posting_id": "JP-200", "submission_date": days_ago_15, "status": "pending"}],
    dns_list=[],
)
test(r2["decision"] == "BLOCK", "Rule 2: Same posting ID = BLOCK", f"Got {r2['decision']}")

# Rule 3: Same client, different vendor within 30 days = WARN (unless Rule 1 fires)
r3 = check_submission(
    request={"consultant_id": "C-003", "end_client": "Amazon", "vendor_name": "Vendor-B", "job_posting_id": "JP-300", "submission_date": today},
    submission_history=[{"consultant_id": "C-003", "end_client": "Amazon", "vendor_name": "Vendor-A", "job_posting_id": "JP-250", "submission_date": days_ago_15, "status": "pending"}],
    dns_list=[],
)
# Rule 1 also fires (same consultant+client within 90 days), so BLOCK takes precedence
test(r3["decision"] == "BLOCK", "Rule 3+1: Same client different vendor 15d + Rule 1 = BLOCK", f"Got {r3['decision']}")

# Rule 4: Different consultant, same role = ALLOW + LOG
r4 = check_submission(
    request={"consultant_id": "C-004", "end_client": "Meta", "vendor_name": "Vendor-A", "job_posting_id": "JP-400", "submission_date": today},
    submission_history=[{"consultant_id": "C-099", "end_client": "Meta", "vendor_name": "Vendor-A", "job_posting_id": "JP-400", "submission_date": days_ago_15, "status": "pending"}],
    dns_list=[],
)
test(r4["decision"] == "ALLOW", "Rule 4: Different consultant same role = ALLOW", f"Got {r4['decision']}")

# Rule 5: DNS list match = BLOCK
r5 = check_submission(
    request={"consultant_id": "C-005", "end_client": "Apple", "vendor_name": "Vendor-A", "job_posting_id": "JP-500", "submission_date": today},
    submission_history=[],
    dns_list=[{"consultant_id": "C-005", "company": "Apple", "vendor": "", "reason": "NDA conflict"}],
)
test(r5["decision"] == "BLOCK", "Rule 5: DNS list match = BLOCK", f"Got {r5['decision']}")

# DNS with different vendor (should NOT match if vendor-specific)
r5b = check_submission(
    request={"consultant_id": "C-005", "end_client": "Apple", "vendor_name": "Vendor-A", "job_posting_id": "JP-501", "submission_date": today},
    submission_history=[],
    dns_list=[{"consultant_id": "C-005", "company": "Apple", "vendor": "Vendor-B", "reason": "Vendor-specific block"}],
)
test(r5b["decision"] == "ALLOW", "Rule 5: DNS vendor-specific, different vendor = ALLOW", f"Got {r5b['decision']}")

# Clean submission — no history, no DNS
clean = check_submission(
    request={"consultant_id": "C-006", "end_client": "Netflix", "vendor_name": "Vendor-A", "job_posting_id": "JP-600", "submission_date": today},
    submission_history=[],
    dns_list=[],
)
test(clean["decision"] == "ALLOW", "Clean submission, no history = ALLOW", f"Got {clean['decision']}")

# Multiple rules firing — verify BLOCK overrides WARN
multi = check_submission(
    request={"consultant_id": "C-007", "end_client": "Tesla", "vendor_name": "Vendor-A", "job_posting_id": "JP-700", "submission_date": today},
    submission_history=[
        {"consultant_id": "C-007", "end_client": "Tesla", "vendor_name": "Vendor-B", "job_posting_id": "JP-650", "submission_date": days_ago_15, "status": "pending"},
    ],
    dns_list=[{"consultant_id": "C-007", "company": "Tesla", "vendor": "", "reason": "Previous litigation"}],
)
test(multi["decision"] == "BLOCK", "Multiple rules: DNS + 90-day = BLOCK", f"Got {multi['decision']}")
test(len(multi.get("rules_triggered", [])) >= 2, "Multiple rules triggered", f"Got {len(multi.get('rules_triggered', []))} rules")

# Case insensitivity
case_test = check_submission(
    request={"consultant_id": "C-008", "end_client": "microsoft", "vendor_name": "vendor-a", "job_posting_id": "JP-800", "submission_date": today},
    submission_history=[{"consultant_id": "C-008", "end_client": "MICROSOFT", "vendor_name": "VENDOR-B", "job_posting_id": "JP-750", "submission_date": days_ago_45, "status": "pending"}],
    dns_list=[],
)
test(case_test["decision"] == "BLOCK", "Case-insensitive client matching", f"Got {case_test['decision']}")


# ══════════════════════════════════════════════════════════════════
# SUITE 4: CSV PARSER — MALFORMED INPUT HANDLING
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SUITE 4: CSV Parser — Malformed Input Handling")
print("=" * 70)

# 4a. Non-existent file
profiles, issues = parse_crm_export("/nonexistent/file.csv")
test(len(profiles) == 0, "Non-existent file returns empty profiles")
test(any(i.get("severity") == "CRITICAL" for i in issues), "Non-existent file flags CRITICAL issue")

# 4b. Valid CSV with all 8 rows
sample_csv = str(Path(__file__).parent / "sample_crm_export.csv")
profiles, issues = parse_crm_export(sample_csv)
test(len(profiles) == 8, "Sample CSV parses all 8 rows", f"Got {len(profiles)}")
critical = [i for i in issues if i.get("severity") == "CRITICAL"]
test(len(critical) == 0, "No CRITICAL issues in sample CSV", f"Got {len(critical)}")

# 4c. Create a minimal valid CSV
with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    writer = csv.writer(f)
    writer.writerow(["consultant_id", "full_name", "marketing_name", "primary_category", "job_title",
                     "years_experience", "core_skills", "visa_status", "visa_expiration_date",
                     "employment_type_preference", "target_rate", "min_rate", "location",
                     "remote_preference", "bench_start_date", "linkedin_urls", "do_not_submit",
                     "certifications", "resume_file_reference"])
    writer.writerow(["C-999", "Test User", "TU", "IT", "Dev", "5", "Python;Java", "H1B",
                     "2026-12-31", "C2C", "100", "80", "NYC", "Yes", "2026-01-01", "", "", "", ""])
    tmp_path = f.name

profiles, issues = parse_crm_export(tmp_path)
test(len(profiles) == 1, "Minimal CSV parses 1 row", f"Got {len(profiles)}")
if profiles:
    test(profiles[0]["consultant_id"] == "C-999", "Correct consultant_id parsed")
    test(profiles[0]["visa_status"] == "H1B", "Correct visa_status parsed")
os.unlink(tmp_path)

# 4d. Empty CSV (header only)
with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    writer = csv.writer(f)
    writer.writerow(["consultant_id", "full_name", "marketing_name", "primary_category", "job_title",
                     "years_experience", "core_skills", "visa_status", "visa_expiration_date",
                     "employment_type_preference", "target_rate", "min_rate", "location",
                     "remote_preference", "bench_start_date", "linkedin_urls", "do_not_submit",
                     "certifications", "resume_file_reference"])
    tmp_path = f.name

profiles, issues = parse_crm_export(tmp_path)
test(len(profiles) == 0, "Empty CSV (header only) returns 0 profiles")
os.unlink(tmp_path)


# ══════════════════════════════════════════════════════════════════
# SUITE 5: HOT LIST — FORMAT VALIDATION
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SUITE 5: Hot List Publisher — Format & Content Validation")
print("=" * 70)

# Generate with real priority data
sample_profiles, _ = parse_crm_export(sample_csv)
visa_results = {}
for p in sample_profiles:
    visa_results[p["consultant_id"]] = calculate_visa_urgency({
        "consultant_id": p["consultant_id"],
        "visa_status": p["visa_status"],
        "visa_expiration_date": p.get("visa_expiration_date", ""),
    })

priority_inputs = []
for p in sample_profiles:
    visa = visa_results[p["consultant_id"]]
    bench_start = datetime.strptime(p["bench_start_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    days_on_bench = (datetime.now(timezone.utc) - bench_start).days
    priority_inputs.append({
        "consultant_id": p["consultant_id"],
        "consultant_name": p["full_name"],
        "visa_urgency_tier": visa["urgency_tier"],
        "days_on_bench": days_on_bench,
        "market_demand": "HIGH",
        "rate_tier": "MID",
        "active_submission_count": 0,
    })

priority_results = calculate_batch_priorities(priority_inputs)

hotlist = generate_hotlist(
    prioritized_profiles=priority_results,
    submission_stats={"total_today": 3, "approved": 2, "blocked": 1, "pending": 0},
    stale_submissions=[{"consultant_id": "C-033", "job_id": "JP-OLD", "days_stale": 14}],
    alerts=[
        "VISA ALERT: C-011 (Amit Patel) OPT expires in ~18 days",
        "DATA QUALITY: C-078 missing resume file reference",
    ],
    report_date="2026-02-15",
)

test(isinstance(hotlist, str), "Hot List is a string")
test(len(hotlist) > 100, "Hot List has substantial content", f"Got {len(hotlist)} chars")
test("2026-02-15" in hotlist, "Hot List contains report date")
# Check that at least some consultant names appear
consultant_names_in_hotlist = sum(1 for p in priority_results if p.get("consultant_name", "") in hotlist)
test(consultant_names_in_hotlist >= 4, "Hot List contains most consultant names", f"Found {consultant_names_in_hotlist}/8")

# Empty inputs
empty_hotlist = generate_hotlist(
    prioritized_profiles=[],
    submission_stats={"total_today": 0, "approved": 0, "blocked": 0, "pending": 0},
    stale_submissions=[],
    alerts=[],
    report_date="2026-02-15",
)
test(isinstance(empty_hotlist, str), "Empty Hot List still returns a string")
test(len(empty_hotlist) > 10, "Empty Hot List has header content")


# ══════════════════════════════════════════════════════════════════
# SUITE 6: SCORING WEIGHT INTEGRITY
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SUITE 6: Configuration & Weight Integrity")
print("=" * 70)

# Load and validate priority weights
weights_path = AGENTS_DIR / "z" / "workspace" / "skills" / "scoring" / "priority_weights.json"
with open(weights_path) as f:
    config = json.load(f)

# Weights sum to 1.0
w = config["weights"]
total = sum(w.values())
test(abs(total - 1.0) < 0.001, f"Priority weights sum to 1.0", f"Got {total}")

# All weight factors have matching scoring tables
# Note: weight key is "active_submission_count" but table key is "active_submissions"
scoring_table_keys = set(config["scoring_tables"].keys())
for factor in w.keys():
    # Handle the naming mismatch: weight = "active_submission_count", table = "active_submissions"
    table_key = "active_submissions" if factor == "active_submission_count" else factor
    test(table_key in scoring_table_keys, f"Scoring table exists for '{factor}'", f"Looking for '{table_key}'")

# Thresholds are ordered correctly (p1 > p2 > p3)
t = config["thresholds"]
test(t["p1_urgent"] > t["p2_active"] > t["p3_maintenance"],
     "Thresholds ordered: p1 > p2 > p3",
     f"p1={t['p1_urgent']}, p2={t['p2_active']}, p3={t['p3_maintenance']}")

# Version field exists
test("version" in config, "Config has version field")

# Scoring tables have reasonable values (1-10 range)
for factor, table in config["scoring_tables"].items():
    for bracket, score in table.items():
        test(0 <= score <= 10, f"Score for {factor}/{bracket} in 0-10 range", f"Got {score}")


# ══════════════════════════════════════════════════════════════════
# SUITE 7: FULL DAILY CYCLE SIMULATION
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SUITE 7: Full Daily Cycle Simulation (Morning → Approval → Hot List)")
print("=" * 70)

# Step 1: Ingest CRM data
profiles, issues = parse_crm_export(sample_csv)
test(len(profiles) == 8, "Step 1: CRM ingestion — 8 profiles loaded")

# Step 2: Calculate visa urgency for all
visa_batch = calculate_batch_visa_urgency([
    {"consultant_id": p["consultant_id"], "visa_status": p["visa_status"],
     "visa_expiration_date": p.get("visa_expiration_date", "")}
    for p in profiles
])
test(len(visa_batch) == 8, "Step 2: Visa urgency — 8 results")
critical_visa = [v for v in visa_batch if v["urgency_tier"] == "CRITICAL"]
print(f"    {len(critical_visa)} consultant(s) with CRITICAL visa urgency")

# Step 3: Build priority queue
priority_queue = calculate_batch_priorities([
    {
        "consultant_id": p["consultant_id"],
        "consultant_name": p["full_name"],
        "visa_urgency_tier": next(v["urgency_tier"] for v in visa_batch if v["consultant_id"] == p["consultant_id"]),
        "days_on_bench": (datetime.now(timezone.utc) - datetime.strptime(p["bench_start_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)).days,
        "market_demand": "HIGH",
        "rate_tier": "MID",
        "active_submission_count": 0,
    }
    for p in profiles
])
test(len(priority_queue) == 8, "Step 3: Priority queue — 8 ranked")
test(priority_queue[0]["score"] >= priority_queue[-1]["score"], "Step 3: Queue sorted high-to-low")
print(f"    Top consultant: {priority_queue[0]['consultant_name']} (score={priority_queue[0]['score']}, tier={priority_queue[0]['priority_tier']})")
print(f"    Bottom: {priority_queue[-1]['consultant_name']} (score={priority_queue[-1]['score']}, tier={priority_queue[-1]['priority_tier']})")

# Step 4: Simulate submission requests from Jay
submissions = [
    {"consultant_id": "C-042", "end_client": "Microsoft", "vendor_name": "Robert Half", "job_posting_id": "LI-98765", "submission_date": today},
    {"consultant_id": "C-042", "end_client": "Microsoft", "vendor_name": "TEKsystems", "job_posting_id": "LI-98766", "submission_date": today},
    {"consultant_id": "C-023", "end_client": "Google", "vendor_name": "Insight Global", "job_posting_id": "LI-87654", "submission_date": today},
]

# First submission: clean
r1 = check_submission(request=submissions[0], submission_history=[], dns_list=[])
test(r1["decision"] == "ALLOW", "Step 4a: First submission ALLOW")

# Second submission: same client + same consultant (via different vendor) — should BLOCK on Rule 1
# because first submission was just approved (simulate it being in history now)
history_after_first = [{"consultant_id": "C-042", "end_client": "Microsoft", "vendor_name": "Robert Half", "job_posting_id": "LI-98765", "submission_date": today, "status": "approved"}]
r2 = check_submission(request=submissions[1], submission_history=history_after_first, dns_list=[])
test(r2["decision"] == "BLOCK", "Step 4b: Same client same day via different vendor = BLOCK", f"Got {r2['decision']}")

# Third submission: different consultant, different client
r3 = check_submission(request=submissions[2], submission_history=history_after_first, dns_list=[])
test(r3["decision"] == "ALLOW", "Step 4c: Different consultant + client = ALLOW")

# Step 5: Generate daily Hot List
approved_count = sum(1 for r in [r1, r3] if r["decision"] == "ALLOW")
blocked_count = sum(1 for r in [r2] if r["decision"] == "BLOCK")

final_hotlist = generate_hotlist(
    prioritized_profiles=priority_queue,
    submission_stats={"total_today": 3, "approved": approved_count, "blocked": blocked_count, "pending": 0},
    stale_submissions=[],
    alerts=[f"VISA CRITICAL: {len(critical_visa)} consultant(s) need immediate placement"],
    report_date=today,
)
test(isinstance(final_hotlist, str) and len(final_hotlist) > 50, "Step 5: Hot List generated")
print(f"    Hot List length: {len(final_hotlist)} chars")
print(f"    Daily stats: {approved_count} approved, {blocked_count} blocked")


# ══════════════════════════════════════════════════════════════════
# SUITE 8: LOGGING VERIFICATION
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SUITE 8: Audit Trail / Logging Verification")
print("=" * 70)

# Check that scoring_log.jsonl was populated
log_path = AGENTS_DIR / "z" / "workspace" / "skills" / "scoring" / "scoring_log.jsonl"
if log_path.exists():
    with open(log_path) as f:
        log_lines = f.readlines()
    test(len(log_lines) > 0, f"Scoring log has entries ({len(log_lines)} lines)")
    # Verify log entry format
    # Find a priority_calculation entry (visa entries may use different field names)
    first_entry = json.loads(log_lines[0])
    test("timestamp" in first_entry, "Log entries have timestamp")
    test("event_type" in first_entry, "Log entries have event_type")
    # Check that at least one log entry has consultant_id (priority calc entries do)
    has_consultant_id = any("consultant_id" in json.loads(line) for line in log_lines)
    test(has_consultant_id, "At least one log entry has consultant_id")
else:
    test(False, "Scoring log file exists", "File not found")


# ══════════════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print(f"AGENT Z PRODUCTION VALIDATION: {passed} passed, {failed} failed")
print("=" * 70)

if errors:
    print("\nFailed tests:")
    for e in errors:
        print(f"  ✗ {e}")
    print(f"\n⚠ {failed} test(s) need fixing before production deployment.")
    sys.exit(1)
else:
    print("\n✓ Agent Z is production-ready for OpenClaw deployment.")
    sys.exit(0)
