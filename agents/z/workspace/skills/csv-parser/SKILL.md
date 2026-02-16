# CSV parser skill

This skill handles ingestion of flat file exports from the Log1 CRM. It parses CSV and Excel files into structured consultant profiles, validates all fields, and flags data gaps.

## Script

### csv_parser.py
Call `parse_crm_export(file_path, existing_profiles)` to parse a CRM export.

Returns a tuple of (validated_profiles, issues). Issues have severity levels:
- CRITICAL: Missing required columns or file not found. Parsing stops.
- HIGH: Missing visa status, missing bench start date, missing expiration date for expiring visas.
- MEDIUM: Unrecognized category, invalid dates, missing rates.
- LOW: Missing optional fields, detected changes from previous import.

## Expected CSV columns (minimum viable)
consultant_id, full_name, marketing_name, primary_category, job_title, years_experience, core_skills, visa_status, visa_expiration_date, employment_type_preference, target_rate, min_rate, location, remote_preference, bench_start_date, linkedin_urls, do_not_submit, certifications, resume_file_reference

## Ingestion process
1. Receive flat file (CSV/Excel) with candidate data
2. Parse and validate against expected schema
3. Flag missing or inconsistent fields
4. Merge with existing consultant profiles (match on consultant_id)
5. Detect changes from previous import
6. Return validated profiles for priority recalculation

## Rules
- Never silently use invalid data. Flag it.
- Semicolons separate multi-value fields (core_skills, linkedin_urls, do_not_submit, certifications).
- Supports both CSV and Excel (.xlsx) formats.
- If openpyxl is not installed for Excel reading, flag it as HIGH severity.
