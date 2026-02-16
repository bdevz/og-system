"""
CSV Parser for Agent Z -- Log1 CRM Flat File Ingestion
=======================================================
Parses CSV/Excel exports from Log1 CRM into structured consultant profiles.
Validates all fields, flags gaps, merges with existing profiles.

Usage:
    from csv_parser import parse_crm_export

    profiles, errors = parse_crm_export("/path/to/export.csv")
"""

import csv
import json
import os
from datetime import datetime, timezone, date
from pathlib import Path
from typing import Tuple


EXPECTED_COLUMNS = [
    "consultant_id",
    "full_name",
    "marketing_name",
    "primary_category",
    "job_title",
    "years_experience",
    "core_skills",
    "visa_status",
    "visa_expiration_date",
    "employment_type_preference",
    "target_rate",
    "min_rate",
    "location",
    "remote_preference",
    "bench_start_date",
    "linkedin_urls",
    "do_not_submit",
    "certifications",
    "resume_file_reference",
]

REQUIRED_COLUMNS = [
    "consultant_id",
    "full_name",
    "primary_category",
    "visa_status",
    "bench_start_date",
]

VALID_CATEGORIES = {"Java Developer", "Python Developer", "AI-ML Engineer", "DevOps Engineer", "Cloud Architect"}
VALID_VISA_STATUSES = {"H1B", "OPT", "CPT", "STEM-OPT", "GC", "GC-EAD", "Citizen", "TN", "L1", "Other"}
VALID_REMOTE_PREFS = {"Remote only", "Hybrid", "Onsite", "Flexible", "Remote", ""}
VALID_EMPLOYMENT_TYPES = {"W2", "C2C", "1099", "FTE", "Any", ""}


def parse_crm_export(file_path: str, existing_profiles: dict = None) -> Tuple[list, list]:
    """
    Parse a CRM flat file export and validate.

    Args:
        file_path: Path to CSV or Excel file.
        existing_profiles: Optional dict of existing profiles keyed by consultant_id,
                          used for merge/change detection.

    Returns:
        Tuple of (validated_profiles: list, issues: list).
        Each issue has severity (CRITICAL/HIGH/MEDIUM/LOW), consultant_id, field, message.
    """
    file_path = Path(file_path)
    issues = []
    profiles = []

    if not file_path.exists():
        return [], [{"severity": "CRITICAL", "message": f"File not found: {file_path}"}]

    # Determine file type and read
    if file_path.suffix.lower() in (".xlsx", ".xls"):
        rows, header_issues = _read_excel(file_path)
    elif file_path.suffix.lower() in (".csv", ".tsv"):
        rows, header_issues = _read_csv(file_path)
    else:
        return [], [{"severity": "CRITICAL", "message": f"Unsupported file type: {file_path.suffix}"}]

    issues.extend(header_issues)
    if any(i["severity"] == "CRITICAL" for i in issues):
        return [], issues

    # Process each row
    changes_detected = []
    for row_num, row in enumerate(rows, start=2):  # start=2 because row 1 is header
        profile, row_issues = _validate_row(row, row_num)
        issues.extend(row_issues)

        if profile:
            # Calculate derived fields
            profile["days_on_bench"] = _calculate_days_on_bench(profile.get("bench_start_date"))

            # Detect changes from existing profiles
            if existing_profiles and profile["consultant_id"] in existing_profiles:
                changes = _detect_changes(existing_profiles[profile["consultant_id"]], profile)
                if changes:
                    changes_detected.append({
                        "consultant_id": profile["consultant_id"],
                        "changes": changes
                    })

            profiles.append(profile)

    # Summary
    if changes_detected:
        for change in changes_detected:
            issues.append({
                "severity": "LOW",
                "consultant_id": change["consultant_id"],
                "field": "multiple",
                "message": f"Changes detected: {', '.join(change['changes'])}"
            })

    return profiles, issues


def _read_csv(file_path: Path) -> Tuple[list, list]:
    """Read CSV file and return rows + any header issues."""
    issues = []
    rows = []

    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []

        # Check for missing expected columns
        missing = [col for col in REQUIRED_COLUMNS if col not in headers]
        if missing:
            issues.append({
                "severity": "CRITICAL",
                "message": f"Missing required columns: {', '.join(missing)}. Found: {', '.join(headers)}"
            })
            return [], issues

        optional_missing = [col for col in EXPECTED_COLUMNS if col not in headers and col not in REQUIRED_COLUMNS]
        if optional_missing:
            issues.append({
                "severity": "LOW",
                "message": f"Optional columns not found in file: {', '.join(optional_missing)}"
            })

        for row in reader:
            rows.append(row)

    return rows, issues


