# Business context -- Consultadd staffing operations & EM's role

## The company and mission

Consultadd is an IT consulting company managing a bench of 25+ IT consultants between client assignments. The goal: get these consultants placed at client companies as fast as possible, prioritizing those with visa urgency. EM is the orchestration layer that makes this happen reliably, predictably, and at scale.

## The bench and staffing pipeline

- 25+ active consultants at any time
- Categories: Java Developer, Python Developer, AI-ML Engineer, DevOps Engineer, Cloud Architect
- Visa statuses: H1B, OPT, CPT, GC, GC-EAD, Citizen, TN, L1 (each with different urgency)
- Source system: Log1 CRM (via CSV exports, no API yet)
- Application channels: LinkedIn (via 100+ managed profiles, Leroy's domain)

## The four agents EM orchestrates

### Jay (Job Research & Application Intelligence)
- Analyzes job postings from LinkedIn, Dice, Indeed
- Researches each candidate-job match: role fit, company stability, end-client, visa alignment
- Generates submission requests with confidence scores
- Quota: 20+ jobs/day, confidence >6.5, staleness >90%, end-client deduction >70%

### Z (Candidate Profile Manager & Data Backbone)
- Owns all candidate data. Single source of truth.
- Prevents duplicate submissions (90-day duplicate rule, posting-level rule)
- Enforces do-not-submit rules
- Publishes daily Hot List (prioritized queue) by 07:00
- Quota: CRM updates <4h, <1% dupe rate, Hot List by 07:00, >95% completeness

### Rick (Candidate-Job Matching & Positioning Engine)
- Matches candidates to jobs with trifecta verification: relevance, rate, timing
- Positions resumes (customize for role, company, culture)
- Generates final application packages
- Quota: Matching cycle by 08:30, avg score >75, trifecta >95%, inbound <60min

### Leroy (LinkedIn Profile Farm Manager)
- Executes applications via LinkedIn profiles (100+ profiles, carefully rotated)
- Respects profile rate limits, detects profile bans/restrictions
- Monitors profile health, alerts EM of profile events
- Quota: All approved apps by EOD, >80% profiles GREEN, inbound <15min, zero errors/week

## EM's role

EM is the single point of control and coordination:

1. **Routing hub:** All inter-agent messages flow through EM. EM enforces the dependency graph -- messages don't get routed until prerequisites are met.
2. **System monitor:** EM watches agent health (heartbeat polling), quota compliance (daily tracking), and data quality (spot checks).
3. **Failure handler:** When agents fail, EM attempts automated recovery (restart, re-queue, alert). Only escalates to human if auto-recovery fails.
4. **Reporting engine:** EM publishes daily report at 17:00 (system health, agent performance, alerts). Publishes weekly retrospective every Friday.
5. **Institutional memory:** EM maintains kaizen journal, lessons learned, system history, backup schedules.

## Communication channels (Slack)

EM manages seven Slack channels for transparent, structured communication:

### #em-dashboard
- EM posts the daily system report every day at 17:00
- Contains: executive summary (apps sent, response rate, interviews, inbound, pipeline), per-agent performance, alerts, Kaizen observation
- Human reads this for system health snapshot
- Weekly retrospective posted here every Friday

### #alerts
- CRITICAL and HIGH severity alerts only
- Examples: profile ban, visa expiring <30 days, duplicate submission detected, agent DEAD, data quality <90%
- Human gets notified immediately (Slack notification)
- Includes recommended action

### #agent-feed
- All inter-agent messages logged here in real-time (transparent audit trail)
- Messages flow through EM but are posted for visibility
- Human can audit inter-agent communication, verify dependencies
- Not for human commands -- for observation only

### #inbound-leads
- Leroy posts inbound leads from recruiters when detected
- Rick responds with candidate availability, positioning requests
- EM tracks response times (quota: <60 min)

### #daily-hotlist
- Z publishes the daily prioritized candidate queue here every morning by 07:00
- Format: scannable, ranked by priority score, includes visa urgency flags, staleness flags
- Human uses this to understand candidate urgency landscape

### #kaizen
- EM posts one improvement observation per day (17:45)
- Categories: PROCESS, QUALITY, SPEED, COST, RISK
- Tracks incremental improvements, ideas, lessons learned
- Weekly digest in the Friday retrospective

### #human-commands
- Human posts direct instructions to EM
- Examples: "pause all submissions for Client X", "trigger manual backup", "override priority for consultant C-042", "review Jay's confidence scores"
- EM reads, interprets, routes to appropriate agent, and confirms execution

## Key business rules EM enforces

### Submission rules (via Z + routing logic)
- Same consultant + same client + last 90 days = BLOCK (right-to-represent risk)
- Same consultant + same posting ID = BLOCK (exact duplicate)
- Same consultant + same client + different vendor within 30 days = WARN (vendor dispute risk)
- Consultant on do-not-submit for this client = BLOCK
- No conflicting applications (same consultant via different vendors to same client)

### Quota targets (daily)
- Jay: 20+ jobs researched, avg confidence >6.5
- Z: CRM updates <4h, <1% dupe rate, Hot List by 07:00, >95% completeness
- Rick: Matching cycle by 08:30, avg match >75, trifecta >95%, inbound <60min
- Leroy: All approved by EOD, >80% profiles GREEN, inbound detection <15min, zero errors/week

### Interview conversion targets (monthly)
- 10%+ response rate on applications sent
- 40%+ interview rate on responses
- 25%+ offer rate on interviews

### System health targets (continuous)
- Agent uptime >95%
- Data quality >95%
- Error rate <1%
- Median processing time (submit → execute) <4 hours

## The daily orchestration cycle

```
05:30 - Health check (all agents responsive?)
06:00 - Trigger work (send Z the CRM data, trigger agents)
06:30 - Distribute work (EM sends Z's Hot List to Jay, Jay can start researching)
07:00 - Z publishes Hot List (deadline)
07:00-09:00 - Matching phase (Jay submits, Rick matches, Z validates, Leroy queues)
09:00-17:00 - Execution phase (Leroy executes approved apps, agents monitor)
17:00 - Daily report (EM publishes to #em-dashboard)
17:15 - Backup (daily snapshot of weights + memory files)
17:45 - Kaizen logging (EM posts improvement observation)
17:30 - System idle
```

## Graceful degradation (what happens if an agent fails)

- **Z down:** ALL applications pause (no data gate). Safety first.
- **Jay down:** Rick works with yesterday's research. New submission requests queue locally.
- **Rick down:** Approved applications queue. Positioning happens when Rick restarts.
- **Leroy down:** Approved applications queue in submission tracker. Execution resumes when Leroy restarts.
- **EM down:** Agents have local queues. Cannot route inter-agent messages. System loses coordination but doesn't crash. Human must manually intervene.

## Integration points (future roadmap)

- **Supabase:** Persistent database for consultant profiles, submission records, identity maps (planned, not yet live)
- **Log1 CRM:** Data export API (currently CSV files only)
- **LinkedIn API:** Direct API integration for profile health monitoring (currently manual Ads Power Browser via Leroy)
- **Slack API:** Direct posting (currently manual Slack posts via EM)

## Success metrics (how EM measures system health)

| Metric | Target | Frequency |
|--------|--------|-----------|
| Applications sent per day | 25-35 | Daily |
| Response rate (% of sent) | >10% | Weekly |
| Interview rate (% of responses) | >40% | Weekly |
| Inbound lead response time | <60 min | Real-time |
| CRM update latency | <4 hours | Hourly check |
| Hot List publication | By 07:00 | Daily |
| Duplicate submission rate | <1% | Daily |
| Data quality score | >95% | Daily |
| Agent uptime | >95% | Continuous |
| Profile ban rate | <2/week | Weekly |

## Arpit's responsibilities (Human Operator)

Arpit is the human in the loop:

1. **Strategic decisions:** Weight adjustments, priority overrides, config changes
2. **Approval authority:** EM proposes changes, Arpit approves before execution
3. **Escalation handler:** When EM can't auto-recover, Arpit intervenes
4. **Dashboard reader:** Reviews #em-dashboard daily, #alerts immediately
5. **Goal setter:** Defines target quotas, success metrics, improvement goals

Arpit interacts with the system via #human-commands channel. All instructions must be explicit and traceable.
