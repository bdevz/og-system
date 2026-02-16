# Tools available to EM

## Message routing (Python scripts)

### message_router.py
- **Purpose:** Route messages between agents based on dependency graph and business rules.
- **Input:** Message envelope (from, to, type, priority, payload) + system state (agent states, quota data, queue status)
- **Output:** Routing decision (route immediately / hold pending input / escalate) with reasoning
- **Usage:** Called for every inter-agent message (roughly 100+ messages/day)
- **Routing rules config:** `routing_rules.json` contains dependency graph, priority rules, work schedule
- **Example:** Jay sends submission request → EM checks: is Z ready with recent data? Is Rick available? Route to Z first (conflict check), then to Rick (positioning). If Z data is >2h old, hold the message and alert human.

## System monitoring (Python scripts)

### heartbeat_poller.py
- **Purpose:** Poll agent health every 15 minutes during active hours (06:00-17:30).
- **Input:** Agent last-activity timestamps (from message log or direct check)
- **Output:** Health assessment for each agent + recommended action
- **Agent states:** ACTIVE (last activity <15min), IDLE (15-45min, normal), BUSY (>expected duration), SLOW (>2x expected), ERROR, DEAD (no heartbeat >30min)
- **Escalation logic:**
  - SLOW >30 min: investigate, log warning, notify human if >1 hour
  - ERROR: attempt automated recovery (retry, restart), alert human if persistent
  - DEAD: trigger restart from backup, alert human immediately (CRITICAL)
- **Usage:** Scheduled to run every 15 minutes during work hours. Results logged to memory.

### quota_tracker.py
- **Purpose:** Track agent performance against daily quotas and calculate intervention level.
- **Input:** Agent performance data for the period (from agent logs, message counts, execution timestamps)
- **Output:** Quota compliance report + intervention recommendations (4-level ladder)
- **Quotas tracked:**
  - Jay: 20+ jobs/day, confidence >6.5, staleness >90%, end-client deduction >70%
  - Z: CRM updates <4h, <1% dupe rate, Hot List by 07:00, >95% completeness
  - Rick: Matching cycle by 08:30, avg match >75, trifecta >95%, inbound <60min
  - Leroy: All apps by EOD, >80% profiles GREEN, inbound detection <15min, zero errors/week
- **Intervention ladder:**
  1. OBSERVE (first miss): log, no action
  2. DIAGNOSE (2 consecutive or 3 in week): analyze root cause, report to human
  3. INTERVENE (persistent): propose fix, human approves
  4. REBUILD (fundamental failure): propose redesign, restore from backup
- **Usage:** Run daily at 17:00 after work hours close, results posted to #em-dashboard.

### alert_generator.py
- **Purpose:** Generate threshold-based alerts from event data.
- **Input:** Event data (profile ban, visa expiry, duplicate detection, agent states, data quality metrics)
- **Output:** Alert with severity, target channel, recommended action
- **Alert thresholds:**
  - Profile ban → #alerts (CRITICAL, immediate action: rotate profile)
  - Visa expiring <30 days → #alerts (HIGH, flag for human review)
  - Duplicate submission detected after approval → #alerts (CRITICAL, data integrity breach)
  - Agent DEAD → #alerts (CRITICAL, immediate recovery needed)
  - Agent SLOW >30 min → #em-dashboard (MEDIUM, investigate)
  - Data quality <90% → #em-dashboard (MEDIUM, flag for audit)
- **Usage:** Integrated into heartbeat poller and quota tracker. Triggered on events.

## Reporting (Python scripts)

### daily_report.py
- **Purpose:** Generate the daily system report at 17:00.
- **Input:** Aggregated data from all agents (message logs, quota data, heartbeat data, alert counts)
- **Output:** Formatted report string ready for Slack posting
- **Report sections:**
  - Executive summary: Apps sent today, response rate, interviews booked, inbound leads, pipeline health
  - Per-agent performance: Jay research stats, Z data stats, Rick matching stats, Leroy ops stats
  - Alerts section: Any alerts generated today
  - Kaizen observation of the day
  - System health scorecard: Agent uptime, data quality, error rate
- **Usage:** Called daily at 17:00 via cron/scheduler. Output posted to #em-dashboard.

### weekly_retrospective.py
- **Purpose:** Compile weekly findings every Friday at 17:30.
- **Input:** Daily reports from the week, quota data, event logs, kaizen journal entries
- **Output:** Formatted weekly report string ready for Slack posting
- **Report sections:**
  - Conversion funnel: Jobs researched → matches → applications → responses → interviews → offers
  - Week-over-week comparisons: This week vs. last week for all key metrics
  - Per-agent performance summary: Weekly quota compliance, trends, wins
  - Top events of the week: Profile bans, visa urgencies, inbound surge, etc.
  - Retrospective findings from each agent: What worked, what didn't
  - Proposed weight/config adjustments (awaiting human approval): Recommendations from quota analysis
  - Kaizen log for the week: All daily observations compiled and categorized
- **Usage:** Called every Friday at 17:30. Output posted to #em-dashboard.

### dashboard_formatter.py
- **Purpose:** Format system data for Slack markdown posting.
- **Input:** Raw system state (agent states, metrics, alerts, queue depths)
- **Output:** Slack-formatted markdown strings ready for posting
- **Formatting templates:**
  - System dashboard: Agent status bars, pipeline numbers, portfolio health, active alerts
  - Agent performance cards: Per-agent quota compliance, recent alerts, trend indicators
  - Alert summary: Icon + severity + action
  - Metric scorecards: System health metrics with targets and current values