def _read_excel(file_path: Path) -> Tuple[list, list]:
    """Read Excel file using openpyxl. Falls back to CSV-like parsing."""
    try:
        import openpyxl
    except ImportError:
        return [], [{"severity": "HIGH", "message": "openpyxl not installed. Cannot read .xlsx files. Install with: pip install openpyxl"}]

    issues = []
    rows = []

    wb = openpyxl.load_workbook(file_path, read_only=True)
    ws = wb.active

    all_rows = list(ws.iter_rows(values_only=True))
    if not all_rows:
        return [], [{"severity": "CRITICAL", "message": "Excel file is empty"}]

    headers = [str(h).strip() if h else "" for h in all_rows[0]]

    missing = [col for col in REQUIRED_COLUMNS if col not in headers]
    if missing:
        issues.append({
            "severity": "CRITICAL",
            "message": f"Missing required columns: {', '.join(missing)}. Found: {', '.join(headers)}"
        })
        return [], issues

    for row_vals in all_rows[1:]:
        row = {}
        for i, header in enumerate(headers):
            if header and i < len(row_vals):
                val = row_vals[i]
                row[header] = str(val).strip() if val is not None else ""
            elif header:
                row[header] = ""
        rows.append(row)

    wb.close()
    return rows, issues


def _validate_row(row: dict, row_num: int) -> Tuple[dict, list]:
    """Validate a single row and return (profile, issues)."""
    issues = []
    profile = {}

    # --- Required fields ---
    consultant_id = row.get("consultant_id", "").strip()
    if not consultant_id:
        issues.append({"severity": "CRITICAL", "row": row_num, "field": "consultant_id", "message": "Missing consultant_id. Row skipped."})
        return None, issues
    profile["consultant_id"] = consultant_id

    full_name = row.get("full_name", "").strip()
    if not full_name:
        issues.append({"severity": "HIGH", "row": row_num, "consultant_id": consultant_id, "field": "full_name", "message": "Missing full_name."})
    profile["full_name"] = full_name

    profile["marketing_name"] = row.get("marketing_name", "").strip() or full_name

    # Primary category
    category = row.get("primary_category", "").strip()
    if category not in VALID_CATEGORIES:
        issues.append({"severity": "MEDIUM", "row": row_num, "consultant_id": consultant_id, "field": "primary_category", "message": f"Unrecognized category: '{category}'. Expected one of: {', '.join(VALID_CATEGORIES)}"})
    profile["primary_category"] = category

    profile["job_title"] = row.get("job_title", "").strip()

    # Years experience
    try:
        profile["years_experience"] = int(float(row.get("years_experience", 0)))
    except (ValueError, TypeError):
        profile["years_experience"] = 0
        issues.append({"severity": "MEDIUM", "row": row_num, "consultant_id": consultant_id, "field": "years_experience", "message": f"Invalid years_experience: '{row.get('years_experience')}'. Defaulting to 0."})

    # Core skills (semicolon-separated)
    skills_raw = row.get("core_skills", "").strip()
    profile["core_skills"] = [s.strip() for s in skills_raw.split(";") if s.strip()] if skills_raw else []

    # --- Visa ---
    visa_status = row.get("visa_status", "").strip()
    if not visa_status:
        issues.append({"severity": "HIGH", "row": row_num, "consultant_id": consultant_id, "field": "visa_status", "message": "ALERT: Missing visa_status. Cannot prioritize without this."})
    elif visa_status not in VALID_VISA_STATUSES:
        issues.append({"severity": "MEDIUM", "row": row_num, "consultant_id": consultant_id, "field": "visa_status", "message": f"Unrecognized visa_status: '{visa_status}'."})
    profile["visa_status"] = visa_status

    visa_exp = row.get("visa_expiration_date", "").strip()
    if visa_exp:
        try:
            date.fromisoformat(visa_exp)
            profile["visa_expiration_date"] = visa_exp
        except ValueError:
            issues.append({"severity": "MEDIUM", "row": row_num, "consultant_id": consultant_id, "field": "visa_expiration_date", "message": f"Invalid date format: '{visa_exp}'. Expected YYYY-MM-DD."})
            profile["visa_expiration_date"] = None
    else:
        profile["visa_expiration_date"] = None
        if visa_status in {"H1B", "OPT", "CPT", "STEM-OPT", "L1", "TN", "GC-EAD"}:
            issues.append({"severity": "HIGH", "row": row_num, "consultant_id": consultant_id, "field": "visa_expiration_date", "message": f"ALERT: {visa_status} visa requires expiration date but none provided."})

    # --- Employment & Rate ---
    emp_type = row.get("employment_type_preference", "").strip()
    profile["employment_type_preference"] = emp_type

    try:
        profile["target_rate"] = float(row.get("target_rate", 0))
    except (ValueError, TypeError):
        profile["target_rate"] = 0
        issues.append({"severity": "MEDIUM", "row": row_num, "consultant_id": consultant_id, "field": "target_rate", "message": "ALERT: Missing or invalid target_rate. Jay can't filter by rate compatibility."})

    try:
        profile["min_rate"] = float(row.get("min_rate", 0))
    except (ValueError, TypeError):
        profile["min_rate"] = 0

    # --- Location ---
    profile["location"] = row.get("location", "").strip()
    profile["remote_preference"] = row.get("remote_preference", "").strip()

    # --- Bench ---
    bench_start = row.get("bench_start_date", "").strip()
    if bench_start:
        try:
            date.fromisoformat(bench_start)
            profile["bench_start_date"] = bench_start
        except ValueError:
            issues.append({"severity": "MEDIUM", "row": row_num, "consultant_id": consultant_id, "field": "bench_start_date", "message": f"Invalid date format: '{bench_start}'."})
            profile["bench_start_date"] = None
    else:
        profile["bench_start_date"] = None
        issues.append({"severity": "HIGH", "row": row_num, "consultant_id": consultant_id, "field": "bench_start_date", "message": "Missing bench_start_date. Cannot calculate days on bench."})

    # --- LinkedIn ---
    linkedin_raw = row.get("linkedin_urls", "").strip()
    profile["linkedin_urls"] = [u.strip() for u in linkedin_raw.split(";") if u.strip()] if linkedin_raw else []

    # --- DNS ---
    dns_raw = row.get("do_not_submit", "").strip()
    profile["do_not_submit"] = [d.strip() for d in dns_raw.split(";") if d.strip()] if dns_raw else []

    # --- Certifications ---
    certs_raw = row.get("certifications", "").strip()
    profile["certifications"] = [c.strip() for c in certs_raw.split(";") if c.strip()] if certs_raw else []

    # --- Resume ---
    profile["resume_file_reference"] = row.get("resume_file_reference", "").strip()
    if not profile["resume_file_reference"]:
        issues.append({"severity": "LOW", "row": row_num, "consultant_id": consultant_id, "field": "resume_file_reference", "message": "No resume file reference."})

    # --- Status ---
    profile["status"] = "active"
    profile["imported_at"] = datetime.now(timezone.utc).isoformat()

    return profile, issues


