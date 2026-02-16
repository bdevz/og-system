# Tools: Leroy's Skill Arsenal

All tools in Leroy's workspace are scripts that run deterministically with complete audit trails. Leroy calls these tools, they return structured results, Leroy logs and acts on the results.

## Scoring Skills

### health_calculator.py

**Purpose:** Compute LinkedIn profile health score (0-100) and health state (GREEN/YELLOW/ORANGE/RED) based on account metrics.

**Usage:**
```python
from scoring.health_calculator import calculate_health, calculate_portfolio_health

# Single profile
result = calculate_health({
    "profile_id": "P-001",
    "account_age_days": 180,
    "connection_count": 350,
    "daily_application_count": 2,
    "days_since_last_restriction": 45,
    "activity_diversity_score": 85,
    "session_pattern_regularity_score": 90,
    "connection_request_acceptance_rate": 75
})

# Portfolio snapshot
results = calculate_portfolio_health([profile1, profile2, ...])
```

**Returns:**
```json
{
  "profile_id": "P-001",
  "score": 78,
  "state": "YELLOW",
  "breakdown": {
    "account_age": { "raw": 100, "weight": 0.15, "contribution": 15 },
    "connection_count": { "raw": 100, "weight": 0.15, "contribution": 15 },
    ...
  },
  "recommended_actions": ["reduce_daily_applications_to_2", "increase_activity_diversity"],
  "next_check": "2026-02-15T18:00:00Z",
  "timestamp": "2026-02-15T12:00:00Z"
}
```

**Input schema:** Dict with profile ID and 7 scoring factors (listed above).

**Output schema:** Health score (0-100), state enum (GREEN/YELLOW/ORANGE/RED), breakdown of each factor, recommended actions, timestamp.

**Logging:** Every calculation appended to `scoring_log.jsonl` with full breakdown.

---

## Activity Simulator Skills

### schedule_generator.py

**Purpose:** Generate randomized daily activity schedules per profile per tier that simulate human-like LinkedIn behavior.

**Usage:**
```python
from activity_simulator.schedule_generator import generate_schedule, generate_batch_schedules

# Single profile
schedule = generate_schedule({
    "profile_id": "P-001",
    "tier": "A",
    "date": "2026-02-15",
    "health_state": "GREEN",
    "primary_timezone": "EST"
})

# Batch for entire portfolio
schedules = generate_batch_schedules(profile_list, date="2026-02-15")
```

**Returns:**
```json
{
  "profile_id": "P-001",
  "date": "2026-02-15",
  "tier": "A",
  "schedule": [
    {
      "session": 1,
      "login_time": "2026-02-15T08:15:00-05:00",
      "duration_minutes": 22,
      "activities": [
        { "activity": "browse", "duration": 8, "count": 1 },
        { "activity": "reactions", "count": 4 },
        { "activity": "profile_views", "count": 3 },
        { "activity": "connection_requests", "count": 2 }
      ]
    },
    {
      "session": 2,
      "login_time": "2026-02-15T13:45:00-05:00",
      "duration_minutes": 18,
      "activities": [...]
    }
  ]
}
```

**Tier specifications:**
- **Tier A:** 2 sessions/day, 15-30 min total, 2-5 apps/day, diverse activities
- **Tier B:** 1-2 sessions/day, 10-20 min total, 0-2 apps/day, moderate activity
- **Tier C:** 1 session every 2-3 days, 5-10 min, 0-1 app per 3 days, light activity
- **Tier D:** No activity

**Randomization:**
- Login times: ±15 min within tier-defined windows
- Session duration: ±3 min within tier bounds
- Activity counts: Random within tier bounds
- Gap between sessions: 2-5 hours
- Weekend activity: 50% probability, reduced volume

**Logging:** Every schedule appended to activity log with tier and health state.

---

## Inbound Classifier Skills

### message_classifier.py

**Purpose:** Classify inbound LinkedIn messages and determine routing/action.

**Usage:**
```python
from inbound_classifier.message_classifier import classify_message

result = classify_message({
    "message_id": "MSG-1234",
    "profile_id": "P-001",
    "sender_name": "John Smith",
    "sender_title": "Senior Recruiter",
    "sender_company": "TechStaff Inc",
    "message_text": "Hi, we have a great Python role for a midlevel developer in Boston. Are you available?",
    "timestamp": "2026-02-15T10:30:00Z"
})
```

**Returns:**
```json
{
  "message_id": "MSG-1234",
  "profile_id": "P-001",
  "classification": "A",
  "class_label": "HOT",
  "confidence": 0.92,
  "reason": "Recruiter title + specific role mention + availability question",
  "routing": {
    "route_to": "rick",
    "urgency": "immediate",
    "sla_minutes": 15
  },
  "sender_context": {
    "name": "John Smith",
    "title": "Senior Recruiter",
    "company": "TechStaff Inc",
    "company_tier": "TIER_1"
  },
  "opportunity_summary": "Python developer, Boston, midlevel",
  "timestamp": "2026-02-15T10:30:00Z"
}
```

