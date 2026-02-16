# Skill: LinkedIn Application Executor

## Purpose

Execute LinkedIn job applications safely with pre-flight checks, timing simulation, error handling, and complete audit trail. All applications require Z approval before execution.

## What it does

- Performs pre-flight safety checks (health state, daily limits, timing, proxy, approval)
- Simulates realistic application workflow (reading time, form parsing, submission)
- Captures confirmation screenshots for audit trail
- Handles errors with appropriate escalation (rate limits, warnings, network issues)
- Logs everything with Z approval reference

## Why it matters

LinkedIn applications are the core action. But they're also the highest-risk action (triggers restrictions if done too fast, too many, or too mechanically). Safe execution requires:
1. Permission from Z (the submission gatekeeper)
2. Health-based rate limiting (GREEN allows more than YELLOW)
3. Human-like timing (read time before submit)
4. Proper error detection (warnings, blocks, rate limits)
5. Complete audit trail (screenshot proof)

## How to use it

### Pre-flight check

```python
from application_executor.linkedin_apply import preflight_check

check = preflight_check({
    "profile_id": "P-001",
    "health_state": "GREEN",
    "tier": "A",
    "daily_app_count": 1,
    "last_app_minutes_ago": 12,
    "proxy_ip": "192.0.2.15",
    "z_approval_id": "SUBMIT-5678"
})

if check["status"] == "OK":
    print("All checks passed - safe to proceed")
else:
    print(f"Blocked: {check['issues']}")
```

### Execute application

```python
from application_executor.linkedin_apply import execute_application

result = execute_application({
    "profile_id": "P-001",
    "job_id": "JOB-98765",
    "job_title": "Senior Python Developer",
    "company_name": "TechCorp",
    "application_package": {
        "resume_version": "v3-techcorp",
        "cover_letter": "optional_custom"
    },
    "z_approval_id": "SUBMIT-5678",
    "proxy_ip": "192.0.2.15",
    "session_id": "SES-001"
})

if result["status"] == "SUCCESS":
    print(f"Application {result['application_id']} submitted")
    print(f"Screenshot: {result['screenshot_path']}")
else:
    print(f"Error: {result['error_type']}")
```

### Handle errors

```python
from application_executor.linkedin_apply import handle_error, get_error_recovery_action

error = handle_error("rate_limit", {
    "profile_id": "P-001",
    "job_id": "JOB-98765"
})

action = get_error_recovery_action(error)
# action will be "RETRY_LATER" for rate_limit
```

## Pre-flight checks

Before executing any application, the system checks:

### 1. Health State
| State | Status | Daily Limit |
|-------|--------|------------|
| GREEN | ✅ Allowed | Tier default (A=5, B=2, C=1) |
| YELLOW | ✅ Allowed | 2 applications per day (override) |
| ORANGE | ❌ Blocked | No applications |
| RED | ❌ Blocked | No activity |

### 2. Daily Application Limit
- Tier A: 5 per day
- Tier B: 2 per day
- Tier C: 1 per day
- Tier D: 0 per day
- YELLOW state: 2 per day (overrides tier limit)

### 3. Time Gap Since Last Application
- Minimum: 5 minutes between applications on same profile
- Randomized in real execution: 5-15 minutes

### 4. Proxy IP Configuration
- Must have valid proxy IP assigned
- IP should not be reused across profiles same day

### 5. Z Approval
- Must have Z approval ID (SUBMIT-XXXXX)
- Proof of Z's permission to submit

## Application workflow

### Stage 1: Navigation (3 sec simulated)
- Navigate to job posting URL
- Verify page loads correctly

### Stage 2: Reading (30-60 sec random)
- Simulate human reading job description
- Random duration to appear human-like

### Stage 3: Form Parsing (2-5 sec)
- Identify form fields in application
- Map fields to Rick's application package

### Stage 4: Form Filling (10-30 sec random)
- Fill resume field (version from package)
- Auto-fill contact info
- Fill optional cover letter if provided
- Random duration to appear realistic

### Stage 5: Submission (2-5 sec)
- Click submit button
- Confirm submission success

### Stage 6: Confirmation (1-2 sec)
- Capture screenshot of confirmation page
- Store screenshot reference in audit trail

## Output format