def _calculate_days_on_bench(bench_start_date: str) -> int:
    """Calculate days on bench from start date."""
    if not bench_start_date:
        return 0
    try:
        start = date.fromisoformat(bench_start_date)
        return max(0, (date.today() - start).days)
    except (ValueError, TypeError):
        return 0


def _detect_changes(old_profile: dict, new_profile: dict) -> list:
    """Detect meaningful changes between old and new profiles."""
    changes = []
    watch_fields = ["visa_status", "visa_expiration_date", "target_rate", "min_rate",
                    "primary_category", "core_skills", "location", "remote_preference",
                    "do_not_submit", "status"]
    for field in watch_fields:
        old_val = old_profile.get(field)
        new_val = new_profile.get(field)
        if old_val != new_val:
            changes.append(f"{field}: {old_val} -> {new_val}")
    return changes


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        profiles, issues = parse_crm_export(sys.argv[1])
        print(f"\nParsed {len(profiles)} profiles with {len(issues)} issues.\n")
        for issue in issues:
            print(f"  [{issue['severity']}] {issue.get('consultant_id', '')} {issue.get('field', '')}: {issue['message']}")
        print(f"\nProfiles:")
        for p in profiles:
            print(f"  {p['consultant_id']} | {p['full_name']} | {p['primary_category']} | {p['visa_status']} | Bench: {p.get('days_on_bench', '?')} days")
    else:
        print("Usage: python csv_parser.py <path_to_csv>")
        print("       Parses Log1 CRM export and validates consultant profiles.")
