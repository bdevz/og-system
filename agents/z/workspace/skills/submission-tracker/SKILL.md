# Submission tracker skill

This skill manages the submission lifecycle for all consultants. Every application across the entire agency gets logged here.

## Submission record structure

Each submission record contains:
- submission_id (auto-generated)
- date_submitted (timestamp)
- consultant_id and name
- linkedin_profile_used
- job_title, job_posting_id, portal
- vendor_name, vendor_tier, recruiter_name
- end_client, end_client_deduction_confidence
- current_status: Submitted / Recruiter Responded / Interview Scheduled / Interview Completed / Offered / Placed / Rejected / Ghosted / Withdrawn
- status_history (list of timestamped status changes)
- days_since_last_status_change (auto-calculated)
- staleness_flag (true if no update in 7+ days)
- outcome: result, rejection_reason, feedback_notes
- cross_reference_checks: same_client_before, same_role_different_vendor, prior_submissions

## How Z uses this

1. When a submission request arrives, Z calls duplicate_checker.py against this history.
2. When Z approves a submission, a new record is created here.
3. When Leroy confirms an application, the record is updated with confirmation.
4. When outcomes arrive (interview, rejection, placement), the record is updated.
5. Stale submissions (7+ days no update) appear on the Hot List.

## Storage

For now, submission records are stored in memory/submission-log.jsonl (append-only).
Future: migrate to Supabase for query performance at scale.

## Rules
- Every submission gets a unique ID.
- Status changes are appended to history, never overwritten.
- Staleness is calculated daily during Hot List generation.
- Z checks this log before every submission approval.
