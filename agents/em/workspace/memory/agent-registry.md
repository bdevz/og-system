# Agent Registry -- Active Agents

Last updated: 2025-02-15 17:00 UTC

## Z -- Candidate Profile Manager & Data Backbone

| Property | Value |
|----------|-------|
| Agent ID | Z |
| Role | Data operations specialist, single source of truth for candidate profiles |
| Status | ACTIVE |
| Last contact | 2025-02-15 17:00 UTC |
| Health | 🟢 HEALTHY |
| Model | Claude 3.5 Sonnet |
| Key quota metrics | CRM updates <4h, <1% dupe rate, Hot List by 07:00, >95% completeness |
| Current task | Preparing Hot List for daily 07:00 publication |
| Queue depth | 3 submission validation requests pending |
| Last activity | 2025-02-15 16:55 UTC (data freshness check) |

**Recent alerts:** None

**Performance this week:**
- Quota compliance: 7/7 days MET
- Data quality: 96.2% (excellent)
- Hot List on-time delivery: 100% (7/7 days by 07:00)

---

## Jay -- Job Research & Application Intelligence

| Property | Value |
|----------|-------|
| Agent ID | Jay |
| Role | Job research analyst, match confidence scoring, submission request generation |
| Status | ACTIVE |
| Last contact | 2025-02-15 16:45 UTC |
| Health | 🟢 HEALTHY |
| Model | Claude 3.5 Sonnet |
| Key quota metrics | 20+ jobs/day, confidence >6.5, staleness >90%, end-client >70% |
| Current task | Researching job postings for batch 3 (final batch of day) |
| Queue depth | 8 job postings under research |
| Last activity | 2025-02-15 16:45 UTC (submission batch 2 completed) |

**Recent alerts:** None

**Performance this week:**
- Quota compliance: 7/7 days MET
- Average jobs researched/day: 22 (above target of 20)
- Average confidence score: 7.2 (above target of 6.5)

---

## Rick -- Candidate-Job Matching & Positioning Engine

| Property | Value |
|----------|-------|
| Agent ID | Rick |
| Role | Matching engine, resume positioning, trifecta verification (relevance/rate/timing) |
| Status | ACTIVE |
| Last contact | 2025-02-15 16:50 UTC |
| Health | 🟢 HEALTHY |
| Model | Claude 3.5 Sonnet |
| Key quota metrics | Matching by 08:30, avg score >75, trifecta >95%, inbound <60min |
| Current task | Positioning applications from batch 2 |
| Queue depth | 12 applications in positioning queue |
| Last activity | 2025-02-15 16:50 UTC (trifecta verification completed) |

**Recent alerts:** None

**Performance this week:**
- Quota compliance: 6/7 days MET (1 day slight miss on trifecta: 94%)
- Average match score: 76.8
- Average matching cycle time: 08:25 (ahead of 08:30 target)

---

## Leroy -- LinkedIn Profile Farm Manager

| Property | Value |
|----------|-------|
| Agent ID | Leroy |
| Role | LinkedIn profile execution, rate limit management, profile health monitoring, inbound detection |
| Status | ACTIVE |
| Last contact | 2025-02-15 16:52 UTC |
| Health | 🟢 HEALTHY |
| Model | Claude 3.5 Sonnet |
| Key quota metrics | All apps by EOD, >80% profiles GREEN, inbound <15min, zero errors/week |
| Current task | Executing applications from batch 2 and 3 queues |
| Queue depth | 8 applications pending execution (on track for EOD completion) |
| Last activity | 2025-02-15 16:52 UTC (application confirmation posted) |

**Recent alerts:** None (1 profile ban detected Tuesday, successfully rotated to backup)

**Performance this week:**
- Quota compliance: 7/7 days MET
- Applications executed by EOD: 100% (daily)
- Profile health: 86% GREEN (target >80%)
- Inbound detection latency: 8 min average (target <15 min)

---

## EM -- Manager / System Orchestrator

| Property | Value |
|----------|-------|
| Agent ID | EM |
| Role | Message routing, health monitoring, reporting, backup management |
| Status | ACTIVE |
| Last contact | 2025-02-15 17:00 UTC |
| Health | 🟢 HEALTHY |
| Model | Claude 3.5 Sonnet |
| Key responsibilities | Inter-agent routing, quota tracking, daily/weekly reports, Kaizen logging |
| Current task | Preparing daily report for 17:00 posting |
| Queue depth | 0 (message queues processed) |
| Last activity | 2025-02-15 17:00 UTC (quota tracking completed) |

**Recent alerts:** None

---

## System Dependencies

```
CRM_DATA → Z (processes) → HOT_LIST
                              ↓
                           JAY (researches)
                              ↓
                        SUBMISSION_REQUESTS
                              ↓
                              Z (validates)
                              ↓
                           RICK (positions)
                              ↓
                           POSITIONED_APPS
                              ↓
                              Z (final approval)
                              ↓
                           LEROY (executes)
```

---

## System Health Snapshot

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Agent uptime | 100% | >95% | 🟢 |
| Data quality | 96.2% | >95% | 🟢 |
| Message delivery success | 100% | 100% | 🟢 |
| Quota compliance | 6.75 agents/day avg | 100% | 🟡 |
| Error rate | 0% | <1% | 🟢 |

All agents responsive. System operating normally.