**Classification:**
- **Class A (HOT):** Recruiter title + specific role/tech + availability question + Tier 1/2 staffing firm → Route to Rick in 15 min
- **Class B (WARM):** Vague role mention + HR (not dedicated recruiter) + connection request with opportunity → Route to Rick in 2 hours
- **Class C (NETWORKING):** Generic connection request + industry peer + group follow-up → Accept, log, no escalation
- **Class D (SPAM):** Sales pitch + MLM + insurance + mass InMail → Ignore
- **Class E (SUSPICIOUS):** LinkedIn Trust & Safety + verification request + identity confirmation → STOP all activity, alert human immediately

**Rules:** Defined in `classifier_rules.json` with keyword lists, title patterns, known staffing firm names.

**Logging:** Every classification appended to classification log with confidence, sender profile, full message.

---

## Application Executor Skills

### linkedin_apply.py

**Purpose:** Execute LinkedIn job applications with full pre-flight checks, timing simulation, error handling, and audit trail.

**Usage:**
```python
from application_executor.linkedin_apply import execute_application

result = execute_application({
    "profile_id": "P-001",
    "job_id": "JOB-98765",
    "job_title": "Senior Python Developer",
    "company_name": "TechCorp",
    "application_package": {
        "resume_version": "v3-techcorp",
        "cover_letter": "optional",
        "targeting_notes": "emphasize cloud experience"
    },
    "z_approval_id": "SUBMIT-5678",
    "proxy_ip": "192.0.2.15",
    "session_id": "SES-2026-02-15-001"
})
```

**Returns:**
```json
{
  "status": "SUCCESS",
  "profile_id": "P-001",
  "job_id": "JOB-98765",
  "application_id": "APP-12345",
  "timestamp": "2026-02-15T10:45:00Z",
  "z_approval_id": "SUBMIT-5678",
  "screenshot_path": "/path/to/confirmation_screenshot.png",
  "details": {
    "form_fields_filled": 4,
    "reading_time_simulated": 45,
    "submission_time": "2026-02-15T10:45:32Z",
    "user_agent": "Mozilla/5.0...",
    "proxy_ip": "192.0.2.15"
  },
  "preflight_checks": {
    "health_state": "GREEN",
    "daily_limit_ok": true,
    "last_app_gap_minutes": 12,
    "proxy_valid": true
  }
}
```

**Pre-flight checks:**
1. Health state is GREEN (or YELLOW with reduced count)
2. Daily application limit not exceeded
3. Time since last application >5 minutes
4. Proxy IP valid and not reused today on other profiles
5. Z approval present and current

**Application workflow:**
1. Navigate to job posting (simulated timing 30-60 sec to read JD)
2. Parse form fields
3. Fill resume/contact info from Rick's package
4. Fill optional cover letter if provided
5. Submit application
6. Capture confirmation screenshot
7. Log application with full details

**Error handling:**
- Unexpected form field: Flag and escalate
- External ATS (not LinkedIn): Log and proceed
- Profile warning banner: STOP, quarantine profile, alert human
- Rate limit: Backoff and retry or defer to next day
- Network error: Retry up to 3 times, then escalate

**Logging:** Every application appended to `application_history.jsonl` with all details, screenshot reference, Z approval ID.

---

## Connection Manager Skills

### connection_strategy.py

**Purpose:** Manage connection targeting and request execution per tier.

**Usage:**
```python
from connection_manager.connection_strategy import get_connection_targets, execute_connection_request

# Get daily connection targets for profile
targets = get_connection_targets({
    "profile_id": "P-001",
    "tier": "A",
    "date": "2026-02-15",
    "daily_limit": 20
})

# Execute connection request
result = execute_connection_request({
    "profile_id": "P-001",
    "target_id": "T-5678",
    "target_name": "Jane Recruiter",
    "target_title": "Technical Recruiter",
    "note": None,  # 70% no note, 20% generic, 10% personalized
    "proxy_ip": "192.0.2.15"
})
```

**Returns:**
```json
{
  "request_id": "CONN-REQ-1234",
  "profile_id": "P-001",
  "target_id": "T-5678",
  "status": "SENT",
  "timestamp": "2026-02-15T11:30:00Z",
  "note_sent": false
}
```

**Tier daily limits:**
- Tier A: 20 connection requests
- Tier B: 15 connection requests
- Tier C: 8 connection requests
- Tier D: 0 connection requests

**Target tiers:**
- **Tier 1 targets:** Recruiters at Tier 1 staffing firms, technical recruiters at target clients, hiring managers
- **Tier 2 targets:** Tier 2 recruiters, HR professionals, industry peers with 500+ connections
- **Tier 3 targets:** Open networkers, alumni, group members