- **Usage:** Called by daily_report.py and weekly_retrospective.py to format output.

## Backup & recovery (Python scripts)

### backup_agent.py
- **Purpose:** Execute automated backups on schedule.
- **Input:** Backup configuration (backup_schedule.json) + files to back up (weights, memory files, agent snapshots)
- **Output:** Backup files in /backups directory + backup event log
- **Backup types:**
  - Daily (07:00): Scoring weights (from Z, Jay, Rick), memory files (agent registry, kaizen journal, lessons learned)
  - Weekly (Sunday 23:00): Full agent snapshots (SOUL.md, all skills, all memory for each agent)
  - On-change: When a scoring weight or rule is adjusted, immediately back up the changed config
- **Recovery mechanism:** When an agent fails, EM can restore from the most recent backup within minutes.
- **Usage:** Scheduled via cron. Also triggered manually if human requests via #human-commands.

### backup_schedule.json
- **Purpose:** Configuration file defining backup strategy.
- **Content:**
  - What to back up per agent: Which files/directories
  - Frequency: Daily, weekly, on-change
  - Retention policy: Keep last N backups
  - Backup location: /backups directory
- **Example structure:**
  ```json
  {
    "daily_backups": {
      "time": "07:00",
      "files": [
        "/agents/z/workspace/skills/scoring/priority_weights.json",
        "/agents/z/workspace/memory/"
      ],
      "retention_days": 30
    },
    "weekly_backups": {
      "day": "Sunday",
      "time": "23:00",
      "agents": ["z", "jay", "rick", "leroy"],
      "retention_weeks": 12
    }
  }
  ```

## Continuous improvement (Python scripts)

### improvement_tracker.py
- **Purpose:** Log and categorize daily Kaizen observations.
- **Input:** Observation (description, context, proposed action, evidence)
- **Output:** Structured entry in kaizen-journal.md with metadata
- **Kaizen categories:** PROCESS, QUALITY, SPEED, COST, RISK
- **Tracking:** Each observation has date, category, status (proposed/approved/implemented/rejected), evidence link
- **Usage:** Called daily at 17:45. Human approves improvements via #human-commands. Approved improvements implemented in next cycle.

## Memory files (append-only, human-editable)

### agent-registry.md
- Lists all 4 agents (Jay, Z, Rick, Leroy)
- For each: role, current state, quota targets, model assignments, last contact timestamp, health status
- Updated hourly by heartbeat poller
- Human reference for quick system understanding

### system-history.jsonl
- Append-only log of all major system events (agent restarts, quota misses, alerts, backups)
- One JSON object per line
- Queryable by timestamp, agent, event type
- Used for trend analysis and retrospectives

### quota-performance.jsonl
- Append-only log of daily quota compliance for each agent
- One line per agent per day
- Fields: date, agent, quota name, target, actual, status (met/miss/exceed)
- Used for trend analysis, intervention decisions

### kaizen-journal.md
- Daily Kaizen observations
- Format: date, category, observation, proposed_action, status, evidence_link
- Compiled weekly for retrospective
- Human can propose observations via #human-commands

### lessons-learned.md
- Template for recording system-wide lessons
- Updated when:
  - Major incident occurs (agent failure, data breach, etc.)
  - Week completes (Friday retrospective)
  - Important pattern identified (e.g., "every Tuesday afternoon quota dips")
- Structured as: date, lesson, impact, prevention

## Configuration files

### routing_rules.json
- **Purpose:** Encode all routing logic, dependency graph, and work schedule.
- **Content:**
  - Dependency graph: Which agent outputs feed which agent inputs
  - Priority rules: How to rank messages (URGENT > HIGH > NORMAL > LOW)
  - Batch rules: When to batch vs. send immediately (status messages batch, urgent messages immediate)
  - Work schedule: Times when agents are triggered (Z at 06:00, Jay at 07:15, etc.)
  - Hold conditions: When to hold a message (inputs not ready, agent SLOW, queue depth >threshold)
- **Example structure:**
  ```json
  {
    "version": "1.0",
    "dependency_graph": {
      "Z": {
        "inputs": ["CRM_DATA"],
        "outputs": ["HOT_LIST"],
        "start_time": "06:00",
        "deadline": "07:00"
      },
      "Jay": {
        "inputs": ["Z.HOT_LIST"],
        "outputs": ["SUBMISSION_REQUESTS"],
        "start_time": "07:15",
        "deadline": "16:00"
      }
    },
    "routing_rules": [
      {
        "from": "Jay",
        "to": "Z",
        "type": "SUBMISSION_REQUEST",
        "check": "Z has fresh data (age <4h)",
        "priority": "NORMAL",
        "action": "route"
      }
    ]
  }
  ```

## Slack integration (EM acts as Slack poster)

All Slack posts are generated by EM's reporting scripts and posted directly by EM. Channels:

- **#em-dashboard:** Daily reports, retrospectives, system status
- **#alerts:** CRITICAL and HIGH severity alerts
- **#agent-feed:** Inter-agent message audit trail
- **#kaizen:** Daily improvement observations
- **#inbound-leads:** Inbound lead tracking (Leroy reports, Rick responds)
- **#daily-hotlist:** Z's prioritized queue

EM does not expose raw agent logs or unformatted data to Slack. All posts are structured, scannable, and actionable.

## External integrations (future)

- **Supabase:** Persistent storage for consultant profiles, submission records, audit logs
- **Log1 CRM API:** Real-time data sync (currently CSV files only)
- **LinkedIn API:** Direct health monitoring and application tracking
- **Google Sheets:** Dashboard publishing for non-technical stakeholders
