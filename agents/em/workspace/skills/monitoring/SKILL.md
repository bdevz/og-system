# Monitoring Skill -- Health, Quotas, and Alerts

## Purpose

Monitor the health and performance of all agents (Jay, Z, Rick, Leroy) continuously. EM is responsible for:

1. **Heartbeat polling:** Every 15 minutes, check if agents are alive and responsive
2. **Quota tracking:** Every day, calculate quota compliance and recommend interventions
3. **Alert generation:** Threshold-based alerts for critical events (profile bans, visa urgency, duplicate submissions, agent failures)

## Heartbeat Poller

Runs every 15 minutes during business hours (06:00-17:30 ET).

**Input:** Agent activity log (when agents last sent a message or completed a task)

**Output:** Health assessment for each agent

Agent states:
- **ACTIVE:** Last activity <15 min ago. Agent processing work normally.
- **IDLE:** Last activity 15-45 min ago. Normal (agent waiting for input or between batches).
- **BUSY:** Processing task >expected duration. Alert if >2x expected time.
- **SLOW:** Task taking longer than 2x expected baseline.
- **ERROR:** Last operation failed or agent returned error status.
- **DEAD:** No heartbeat >30 min. Trigger restart from backup immediately.

**Escalation logic:**
- SLOW >30 min: Investigate root cause, log warning, notify human if >1 hour
- ERROR: Attempt automated recovery (retry task, restart agent), alert human if persistent
- DEAD: Trigger restart from backup (attempt 3x), alert human immediately (CRITICAL)

## Quota Tracker

Runs daily at 17:00 (end of work day).

**Input:** Daily agent performance data (job count, confidence scores, response times, error counts)

**Output:** Quota compliance report + intervention recommendations

**Quotas:**

| Agent | Metric | Target | Baseline | Alert at |
|-------|--------|--------|----------|----------|
| Jay | Jobs researched/day | 20+ | 25 | <15 |
| Jay | Avg confidence score | >6.5 | 7.2 | <6.0 |
| Jay | Staleness detection | >90% | 95% | <85% |
| Jay | End-client deduction | >70% | 78% | <60% |
| Z | CRM updates latency | <4h | 2.5h | >3h |
| Z | Duplicate detection rate | <1% | 0.3% | >2% |
| Z | Hot List publication | By 07:00 | 06:45 | >07:15 |
| Z | Data completeness | >95% | 97% | <92% |
| Rick | Matching cycle completion | By 08:30 | 08:15 | >09:00 |
| Rick | Avg match score | >75 | 78.2 | <70 |
| Rick | Trifecta pass rate | >95% | 97% | <90% |
| Rick | Inbound lead response | <60 min | 35 min | >80 min |
| Leroy | Apps executed by EOD | 100% | 100% | <90% |
| Leroy | Profiles in GREEN state | >80% | 88% | <75% |
| Leroy | Inbound detection latency | <15 min | 8 min | >20 min |
| Leroy | Execution errors/week | 0 | 0.2 | >1 |

**Intervention ladder (4 levels):**

1. **OBSERVE (first miss):** Log the miss, no action. Example: "2025-02-15: Jay researched 18 jobs (target 20). Note: holiday impact."
2. **DIAGNOSE (2 consecutive misses or 3 in week):** Analyze root cause, prepare report, notify human. Example: "2025-02-15,16,17: Jay misses 3 days. Possible causes: insufficient job inventory, lower match confidence due to new skill mapping."
3. **INTERVENE (persistent problem):** EM proposes fix, human approves before execution. Example: "Propose increasing daily job search volume by 15%, human approves."
4. **REBUILD (fundamental failure):** EM proposes redesign and restores from backup if needed. Example: "Jay's matching algorithm has systematic bias. Propose reweight and retrain. Restore from clean baseline."

## Alert Generator

Generates threshold-based alerts for critical events.

**Alert severity levels:**

- **CRITICAL:** System safety or data integrity at risk. Immediate action required. Post to #alerts, notify human immediately.
- **HIGH:** Process blocked but no damage done. Post to #alerts, human should see same-day.
- **MEDIUM:** Suboptimal outcome but recoverable. Post to #em-dashboard, include in daily report.
- **LOW:** Minor issue, self-correctable. Log to memory only.

**Alert types:**

| Event | Trigger | Severity | Channel | Action |
|-------|---------|----------|---------|--------|
| Profile ban | Leroy detects ban | CRITICAL | #alerts | Rotate to backup profile, escalate |
| Visa expiring | <30 days remaining | HIGH | #alerts | Flag for priority, increase research |
| Duplicate submission | After approval detected | CRITICAL | #alerts | Data integrity breach, analyze |
| Agent DEAD | No heartbeat >30 min | CRITICAL | #alerts | Trigger restart, verify data |
| Agent SLOW | >30 min over baseline | MEDIUM | #em-dashboard | Investigate, adjust expectations |
| Data quality low | <90% completeness | MEDIUM | #em-dashboard | Trigger audit, flag for fixing |
| Quota miss | 2+ consecutive | HIGH | #alerts | Diagnose and report |
| CRM data stale | >4 hours old | HIGH | #alerts | Trigger import, notify human |

## Implementation

- **Heartbeat poller:** Polls every agent for last activity timestamp. Runs every 15 min.
- **Quota tracker:** Aggregates daily metrics. Compares to targets. Escalates misses. Runs at 17:00.
- **Alert generator:** Subscribed to events (profile ban, visa expiry, duplicate, agent status change). Fires alerts in real-time.
- **Logging:** All health checks, quota assessments, and alerts logged to system-history.jsonl with full context.

## Metrics EM tracks

- **Agent uptime:** % of time each agent is ACTIVE or IDLE (target >95%)
- **Quota compliance:** % of quotas met for each agent (target 100%)
- **Alert rate:** # alerts generated (target <5/day)
- **Recovery time:** Minutes to restore agent after DEAD state (target <10 min)
- **Data quality:** % of profiles >90% complete (target >95%)