**Note distribution:**
- 70% no note
- 20% short generic note ("Interested in connecting" or similar)
- 10% personalized note (based on target's background/title)

**Logging:** Every connection request appended to `connection_database.jsonl` with target profile, note, status.

---

## Profile Lifecycle Skills

### warming_protocol.py

**Purpose:** Generate daily warming activity schedule for new Tier C profiles to build trust and account legitimacy.

**Usage:**
```python
from profile_lifecycle.warming_protocol import get_warming_schedule

schedule = get_warming_schedule({
    "profile_id": "P-001",
    "account_age_days": 10,
    "current_date": "2026-02-15",
    "target_connection_count": 150
})
```

**Returns:**
```json
{
  "profile_id": "P-001",
  "warming_phase": "Week1",
  "warming_week": 1,
  "daily_targets": {
    "profile_views": 5,
    "profile_view_responses": 2,
    "connection_requests": 3,
    "reactions": 2,
    "group_joins": 1,
    "browse_time_minutes": 5
  },
  "milestones": {
    "week_1_complete": "50 connections + 10 reactions + brand present",
    "week_2_complete": "100 connections + basic engagement history",
    "week_3_complete": "150 connections + visible skill endorsements",
    "month_3_complete": "ready_for_tier_b_transition"
  },
  "next_phase_date": "2026-02-22",
  "timestamp": "2026-02-15T00:00:00Z"
}
```

**Warming phases:**
- **Week 1-2 (Foundation):** Establish presence, light activity, build initial network
- **Week 3-4 (Trust building):** Increase engagement, industry participation, skill visibility
- **Month 2-3 (Presence):** Consistent activity, thought leadership, community participation
- **Month 4-6 (Maturation):** Ready for Tier B, can handle 1-2 applications per week

**Milestones:** Connection count targets, engagement history, skill endorsements, account maturity signals.

**Logging:** Warming progress tracked in profile's memory file with weekly completion status.

---

### repositioning_engine.py

**Purpose:** Manage gradual, safe profile repositioning (headline, summary, skills, experience).

**Usage:**
```python
from profile_lifecycle.repositioning_engine import plan_repositioning

plan = plan_repositioning({
    "profile_id": "P-001",
    "current_positioning": {
        "headline": "Java Developer",
        "summary": "...",
        "top_skills": ["Java", "Spring", "SQL"]
    },
    "target_positioning": {
        "headline": "Senior Java/Cloud Architect",
        "summary": "...",
        "top_skills": ["Java", "Spring", "AWS", "Kubernetes"]
    },
    "last_major_repositioning_date": "2025-12-15",
    "current_date": "2026-02-15"
})
```

**Returns:**
```json
{
  "status": "ALLOWED",
  "profile_id": "P-001",
  "repositioning_plan": [
    {
      "day": 1,
      "date": "2026-02-15",
      "changes": ["headline"],
      "details": "Update headline to 'Senior Java/Cloud Architect'",
      "expected_disruption": "low"
    },
    {
      "day": 2,
      "date": "2026-02-16",
      "changes": ["summary"],
      "details": "Expand summary with cloud architecture focus",
      "expected_disruption": "low"
    },
    {
      "day": 3,
      "date": "2026-02-17",
      "changes": ["skills_reorder"],
      "details": "Promote AWS and Kubernetes to top 5",
      "expected_disruption": "low"
    },
    {
      "day": 4,
      "date": "2026-02-18",
      "changes": ["featured_section"],
      "details": "Add cloud architecture projects",
      "expected_disruption": "low"
    },
    {
      "day": 5,
      "date": "2026-02-19",
      "changes": ["experience_bullets"],
      "details": "Update recent role bullets with cloud focus",
      "expected_disruption": "low"
    }
  ],
  "total_duration_days": 5,
  "ready_for_applications": "2026-02-20",
  "timestamp": "2026-02-15T12:00:00Z"
}
```

**Repositioning rules:**
- Max 1 major repositioning per month per profile
- Gradual changes only (spread over 5-7 days)
- Major section per day (headline → summary → skills → featured → experience)
- No overnight drastic changes
- Account age minimum 14 days before first repositioning

**Validation:**
- If last repositioning <30 days ago: BLOCKED (return days until next allowed)
- If account age <14 days: BLOCKED (wait for maturation)
- If profile in RED health: BLOCKED (stabilize first)
- Otherwise: ALLOWED (return 5-7 day plan)

**Logging:** Every repositioning plan appended with status, dates, approval/block reason.

---

## External Tools (To Be Integrated)

### Ads Power Browser
- Profile state inspection
- Activity simulation (clicks, fills, submissions)
- Screenshot capture for audit trail
- Session isolation per profile

### Zproxy
- IP allocation per profile per day
- IP reputation checks (must be >70%)
- Rotation management
- Geographic targeting

## Logging & Audit Trail

All skills append to JSONL logs in `/memory/`:
- `scoring_log.jsonl` - Every health calculation
- Activity simulation logs per date
- `inbound-history.jsonl` - Every classified message
- `application-history.jsonl` - Every application with screenshot reference
- `connection-database.jsonl` - Every connection request
- Ban/incident logs in `ban-incident-log.md`

All calculations are reproducible. All decisions traceable. All actions auditable.
