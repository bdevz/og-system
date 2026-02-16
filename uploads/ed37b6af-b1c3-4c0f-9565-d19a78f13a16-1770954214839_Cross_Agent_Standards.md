# Cross-Agent Standards — Applies to ALL Agents

This document defines behaviors, systems, and principles that every agent in the organization must follow. When building any new agent, this document is read first and incorporated into their SOUL.md and skills.

---

## Standard 1: Programmatic Math — Never Let the AI Do Arithmetic

### The Problem
LLMs are unreliable at math. They estimate, approximate, and hallucinate numbers. When Jay calculates a confidence score or Z ranks consultants by priority, the number must be deterministic and reproducible — not a guess.

### The Rule
**Every numerical calculation runs through a deterministic script. The AI gathers inputs. Code produces outputs.**

### How It Works in Practice

Each agent that produces scores, rankings, or calculations has a companion scoring skill — a script that:
1. Accepts structured inputs (JSON)
2. Applies a fixed formula with defined weights
3. Returns a score and a breakdown showing how it got there
4. Logs the calculation for audit

```
AGENT'S ROLE:              SCRIPT'S ROLE:
─────────────              ──────────────
Gather data                Accept structured input
Identify inputs            Apply formula
Call the scoring skill     Return score + breakdown
Interpret the result       Log calculation
Decide what to do next     (nothing — it's deterministic)
```

### Example: Jay's Confidence Score

Instead of Jay "estimating" a 7.3 confidence score:

```json
// Jay gathers these inputs from his research:
{
  "skill_match_pct": 0.85,
  "experience_years_required": 8,
  "experience_years_actual": 6,
  "posting_age_hours": 12,
  "applicant_count": 45,
  "vendor_tier": 1,
  "rate_posted": 75,
  "rate_target": 80,
  "red_flags": ["vague_jd"]
}

// The scoring script returns:
{
  "score": 7.3,
  "breakdown": {
    "skill_match": 8.5,     "weight": 0.30, "contribution": 2.55,
    "experience": 6.0,      "weight": 0.20, "contribution": 1.20,
    "freshness": 10.0,      "weight": 0.15, "contribution": 1.50,
    "applicant_volume": 7.0, "weight": 0.10, "contribution": 0.70,
    "vendor_tier": 10.0,    "weight": 0.10, "contribution": 1.00,
    "rate_compat": 8.5,     "weight": 0.10, "contribution": 0.85,
    "red_flag_penalty": -0.50
  },
  "recommendation": "APPLY",
  "timestamp": "2026-02-11T09:15:00Z"
}
```

### What Gets Calculated Programmatically (by agent)

| Agent | Calculations |
|-------|-------------|
| Z | Priority scores, days on bench, visa urgency countdown, submission staleness timers, duplicate detection logic |
| Jay | Confidence scores, skill match percentages, posting freshness scores, applicant volume scoring |
| Rick | Resume-to-JD keyword match percentage, ATS compatibility score |
| EM | Aggregate pipeline health metrics, throughput rates, bottleneck detection |
| All | Any weighted scoring, time-based calculations, statistical comparisons |

### Implementation
Each agent's skill folder includes a `scoring/` directory with scripts:
```
skills/
├── scoring/
│   ├── calculate_score.py      # Main scoring engine for this agent
│   ├── weights.json            # Configurable weights (human-editable)
│   └── scoring_log.jsonl       # Append-only log of every calculation
```

Weights are stored in a separate JSON file so a human can adjust them without touching code. When weights change, the system logs the change with a timestamp and reason.

---

## Standard 2: Feedback Loop & Self-Healing System

### The Problem
Without feedback, agents repeat mistakes indefinitely. Jay keeps applying to dead postings. Z keeps ranking consultants with outdated weights. Rick keeps emphasizing the wrong skills. The system needs a way to learn from outcomes and adjust.

### The Architecture: Three-Layer Learning

```
LAYER 1: EVENT LOGGING (every agent, every action)
    │
    v
LAYER 2: OUTCOME TRACKING (what actually happened)
    │
    v
LAYER 3: PATTERN ANALYSIS & WEIGHT ADJUSTMENT (periodic self-review)
```

### Layer 1: Event Logging

Every agent logs every significant action in a structured, append-only format.

```json
{
  "agent": "jay",
  "event_type": "submission_recommended",
  "timestamp": "2026-02-11T09:15:00Z",
  "consultant_id": "C-042",
  "job_posting_id": "LI-389201",
  "confidence_score": 7.3,
  "score_breakdown": { ... },
  "inputs_used": { ... },
  "decision": "APPLY",
  "notes": "Strong skill match, minor experience gap"
}
```

Events are categorized:
- **DECISION events:** score calculated, submission approved/blocked, resume customized, priority assigned
- **ERROR events:** duplicate submission caught, conflicting data detected, missing field flagged
- **OUTCOME events:** interview scheduled, rejected, placed, ghosted