```json
{
  "status": "SUCCESS",
  "profile_id": "P-001",
  "job_id": "JOB-98765",
  "application_id": "APP-20260215103245-45678",
  "company_name": "TechCorp",
  "job_title": "Senior Python Developer",
  "z_approval_id": "SUBMIT-5678",
  "submission_timestamp": "2026-02-15T10:34:12Z",
  "screenshot_path": "/tmp/leroy_screenshots/P-001_JOB-98765_APP-20260215103245-45678.png",
  "preflight_checks": {
    "health_state": "GREEN",
    "daily_limit_ok": true,
    "last_app_gap_ok": true,
    "proxy_valid": true,
    "z_approved": true
  },
  "workflow": {
    "stage_1_navigation": { "status": "completed", "duration_seconds": 3 },
    "stage_2_reading": { "status": "completed", "duration_seconds": 45 },
    "stage_3_form_parsing": { "status": "completed", "fields_found": 4 },
    "stage_4_form_fill": { "status": "completed", "duration_seconds": 22 },
    "stage_5_submission": { "status": "completed", "duration_seconds": 3 },
    "stage_6_confirmation": { "status": "completed", "screenshot_captured": true }
  },
  "details": {
    "form_fields_filled": 4,
    "reading_time_seconds": 45,
    "user_agent": "Mozilla/5.0...",
    "proxy_ip": "192.0.2.15",
    "browser": "Ads Power Browser"
  },
  "audit_trail": {
    "initiated_at": "2026-02-15T10:33:27Z",
    "completed_at": "2026-02-15T10:34:12Z",
    "total_duration_seconds": 45,
    "z_approval_id": "SUBMIT-5678",
    "profile_id": "P-001",
    "job_id": "JOB-98765"
  }
}
```

## Error handling

### Unexpected Form Field
**Severity:** MEDIUM
**Trigger:** LinkedIn presents fields not expected
**Action:** Flag and escalate to EM
**Message:** "Unexpected form field encountered - manual review needed"

### External ATS
**Severity:** LOW
**Trigger:** Application redirected to external tracking system
**Action:** Log and continue
**Message:** "Application redirected to external ATS - proceeding with submission"

### Profile Warning Banner
**Severity:** CRITICAL
**Trigger:** LinkedIn warning banner appears during application
**Action:** Stop immediately, quarantine profile
**Message:** "LinkedIn warning banner detected - quarantine profile immediately"
**Escalation:** To Z immediately (restrict profile)

### Rate Limit
**Severity:** HIGH
**Trigger:** "You're applying too fast" or similar message
**Action:** Backoff and retry later
**Message:** "Rate limited - will retry after backoff or defer to next day"
**Escalation:** Alert EM if 3 failures

### Network Error
**Severity:** MEDIUM
**Trigger:** Connection lost, timeout, etc.
**Action:** Retry up to 3 times
**Message:** "Network error - attempting retry"

## Input schema

### Preflight check

```json
{
  "profile_id": "P-001",
  "health_state": "GREEN",
  "tier": "A",
  "daily_app_count": 1,
  "last_app_minutes_ago": 12,
  "proxy_ip": "192.0.2.15",
  "z_approval_id": "SUBMIT-5678"
}
```

### Application execution

```json
{
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
}
```

## Performance

- Preflight check: <10ms
- Application execution: 45-130 seconds (realistic human timing)
- Screenshot capture: <1s

## Integration points

- **Z (Submission Gatekeeper):** Provides approval before execution
- **Schedule Generator:** Determines when application is scheduled
- **Health Calculator:** Determines health state and daily limits
- **Portfolio Manager:** Tracks daily application counts
- **Rick (Resume Builder):** Provides application package

## Audit trail

Every application creates an immutable record:
- Application ID (unique, timestamped)
- Profile ID + Job ID
- Z approval reference (proof of permission)
- Full workflow stages with timestamps
- Screenshot path (proof of submission)
- Proxy IP used
- User agent
- Session ID

This allows complete accountability: Z can verify that Leroy only applied when approved, to the right job, with the right resume.

## Safety constraints enforced

1. **No application without Z approval** - Hard block
2. **No application when RED** - Hard block
3. **No application when ORANGE** - Hard block
4. **No more than tier daily limit (GREEN) or 2 (YELLOW)** - Hard block
5. **No less than 5 minutes gap** - Hard block
6. **Profile warning detected** - Immediate quarantine
7. **Rate limit detected** - Backoff and escalate

## Future enhancements

- Real Ads Power Browser integration (currently simulated)
- Real LinkedIn form submission (currently simulated)
- Cover letter customization based on job posting
- Automatic rejection handling (follow-up messages)
- Success rate tracking per profile
