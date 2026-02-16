# Agent Registry -- Who EM manages

## Jay (Job Research & Application Intelligence)
- **Role:** Deep research analyst for job postings. Researches each consultant match, calculates match scores, generates submission requests.
- **EM's relationship:** EM sends Jay the daily prioritized candidate queue from Z. Jay sends EM submission requests. EM routes requests to Z for conflict checking, then back to Rick for positioning, then to Leroy for execution.
- **Quota:** 20+ postings researched/day, avg confidence >6.5, staleness detection >90%, end-client deduction >70%
- **Input expectancy:** Z delivers prioritized queue by 07:15. Jay starts work immediately.
- **Output expectancy:** Submission requests to EM by 09:00 (batch 1), 12:00 (batch 2), 15:00 (batch 3).
- **Failure modes:** Slow research (quality checks too strict), inaccurate match scoring (outdated job data), missed staleness detection (old postings).
- **Auto-recovery triggers:** If Jay misses batch deadline by >30min, EM escalates to human with pending queue status.

## Z (Candidate Profile Manager & Data Backbone)
- **Role:** Single source of truth for all candidate data. Maintains flawless profiles, prevents duplicate submissions, enforces do-not-submit rules, publishes daily prioritized Hot List.
- **EM's relationship:** EM sends Z CRM updates (from external source). Z publishes Hot List. Z receives submission requests and sends conflict checks back through EM. EM monitors Z's quota and data quality.
- **Quota:** CRM updates within 4 hours, <1% duplicate rate, Hot List published by 07:00, >95% profile data completeness.
- **Input expectancy:** Fresh CRM data available (external). Z processes and publishes Hot List by 07:00.
- **Output expectancy:** Hot List to EM by 07:00. Submission approvals/blocks to EM same-day. Alerts on visa urgency, profile bans.
- **Failure modes:** Slow CRM processing (validation overhead), duplicate detection misses (stale history), incomplete profiles (missing visa/rate data).
- **Auto-recovery triggers:** If Z data quality drops <92%, EM triggers data audit. If Hot List misses 07:00 deadline by >15min, EM escalates.
- **Safety gate:** If Z is DEAD, EM pauses all application submissions (no data to validate against).

## Rick (Candidate-Job Matching & Positioning Engine)
- **Role:** Matching engine. Scores candidate-job fit, positions resumes, verifies trifecta (relevance, rate, timing), generates final submission packages.
- **EM's relationship:** EM routes Jay's submission requests to Rick. Rick returns positioned applications. EM routes those to Z for conflict final check, then to Leroy for execution.
- **Quota:** Matching cycle completed by 08:30, avg match score >75, trifecta pass rate >95%, inbound response <60 min.
- **Input expectancy:** Submission requests from EM by 09:30 (daily batch).
- **Output expectancy:** Positioned applications to EM by 11:00. Inbound lead responses to EM by 10:00 (next business day).
- **Failure modes:** Slow matching (too many candidate-job pairs), inaccurate scoring (outdated skill mapping), trifecta misses (rate or timing violations).
- **Auto-recovery triggers:** If Rick misses 08:30 matching cycle deadline by >15min, EM investigates queue backlog. If match quality drops <72%, EM escalates.

## Leroy (LinkedIn Profile Farm Manager)
- **Role:** Executes applications via LinkedIn. Manages 100+ profiles, respects profile rate limits, tracks profile health, detects profile bans/restrictions.
- **EM's relationship:** EM routes approved applications from Rick to Leroy. Leroy executes and sends confirmation screenshots. Leroy alerts EM of profile events (bans, restrictions).
- **Quota:** All approved applications executed by EOD, >80% profiles in GREEN state, inbound lead detection <15 min, zero execution errors/week.
- **Input expectancy:** Approved applications from EM (cumulative, not time-gated). Fresh profile list with health status from backup.
- **Output expectancy:** Application confirmations (with screenshots) to EM same-day. Inbound lead alerts to EM real-time. Daily profile health report to EM by 08:00.
- **Failure modes:** Profile bans (LinkedIn rate limiting), execution failures (browser crashes), missed inbound leads (detection lag).
- **Auto-recovery triggers:** If profile ban detected, EM logs event and rotates to backup profile. If execution failure, EM retries via backup. If inbound detection >25min, EM escalates.

## Inter-agent message format (standard envelope)

All messages between agents flow through EM. Standard format:

```
From: [agent_id]
To: [target_agent_id or "EM"]
Type: [REQUEST / RESPONSE / ALERT / UPDATE / ESCALATION]
Priority: [URGENT / HIGH / NORMAL / LOW]
Timestamp: [ISO-8601]
Reference: [linked event/submission/consultant ID]

Payload:
[structured data]

Context:
[brief explanation of business reason]
```

## Dependency graph (CRITICAL)

```
CRM_DATA_ARRIVES
  ↓
Z processes (GATE: CRM valid)
  ↓
Z publishes HOT_LIST by 07:00
  ↓
JAY receives HOT_LIST (GATE: Z published)
  ↓
JAY researches jobs + generates SUBMISSION_REQUESTS
  ↓
EM routes to RICK (GATE: JAY submitted)
  ↓
RICK positions + trifecta check → POSITIONED_APPS
  ↓
EM routes back to Z (GATE: RICK validated)
  ↓
Z final conflict check → APPROVED_APPS
  ↓
EM routes to LEROY (GATE: Z approved)
  ↓
LEROY executes → CONFIRMATIONS
  ↓
EM logs in submission tracker

INBOUND_LEADS arrive (any time)
  ↓
LEROY detects → alerts EM
  ↓
EM routes to RICK (<60 min priority)
  ↓
RICK positions → POSITIONED_LEAD
  ↓
EM routes to LEROY → execute
```

## Graceful degradation playbook

| Agent | State | Action |
|-------|-------|--------|
| Z | DEAD | PAUSE all applications. No data gate. Alert human. Restore from backup ASAP. |
| Jay | DEAD | Rick works with yesterday's research. Queue submission requests locally. Restore from backup. |
| Rick | DEAD | Applications approved but not positioned. Queue them. Once Rick is live, process queued batch. |
| Leroy | DEAD | Applications approved but not executed. Queue in submission tracker. Once Leroy is live, execute batch. |
| EM | DEAD | Agents have local message queues. Cannot route inter-agent messages. Human must manually intervene. Restore EM immediately. |

## State indicators EM monitors

- **ACTIVE:** Last activity <15 min ago. Agent processing work normally.
- **IDLE:** Last activity 15-45 min ago. Agent waiting for input or between batches. Normal.
- **BUSY:** Processing task >expected duration. Alert if >2x expected time.
- **SLOW:** Task taking longer than 2x expected baseline. Investigate root cause.
- **ERROR:** Last operation failed or agent returned error status. Attempt auto-recovery.
- **DEAD:** No heartbeat >30 min. Trigger restart from backup. Alert human.
