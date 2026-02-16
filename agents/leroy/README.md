# Agent Leroy - LinkedIn Profile Farm Manager & Inbound Intelligence

Leroy is a LinkedIn operations specialist managing a portfolio of 100+ LinkedIn profiles across four tiers (A, B, C, D), orchestrating applications, inbound lead routing, profile health management, and account warming with pharmaceutical-grade safety controls.

## Directory Structure

```
agents/leroy/
├── workspace/
│   ├── SOUL.md              # Leroy's mission, values, decision framework
│   ├── AGENTS.md            # Coordination with Z, Rick, EM
│   ├── USER.md              # Portfolio structure, constraints, infrastructure
│   ├── TOOLS.md             # Complete tool documentation
│   │
│   ├── skills/
│   │   ├── scoring/
│   │   │   ├── health_calculator.py       # Profile health scoring (0-100)
│   │   │   ├── health_weights.json        # Configurable weights and thresholds
│   │   │   ├── scoring_log.jsonl          # Audit trail of all calculations
│   │   │   └── SKILL.md                   # Complete documentation
│   │   │
│   │   ├── activity-simulator/
│   │   │   ├── schedule_generator.py      # Randomized daily activity schedules
│   │   │   ├── behavior_profiles.json     # Tier-specific behavior parameters
│   │   │   └── SKILL.md
│   │   │
│   │   ├── inbound-classifier/
│   │   │   ├── message_classifier.py      # Classify inbound leads A/B/C/D/E
│   │   │   ├── classifier_rules.json      # Classification rules and keyword lists
│   │   │   └── SKILL.md
│   │   │
│   │   ├── application-executor/
│   │   │   ├── linkedin_apply.py          # Execute applications with pre-flight checks
│   │   │   └── SKILL.md
│   │   │
│   │   ├── connection-manager/
│   │   │   ├── connection_strategy.py     # Connection targeting and execution
│   │   │   └── SKILL.md
│   │   │
│   │   └── profile-lifecycle/
│   │       ├── warming_protocol.py        # New profile warming schedules
│   │       ├── repositioning_engine.py    # Safe profile repositioning logic
│   │       └── SKILL.md
│   │
│   └── memory/
│       ├── profile-portfolio/     # Empty directory for portfolio data
│       ├── inbound-history.jsonl  # All classified inbound messages
│       ├── application-history.jsonl      # All applications submitted
│       ├── connection-database.jsonl      # All connection requests sent
│       ├── ban-incident-log.md   # Root cause analysis of restrictions
│       └── lessons-learned.md    # Operational insights and rule changes
│
├── agent/              # Agent implementation (placeholder)
└── sessions/           # Session logs (placeholder)
```

## Quick Start

### 1. Check Profile Health

```bash
cd workspace
python3 skills/scoring/health_calculator.py
```

Sample output: Profile health score (0-100) with GREEN/YELLOW/ORANGE/RED state.

### 2. Classify Inbound Message

```bash
python3 skills/inbound-classifier/message_classifier.py
```

Classifies message as A (HOT), B (WARM), C (NETWORKING), D (SPAM), or E (SUSPICIOUS).

### 3. Generate Activity Schedule

```bash
python3 skills/activity-simulator/schedule_generator.py
```

Random daily schedule respecting health state and tier constraints.

### 4. Execute Application

```bash
python3 skills/application-executor/linkedin_apply.py
```

Application with preflight checks, timing simulation, and Z approval reference.

## Core Concepts

### Health State System

Every profile has a health score (0-100) and state that determines activity level:

- **GREEN (85-100):** Full operations, tier default limits
- **YELLOW (60-84):** Reduced activity, max 2 applications/day
- **ORANGE (30-59):** Hydration only, zero applications
- **RED (0-29):** Quarantine, zero activity immediately

Health is calculated from 7 factors: account age, connections, daily apps, restriction history, activity diversity, session patterns, acceptance rate.

### Portfolio Tiers

- **Tier A (10-15):** Thoroughbred - 2-5 apps/day, diverse activity
- **Tier B (20-30):** Growth - 0-2 apps/day, moderate activity
- **Tier C (40-60):** Warming - 0-1 app per 3 days, light activity
- **Tier D (20-40):** Dormant - zero activity until ready

### Inbound Lead Classification

- **Class A (HOT):** Recruiter + specific role + Tier 1/2 firm → Rick in 15 min
- **Class B (WARM):** HR or recruiter with vague role → Rick in 2 hours
- **Class C (NETWORKING):** Generic connection, peers, alumni → Accept & log
- **Class D (SPAM):** Sales pitch, MLM, insurance → Ignore
- **Class E (SUSPICIOUS):** Trust & Safety, verification request → STOP & ALERT

### Application Safety

All applications require:
1. **Z Approval:** Submission gatekeeper confirms
2. **Health Check:** GREEN or YELLOW state
3. **Daily Limit:** Tier-specific max (A=5, B=2, C=1)
4. **Time Gap:** 5+ minutes since last application
5. **Proxy Valid:** IP not reused across profiles same day

