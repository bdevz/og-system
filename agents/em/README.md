# EM -- Manager / System Orchestrator

Complete agent workspace for the OG multi-agent recruitment system's operations manager.

## Quick Start

### Read First
1. **SOUL.md** -- EM's charter, mission, decision hierarchy, rules
2. **AGENTS.md** -- Who EM manages (Jay, Z, Rick, Leroy), their quotas, dependency graph
3. **USER.md** -- Business context, Slack channels, daily cycle
4. **TOOLS.md** -- All scripts and tools documentation

### Run Scripts
All scripts are standalone and runnable with `python script.py`:

```bash
# Message routing
cd workspace/skills/routing && python message_router.py

# Monitoring
cd workspace/skills/monitoring && python heartbeat_poller.py
cd workspace/skills/monitoring && python quota_tracker.py

# Alerting
cd workspace/skills/monitoring && python alert_generator.py

# Reporting
cd workspace/skills/reporting && python daily_report.py
cd workspace/skills/reporting && python weekly_retrospective.py

# Backup
cd workspace/skills/backup && python backup_agent.py daily

# Kaizen
cd workspace/skills/kaizen && python improvement_tracker.py
```

## Directory Structure

```
em/
├── workspace/                          # EM's operational workspace
│   ├── SOUL.md                        # EM's charter and decision rules
│   ├── AGENTS.md                      # Agent registry and dependencies
│   ├── USER.md                        # Business context
│   ├── TOOLS.md                       # All scripts documented
│   │
│   ├── skills/                        # Operational capabilities
│   │   ├── routing/
│   │   │   ├── SKILL.md
│   │   │   ├── message_router.py      # Route messages between agents
│   │   │   └── routing_rules.json     # Dependency graph + rules
│   │   │
│   │   ├── monitoring/
│   │   │   ├── SKILL.md
│   │   │   ├── heartbeat_poller.py    # Poll agent health every 15 min
│   │   │   ├── quota_tracker.py       # Track daily quotas + 4-level intervention
│   │   │   └── alert_generator.py     # Generate threshold-based alerts
│   │   │
│   │   ├── reporting/
│   │   │   ├── SKILL.md
│   │   │   ├── daily_report.py        # Daily report at 17:00
│   │   │   ├── weekly_retrospective.py # Friday retrospective at 17:30
│   │   │   └── dashboard_formatter.py # Slack markdown formatting
│   │   │
│   │   ├── backup/
│   │   │   ├── SKILL.md
│   │   │   ├── backup_agent.py        # Execute backups (daily, weekly, on-change)
│   │   │   └── backup_schedule.json   # Backup schedule config
│   │   │
│   │   └── kaizen/
│   │       ├── SKILL.md
│   │       └── improvement_tracker.py # Log daily improvements
│   │
│   └── memory/                        # Persistent state (append-only logs)
│       ├── agent-registry.md          # All 4 agents + health status
│       ├── system-history.jsonl       # Event log (events: health check, quota, backup, alert)
│       ├── quota-performance.jsonl    # Daily quota compliance per agent
│       ├── kaizen-journal.md          # Daily improvement observations
│       └── lessons-learned.md         # System insights and patterns
│
├── agent/                             # Agent execution directory (placeholder)
└── sessions/                          # Session logs (placeholder)
```

## Core Concepts

### EM's Responsibilities

1. **Message Routing:** All inter-agent communication flows through EM. EM enforces dependency graph, respects rate limits, escalates conflicts.

2. **Health Monitoring:** Heartbeat polling every 15 minutes. Detects SLOW/ERROR/DEAD states. Triggers automated recovery.

3. **Quota Tracking:** Daily compliance check. 4-level intervention ladder: OBSERVE → DIAGNOSE → INTERVENE → REBUILD.

4. **Alerting:** Threshold-based alerts for profile bans, visa urgency, duplicates, agent failures, data quality issues.

5. **Reporting:** Daily reports at 17:00, weekly retrospectives Friday at 17:30. System health snapshot + per-agent performance.

6. **Backup & Recovery:** Daily weights backup, weekly full snapshots, on-change backups. Enables fast recovery from agent failure.

7. **Continuous Improvement:** Kaizen logging. One observation per day. Tracks improvements over time.

### Agents Managed

| Agent | Role | Quota | Model |
|-------|------|-------|-------|
| Z | Data backbone | CRM <4h, <1% dupe, Hot List by 07:00, >95% complete | Claude 3.5 Sonnet |
| Jay | Research | 20+ jobs/day, confidence >6.5, staleness >90%, end-client >70% | Claude 3.5 Sonnet |
| Rick | Matching | By 08:30, score >75, trifecta >95%, inbound <60min | Claude 3.5 Sonnet |
| Leroy | Execution | All apps by EOD, >80% profiles GREEN, inbound <15min, 0 errors/week | Claude 3.5 Sonnet |

### Dependency Graph

```
CRM_DATA
  ↓
Z (validates)
  ↓
Hot List (by 07:00)
  ↓
Jay (researches)
  ↓
Submission Requests
  ↓
Z (conflict check)
  ↓
Rick (positions)
  ↓
Positioned Apps
  ↓
Z (final approval)
  ↓
Leroy (executes)
  ↓
Application Confirmations
```

### Slack Channels

- **#em-dashboard:** Daily reports, system status, weekly retrospectives
- **#alerts:** CRITICAL and HIGH severity alerts only
- **#agent-feed:** All inter-agent messages (transparent audit trail)
- **#kaizen:** Daily improvement observations
- **#inbound-leads:** Inbound lead tracking
- **#daily-hotlist:** Z's prioritized queue
- **#human-commands:** Human operator (Arpit) posts instructions

## Daily Orchestration Cycle