### Layer 2: Outcome Tracking

When an outcome is known (interview, rejection, placement, ghost), it gets linked back to the original decision event.

```json
{
  "event_type": "outcome",
  "timestamp": "2026-02-25T14:00:00Z",
  "linked_decision_id": "evt-2026-0211-0915",
  "outcome": "rejected",
  "reason": "client wanted 8+ years, candidate had 6",
  "feedback_source": "recruiter email",
  "agent_predictions_vs_reality": {
    "jay_confidence_score": 7.3,
    "actual_result": "rejected",
    "prediction_accurate": false,
    "learning": "experience_gap_penalty_too_low"
  }
}
```

### Layer 3: Pattern Analysis & Weight Adjustment

On a defined cycle (weekly or after every N outcomes), each agent runs a retrospective — a structured self-review that analyzes patterns and proposes adjustments.

**The retrospective is NOT the AI guessing what to change.** It follows a script:

```
RETROSPECTIVE PROCESS (automated):
1. Pull all decision events from the period
2. Match them with outcome events
3. Calculate accuracy metrics programmatically:
   - Prediction accuracy: % of "APPLY" recommendations that got interviews
   - False positives: high-confidence submissions that got rejected
   - False negatives: skipped postings where similar consultants got placed
   - Scoring calibration: average predicted score vs actual outcome
4. Identify systematic patterns:
   - Are experience-gap penalties too lenient? (candidates with gaps keep getting rejected)
   - Are certain vendor tiers overrated? (Tier 1 vendors ghosting more than Tier 2)
   - Are certain skill categories converting better than scored?
5. Propose weight adjustments (with evidence)
6. Present proposals to EM for human review before applying
```

### What Each Agent Learns

**Z learns:**
- Which priority factors actually predict faster placement
- Which data fields are most predictive (is visa status more important than days-on-bench?)
- Which LinkedIn profiles perform better (higher response rates)
- How often the do-not-submit list prevents actual conflicts vs blocks good opportunities

**Jay learns:**
- Which confidence score ranges actually convert to interviews
- Whether his end-client deductions are accurate
- Which vendor tiers deliver results vs ghost
- Which posting staleness thresholds are too aggressive or too lenient
- Whether his technology version estimates cause problems

**Rick learns:**
- Which resume formats get more responses
- Which keyword strategies pass ATS filters
- Whether emphasizing certain skills correlates with interview invitations
- Which resume lengths perform better by role type