### Profile Warming

New profiles go through structured warming (14-180 days):

- **Week 1-2:** Foundation - 50 connections, light engagement
- **Week 3-4:** Trust building - 100 connections, moderate engagement
- **Month 2-3:** Presence - 150 connections, consistent activity
- **Month 4-6:** Maturation - Ready for Tier B, can handle applications

### Safe Repositioning

Profile changes spread over 5-7 days, one section per day:

- Day 1: Headline (most visible)
- Day 2: Summary
- Day 3: Skills
- Day 4: Featured section
- Day 5: Experience

Constraints: Min 14 days account age, max 1 per 30 days.

## Key Rules

1. **Never exceed daily limits.** Hard stops at tier max, YELLOW cap at 2.
2. **Never change profiles overnight.** Always gradual, spread over days.
3. **Classify inbound leads within 15 minutes.** Class A gets immediate routing.
4. **Reduce activity when health drops.** No override, automatic state-driven limits.
5. **Quarantine restricted profiles immediately.** Zero activity, alert Z.
6. **Randomize all timing.** No two sessions look the same.
7. **Screenshot every application.** Audit trail proof.
8. **Coordinate with Z on applications.** Z is submission gatekeeper.
9. **Never reuse proxy IP same day.** One IP = one profile.
10. **When in doubt, ask EM.** Better safe than scraped.

## Integration with Multi-Agent System

**Z (Candidate Profile Manager):**
- Approves applications before Leroy executes
- Receives application confirmations with screenshots
- Alerts on portfolio health issues

**Rick (Resume Builder):**
- Provides application packages (resume, cover letter)
- Routes inbound leads to hiring managers
- Recommends repositioning strategies

**EM (Executive Manager):**
- Receives daily portfolio health reports
- Approves risky actions
- Makes strategic tier allocation decisions

## Operational Metrics

Daily monitoring includes:

- Portfolio health distribution (# GREEN/YELLOW/ORANGE/RED)
- Applications submitted (actual vs. target)
- Inbound leads classified and routed
- Connection requests sent and accepted
- Proxy IP reputation scores
- Any warnings or restrictions detected

## Error Handling

All errors classified by severity:

- **CRITICAL:** Stop immediately, alert human and Z (Trust & Safety, restrictions)
- **HIGH:** Reduce activity automatically, alert EM (health thresholds, rate limits)
- **MEDIUM:** Self-correct and log (timing variance, classification uncertainty)
- **LOW:** Log and continue (minor timing adjustments)

## Files Reference

### SOUL.md
Leroy's personality, mission, decision framework, and core rules.

### AGENTS.md
How Leroy coordinates with other agents (Z, Rick, EM).

### USER.md
Portfolio structure (tiers), constraints, infrastructure, metrics.

### TOOLS.md
Complete documentation of all 6 skills with input/output schemas.

### Health Calculator
`skills/scoring/health_calculator.py` - Core scoring algorithm. All other decisions based on this.

### Schedule Generator
`skills/activity-simulator/schedule_generator.py` - Daily activity randomization respecting health state.

### Message Classifier
`skills/inbound-classifier/message_classifier.py` - Instant classification of inbound opportunities.

### Application Executor
`skills/application-executor/linkedin_apply.py` - Safe application execution with pre-flight checks.

### Connection Manager
`skills/connection-manager/connection_strategy.py` - Connection targeting and request execution.

### Profile Lifecycle
`skills/profile-lifecycle/{warming_protocol,repositioning_engine}.py` - New profile warming and safe repositioning.

## Memory & Audit Trail

### Ban Incident Log
`memory/ban-incident-log.md` - Root cause analysis of every restriction or warning with recovery actions.

### Lessons Learned
`memory/lessons-learned.md` - Operational insights that led to rule changes.

### Application History
`memory/application-history.jsonl` - Every application with timestamp, Z approval, screenshot path.

### Connection Database
`memory/connection-database.jsonl` - Every connection request with target profile and note type.

### Inbound History
`memory/inbound-history.jsonl` - Every classified inbound message with routing decision.

## Future Enhancements

- Real Ads Power Browser integration (currently simulated)
- Machine learning on application success rates
- Reputation tracking per recruiter/firm
- Budget-aware targeting (prioritize high-value)
- Temporal pattern optimization (best times to apply)
- A/B testing of profile positioning variants
- Connection acceptance rate prediction
- Regional variation analysis

## Notes

All scripts are fully runnable with CLI demos:

```bash
python3 skills/scoring/health_calculator.py
python3 skills/inbound-classifier/message_classifier.py
python3 skills/application-executor/linkedin_apply.py
# ... etc
```

Each skill is independent and can be tested separately. Audit trails (JSONL logs) capture every calculation for reproducibility and compliance.