```
05:30 - Health check (all agents responsive?)
06:00 - Trigger work (send Z the CRM data, trigger agents)
06:30 - Distribute work (send Z's Hot List to Jay)
07:00 - Z publishes Hot List (deadline HARD)
07:15 - Jay starts research
09:00 - Jay submits batch 1
09:30 - Rick starts matching
12:00 - Jay submits batch 2
15:00 - Jay submits batch 3
17:00 - Publish daily report to #em-dashboard (deadline HARD)
17:15 - Execute daily backup
17:45 - Log Kaizen observation
23:00 (Sunday) - Execute weekly backup
```

## Key Design Patterns

### Message Routing
- Every message gets a routing decision: ROUTE / HOLD / ESCALATE / DROP
- Dependency graph enforced: Rick doesn't start until Jay AND Z are ready
- Priority-based: URGENT → route immediately, NORMAL → batch and route per deadline
- Logging: Every routing decision logged for audit trail

### 4-Level Intervention Ladder
1. **OBSERVE:** First quota miss. Log and continue.
2. **DIAGNOSE:** 2 consecutive or 3 in week. Analyze root cause, report to human.
3. **INTERVENE:** Persistent problem. Propose fix, human approves.
4. **REBUILD:** Fundamental failure. Propose redesign, restore from backup.

### Graceful Degradation
- Z down → PAUSE all submissions (no data gate)
- Jay down → Rick works with yesterday's research
- Rick down → Leroy executes approved apps with template positioning
- Leroy down → Apps queue in submission tracker
- EM down → Agents have local message queues

### Safety Gates
- Z is critical safety gate for data validation. If Z is DEAD/ERROR, no submissions routed.
- Duplicate submission detection happens at Z, not downstream.
- Profile bans are escalated CRITICAL, profile rotation is immediate.

## Metrics EM Tracks

### System-Level
- Applications sent/day (target 25-35)
- Response rate % (target >10%)
- Interview rate % (target >40%)
- Inbound detection latency (target <15 min)
- Data quality score % (target >95%)

### Per-Agent
- Agent uptime % (target >95%)
- Quota compliance % (target 100%)
- Task duration vs. baseline (target <2x baseline)
- Error rate per day (target <1%)

### Infrastructure
- Message routing latency (target <1 sec)
- Backup success rate (target 100%)
- Recovery time on agent failure (target <10 min)

## Implementation Notes

### All Python Scripts
- Standalone, runnable with `python script.py`
- Include demo data for testing
- Support CLI invocation for integration into scheduled jobs
- Log to memory files (append-only, JSONL format)
- No external dependencies (pure Python + stdlib)

### Configuration Files
- `routing_rules.json` -- Complete routing logic encoded
- `backup_schedule.json` -- Backup strategy and retention
- `quota_config.json` (referenced in quota_tracker.py) -- Quota definitions

### Memory Files (Append-Only)
- `system-history.jsonl` -- All major system events
- `quota-performance.jsonl` -- Daily quota compliance
- `kaizen-journal.md` -- Human-readable Kaizen log
- `agent-registry.md` -- Current agent status snapshot

## Testing & Validation

All scripts tested and working:

```bash
# Test routing
cd workspace/skills/routing && python message_router.py
# Output: Routing decision JSON for sample submission request

# Test monitoring
cd workspace/skills/monitoring && python heartbeat_poller.py
# Output: Health assessment for all 4 agents

# Test monitoring - quota
cd workspace/skills/monitoring && python quota_tracker.py
# Output: Daily compliance report

# Test monitoring - alerts
cd workspace/skills/monitoring && python alert_generator.py
# Output: Sample alerts in JSON format

# Test reporting - daily
cd workspace/skills/reporting && python daily_report.py
# Output: Daily report in Slack markdown format

# Test reporting - weekly
cd workspace/skills/reporting && python weekly_retrospective.py
# Output: Weekly retrospective in Slack markdown format

# Test backup
cd workspace/skills/backup && python backup_agent.py daily
# Output: Backup execution result

# Test kaizen
cd workspace/skills/kaizen && python improvement_tracker.py
# Output: Sample Kaizen observations logged
```

## Integration with OpenClaw

EM is the parent agent in OpenClaw. In production:

1. OpenClaw creates message envelope
2. OpenClaw routes to EM via `message_router.py`
3. EM routes to appropriate child agent (Z, Jay, Rick, Leroy)
4. Agent processes and responds
5. EM logs response and routes to next agent per dependency graph

## Human Operator Interface

Arpit (human operator) interacts via:

1. **#em-dashboard:** Reads daily reports and weekly retrospectives
2. **#alerts:** Monitors critical alerts, takes action
3. **#human-commands:** Posts instructions to EM (e.g., "pause submissions", "override priority", "approve weight change")
4. **#agent-feed:** Optionally audits inter-agent communication

## Deployment Considerations

- All scripts use absolute paths (cross-platform safe)
- Logging to persistent memory files enables recovery
- Backup/restore mechanism enables disaster recovery
- No external dependencies (pure Python, works anywhere)
- Designed for cloud or local deployment

## Next Steps / Roadmap

1. **Implement parallel processing:** Rick's trifecta checking (SPEED improvement)
2. **Proactive profile monitoring:** Alert at 85% cap, not at ban (QUALITY improvement)
3. **ML duplicate detection:** Predict duplicates before Z validation (SPEED + QUALITY)
4. **Supabase integration:** Replace file-based memory with persistent DB
5. **Full API integration:** CRM and LinkedIn API direct integration (remove manual steps)

---

*Built for the OG recruitment system at Consultadd. EM is the orchestration backbone that makes the multi-agent system reliable, observable, and continuously improving.*