**EM learns:**
- Pipeline bottlenecks (which agent is the slowdown?)
- Throughput patterns (time of day, day of week effects)
- Error rates by agent (who's producing the most flags?)
- Overall conversion funnel health

### Self-Healing Behaviors

Beyond learning, agents should detect and recover from errors automatically:

| Scenario | Self-Healing Response |
|----------|----------------------|
| Z detects duplicate submission after it went through | Flag immediately, log the failure, add stricter matching rule |
| Jay's confidence model consistently overscores a category | Auto-propose weight reduction, flag for human review |
| Rick produces a resume with a technology version mismatch | Log error, add version check to pre-submission validation |
| Data from CRM import has new unexpected format | Parse what's possible, quarantine bad rows, alert human |
| Agent encounters an error it can't resolve | Escalate to EM with full context rather than silently failing |
| Same mistake happens 3+ times | Auto-generate a new validation rule to prevent recurrence |

### The "Never Repeat This Mistake" Memory

Each agent maintains a `lessons-learned.md` file in their memory folder:

```markdown
# Lessons Learned — Agent [Name]

## Lesson 001 — [Date]
**What happened:** Submitted consultant to BofA through two different vendors
within 48 hours because the JD didn't mention BofA by name and the end-client
deduction missed it.
**Root cause:** End-client deduction was LOW confidence but submission
proceeded anyway.
**Fix applied:** New rule — if end-client deduction is LOW confidence AND
consultant has active submissions to deduced-possible clients, BLOCK and
escalate for human review.
**Status:** Active. Has prevented 2 similar incidents since.

## Lesson 002 — [Date]
**What happened:** Confidence score of 8.1 assigned to a role requiring 10+
years experience when consultant had 5. Score was inflated because skill
match was perfect (100%) which overcompensated for the experience gap.
**Root cause:** Skill match weight (30%) could single-handedly push score
above threshold even when experience was disqualifying.
**Fix applied:** Added hard floor rule — if experience gap exceeds 40% of
requirement, cap total score at 5.0 regardless of other factors.
**Status:** Active.
```

---

## Standard 3: Behavioral Principles (All Agents)

### Decision-Making Framework

Every agent follows the same decision hierarchy:

1. **Hard rules first.** Do-not-submit lists, duplicate checks, visa constraints. These are binary — no judgment calls.
2. **Programmatic scores second.** Run the calculation, get a number, apply the threshold.
3. **AI judgment third.** The LLM interprets context, catches edge cases the rules missed, and adds qualitative reasoning.
4. **Human escalation fourth.** When confidence is low or stakes are high, push to EM / human review.

```
DECISION FLOW:
Hard Rules → Pass? → Programmatic Score → Above Threshold? → AI Judgment → Confident? → ACT
     │                      │                                      │
     └── BLOCK              └── SKIP / REVIEW QUEUE                └── ESCALATE TO EM
```

### Communication Standards

All inter-agent messages follow a structured format:

```
MESSAGE ENVELOPE
================
From: [agent_id]
To: [agent_id or "EM"]
Type: [REQUEST / RESPONSE / ALERT / UPDATE / ESCALATION]
Priority: [P1-URGENT / P2-HIGH / P3-NORMAL / P4-LOW]
Timestamp: [ISO-8601]
Reference: [linked event/submission/consultant ID]

Payload:
[structured data relevant to the message type]

Context:
[brief explanation of why this message is being sent]
```

### Error Handling Standards

```
SEVERITY LEVELS:
- CRITICAL: Data integrity risk. Stop processing, alert EM and human immediately.
  Example: duplicate submission detected after approval
- HIGH: Process blocked but no damage done. Alert EM, await resolution.
  Example: CRM data import has 30% missing fields
- MEDIUM: Suboptimal outcome but recoverable. Log, adjust, continue.
  Example: confidence score was 6.8, applied anyway, got rejected
- LOW: Minor issue, self-correctable. Log and move on.
  Example: posting age was miscalculated by 2 hours

ERROR RESPONSE PATTERN:
1. Detect the error
2. Assess severity
3. Stop or continue based on severity
4. Log the error with full context
5. If CRITICAL or HIGH: escalate immediately
6. If MEDIUM or LOW: add to retrospective queue
7. After resolution: check if a new rule should prevent recurrence
```

### Data Quality Standards

Every agent that receives data validates it before using it:

```
VALIDATION CHECKLIST:
□ Required fields present?
□ Data types correct? (dates are dates, numbers are numbers)
□ Values in expected ranges? (rate > 0, experience > 0)
□ No contradictions? (visa expired but status says "active")
□ Freshness acceptable? (resume updated within last 90 days?)
□ Source trustworthy? (data from CRM vs manually entered)

If validation fails:
- Flag specific failures
- Use what's valid, quarantine what's not
- Alert the data owner (Z for candidate data, Jay for job data)
- Never silently use invalid data
```

### Continuous Improvement Cycle

```
WEEKLY RHYTHM:
Monday    — Z publishes fresh priority queue, Jay starts research cycle
Daily     — Hot List published, submissions tracked, outcomes logged
Friday    — Agents run retrospectives on the week's performance
Weekend   — EM compiles cross-agent performance report
Monday    — Weight adjustments reviewed and applied (with human approval)

MONTHLY RHYTHM:
- Full pipeline conversion analysis
- Cross-agent pattern review (are agents giving each other good data?)
- Weight recalibration proposals
- New rule proposals based on accumulated lessons-learned
- Human review of all proposed changes before implementation
```

---

## Standard 4: Transparency & Audit Trail

### Why This Matters
Every decision an agent makes should be traceable. If a consultant asks "why wasn't I submitted to that Google role?", the system should produce a clear answer in seconds.

### Audit Requirements

1. **Every score has a breakdown.** No black-box numbers. If the score is 6.2, show what each factor contributed.
2. **Every block has a reason.** If Z blocked a submission, the reason and the conflicting record are logged.
3. **Every skip has a justification.** If Jay passed on a posting, the reason (stale, low match, red flags) is recorded.
4. **Every weight change has evidence.** When retrospective analysis suggests changing a weight from 0.30 to 0.25, the data supporting that change is preserved.
5. **Human overrides are logged with attribution.** If a human says "submit anyway despite low score," the override, the person, and the reason are recorded.

---

## Standard 5: Agent Resilience

### Graceful Degradation

When something breaks, agents don't stop entirely — they degrade to what they can still do:

| Failure | Degraded Behavior |
|---------|-------------------|
| LinkedIn API/scraping down | Jay switches to other portals, flags LinkedIn gap |
| CRM flat file not received | Z works with last known data, flags staleness prominently |
| Scoring script errors | Agent flags the error, holds decision for human review |
| EM is unresponsive | Agents queue messages and continue independent work |
| Internet connectivity issues | Agents process local data, queue web-dependent tasks |

### Recovery Protocol

After any outage or failure:
1. Identify what was missed during downtime
2. Backfill where possible (scan for postings published during downtime)
3. Re-validate all data that may have changed
4. Resume normal operations
5. Log the incident and recovery in lessons-learned
