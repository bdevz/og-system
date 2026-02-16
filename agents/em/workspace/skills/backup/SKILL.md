# Backup Skill -- Automated Backup & Recovery

## Purpose

Execute automated backups on schedule to enable fast recovery if agents fail:

1. **Daily backup (07:00):** Scoring weights and memory files from all agents
2. **Weekly backup (Sunday 23:00):** Full agent snapshots (SOUL.md, skills, memory)
3. **On-change backup:** Triggered when scoring weights or rules are adjusted

## Backup types

### Daily backup
- **What:** Scoring weights (Z's priority_weights.json, etc.), memory files (agent registry, kaizen journal, lessons learned)
- **Where:** `/backups/daily/YYYY-MM-DD/`
- **When:** 07:00 every day
- **Retention:** Keep last 30 daily backups
- **Size:** Small (~100KB)

### Weekly backup
- **What:** Full agent snapshots for all agents (Z, Jay, Rick, Leroy)
  - SOUL.md (agent charter)
  - All skill directories with Python scripts
  - All memory files
- **Where:** `/backups/weekly/YYYY-Www/` (ISO week format)
- **When:** Sunday 23:00
- **Retention:** Keep last 12 weekly backups (3 months)
- **Size:** Medium (~5-10MB per backup)

### On-change backup
- **What:** Triggered immediately when scoring weights or system rules are changed (human approval required)
- **Where:** `/backups/on-change/YYYY-MM-DD-HHmmss/`
- **Retention:** Keep last 10 on-change backups
- **Purpose:** Audit trail of all config changes

## Recovery procedure

When an agent fails (state = DEAD):

1. EM triggers restart from most recent backup (daily or weekly)
2. Copy backup files to `/agents/[agent_id]/` overwriting current state
3. Restart agent process
4. Verify agent responds to heartbeat within 5 minutes
5. If recovery succeeds: log event, resume operations
6. If recovery fails: escalate to human with full diagnostic info

## Implementation

**backup_agent.py:**
- Reads `backup_schedule.json` to determine what/when/where to back up
- Executes backup (copy files to backup directory)
- Logs backup event to system-history.jsonl
- Manages retention (delete old backups exceeding retention policy)

**backup_schedule.json:**
- Configuration file with backup schedule and retention policies
- Human-editable (to adjust retention, frequency, scope)

## Backup verification

After each backup:
- Verify all files copied successfully (checksum comparison)
- Verify backup directory readable (no permission errors)
- Log backup completion timestamp and file count
- Alert human if backup fails

## Disaster recovery

If EM itself crashes:
1. Restart EM from most recent backup
2. EM reads message queue from persistent log
3. Resume message routing from where it left off
4. Agents should have local queues (message buffering) while EM is down

If multiple agents fail simultaneously:
1. Attempt to restart all from backup in parallel
2. Respect dependency graph (start Z first, then Jay/Rick, then Leroy)
3. Verify each agent before continuing pipeline
4. If critical agents don't recover, escalate to human immediately
