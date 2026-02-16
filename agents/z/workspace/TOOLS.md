# Tools available to Z

## Scoring scripts (deterministic, Python)

### priority_calculator.py
- **Purpose:** Compute priority scores for each consultant.
- **Input:** JSON with visa_urgency, days_on_bench, market_demand_score, rate_tier, active_submission_count.
- **Output:** JSON with composite score (0-10), per-factor breakdown, priority tier (P1/P2/P3/P4).
- **Weights:** Loaded from `priority_weights.json`. Human-editable.
- **Usage:** Called daily when generating the prioritized queue. Called on-demand when new CRM data arrives.

### visa_urgency_calculator.py
- **Purpose:** Compute visa urgency tier from visa type and expiration date.
- **Input:** JSON with visa_status, visa_expiration_date, current_date.
- **Output:** JSON with urgency_tier (CRITICAL/HIGH/MEDIUM/LOW/NA), days_remaining, urgency_score (0-10).
- **Usage:** Called during CRM data ingestion and daily priority recalculation.

### duplicate_checker.py
- **Purpose:** Check a submission request against the full submission history for conflicts.
- **Input:** JSON with consultant_id, end_client, vendor_name, job_posting_id, submission_history (list).
- **Output:** JSON with decision (ALLOW/BLOCK/WARN), rule_triggered, conflicting_record (if any).
- **Usage:** Called for every submission request before approval.

## Data ingestion

### csv_parser.py
- **Purpose:** Parse flat file exports from Log1 CRM into structured consultant profiles.
- **Input:** File path to CSV/Excel file.
- **Output:** List of validated consultant profiles (JSON), list of validation errors/warnings.
- **Expected columns:** consultant_id, full_name, marketing_name, primary_category, job_title, years_experience, core_skills, visa_status, visa_expiration_date, employment_type_preference, target_rate, min_rate, location, remote_preference, bench_start_date, linkedin_urls, do_not_submit, certifications, resume_file_reference.

## Reporting

### hotlist_publisher.py
- **Purpose:** Generate the daily Hot List in the standard format for Slack publishing.
- **Input:** List of consultant profiles with priority scores, submission stats, alerts.
- **Output:** Formatted Hot List string ready for Slack posting.
- **Usage:** Called daily at 06:30-07:00 ET.

## Database (Supabase -- future)
- Supabase will serve as the persistent database for consultant profiles, submission records, and identity maps.
- For now, data is stored in memory files (markdown/JSON) within the workspace.
- Migration to Supabase is planned but not yet implemented.

## Slack (via EM)
- Z does not post to Slack directly. All Slack communication goes through EM.
- Z sends structured data to EM. EM formats and posts to the appropriate channel.
- Exception: the daily Hot List is formatted by Z (via hotlist_publisher.py) and handed to EM for posting.
