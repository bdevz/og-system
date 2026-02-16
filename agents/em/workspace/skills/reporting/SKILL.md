# Reporting Skill -- Daily Reports, Retrospectives, and Dashboard

## Purpose

Generate structured reports for human consumption:

1. **Daily report:** Published every day at 17:00 to #em-dashboard. System health snapshot.
2. **Weekly retrospective:** Published every Friday at 17:30 to #em-dashboard. Conversion funnel, WoW comparisons, findings, Kaizen log.
3. **Dashboard formatter:** Formats data for Slack markdown posting (agent status, metrics, alerts).

## Daily Report

**Trigger:** 17:00 every day

**Components:**

1. **Executive summary** (3-4 bullet points)
   - Applications sent today
   - Response rate (cumulative)
   - Interviews booked today
   - Inbound leads received

2. **Agent performance** (per-agent section)
   - Jay: Jobs researched, avg confidence, staleness, end-client deduction
   - Z: CRM update latency, dupe rate, Hot List publication time, completeness
   - Rick: Matching cycle time, avg match score, trifecta pass rate, inbound response
   - Leroy: Apps executed, profile health, inbound detection latency, execution errors

3. **Alerts section**
   - Any alerts from the day (critical/high only)

4. **System health scorecard**
   - Agent uptime (% ACTIVE/IDLE combined)
   - Data quality score
   - Error rate
   - Message volume

5. **Kaizen observation of the day**
   - Category, observation, proposed action

**Format:** Slack markdown with emojis and status bars

## Weekly Retrospective

**Trigger:** Friday 17:30

**Components:**

1. **Conversion funnel (WoW)**
   - Jobs researched (this week vs. last week)
   - Matches generated
   - Applications sent
   - Responses received
   - Interviews booked
   - Offers received
   - Conversion rates at each stage

2. **Per-agent performance (WoW)**
   - Each agent's key metrics compared to last week
   - Trends (up/down arrows)
   - Notable events

3. **Top events of the week**
   - Profile bans, visa urgencies, inbound surges
   - System incidents

4. **Retrospective findings**
   - What worked well? What didn't?
   - Blockers encountered
   - Dependencies that caused delays

5. **Proposed adjustments** (awaiting human approval)
   - Weight changes
   - Quota adjustments
   - Process improvements

6. **Kaizen digest for the week**
   - All daily observations compiled
   - Categorized by type (PROCESS, QUALITY, SPEED, COST, RISK)

## Dashboard Formatter

Formats system data for Slack markdown. Used by daily_report.py and weekly_retrospective.py.

**Templates:**

- Agent status bars: Shows ACTIVE/IDLE/BUSY/SLOW/ERROR/DEAD with visual indicator
- Metric scorecards: Target vs. actual with status (🟢 MET / 🟡 AT RISK / 🔴 MISS)
- Alert summary: Icon + severity + title + action
- Pipeline visualization: Numbers flowing through system stages

## Implementation

- **daily_report.py:** Runs at 17:00. Aggregates data from quotas, alerts, heartbeats. Formats and posts to Slack.
- **weekly_retrospective.py:** Runs Friday 17:30. Analyzes 7-day history. Compiles findings and Kaizen.
- **dashboard_formatter.py:** Helper functions for Slack markdown formatting.

All reports include:
- Timestamp
- Data freshness (when was this last calculated?)
- Confidence (based on data quality)
- Link to detailed logs for human investigation
