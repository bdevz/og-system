# Lessons Learned

This document records operational lessons learned from running the LinkedIn profile farm. These are insights that have led to rule changes, new procedures, or improved understanding of LinkedIn behavior.

## Format

Each lesson follows this template:

```
## LESSON: [Short title]

**Date Discovered:** YYYY-MM-DD
**Severity:** Critical | High | Medium | Low
**Category:** Health | Activity | Safety | Targeting | Timing

**Observation:**
[What we observed in the data/behavior]

**Initial Hypothesis:**
[What we thought was happening]

**Actual Root Cause:**
[What was really happening]

**Evidence:**
- [Data point 1]
- [Data point 2]

**Rule Change:**
- [What changed in the system]
- [Where change was implemented]

**Expected Impact:**
- [How this prevents recurrence]
- [Estimated impact on portfolio]

**Related Incidents:**
- [Incident ID if applicable]

---
```

## Active Lessons

### LESSON: Health State Must Drive Activity Limits Immediately

**Date Discovered:** 2026-02-15
**Severity:** High
**Category:** Health

**Observation:**
Profile in YELLOW health state (score 68) submitted 4 applications in one day. Within hours, received rate limit warning and was blocked from further applications.

**Initial Hypothesis:**
Rate limiting was just a natural throttle. We could let YELLOW profiles have some grace period before strictly enforcing the 2-app limit.

**Actual Root Cause:**
LinkedIn's algorithms track submissions in real-time. When a YELLOW-health profile (showing stress signals) submits applications at a rate meant for GREEN profiles, it immediately triggers rate limiting. Health state is not a suggestion—it's a signal of actual account stress that must be respected.

**Evidence:**
- YELLOW profile: 4 apps/day on 2026-02-15
- Rate limit warning received at 14:32 UTC (same day)
- Application submission blocked for 24 hours
- Similar pattern on other profiles: YELLOW + high app rate = warning

**Rule Change:**
- `schedule_generator.py`: YELLOW state now hardcaps applications to 2 per day in activity schedule
- `preflight_check()`: Added explicit block if daily_app_count >= 2 AND health_state == "YELLOW"
- `health_calculator.py`: Clarified state interpretation in documentation

**Expected Impact:**
- Reduce MEDIUM/HIGH incidents by ~30%
- No more YELLOW-state profiles exceeding 2 apps/day
- Better health state preservation

**Related Incidents:**
- INCIDENT: 2026-02-15 P-TEST-001 - Rate Limit Warning

---

## Completed Lessons

(None yet. This is the first operational lesson recorded.)

---

## Template for New Lessons

Use this when you discover a new insight:

```
## LESSON: [Title]

**Date Discovered:** [YYYY-MM-DD]
**Severity:** Critical | High | Medium | Low
**Category:** Health | Activity | Safety | Targeting | Timing | (other)

**Observation:**
[What you observed]

**Initial Hypothesis:**
[What you thought]

**Actual Root Cause:**
[What was really happening]

**Evidence:**
- [Data 1]
- [Data 2]

**Rule Change:**
- [What changed]
- [Where]

**Expected Impact:**
- [Positive outcomes]

**Related Incidents:**
- [If any]

---
```

## Lesson Categories

### Health Lessons
How account health works, what signals matter, how to interpret health state.

### Activity Lessons
How application rates, connection patterns, engagement behaviors affect account safety.

### Safety Lessons
LinkedIn's detection mechanisms, what triggers warnings, what indicates ban risk.

### Targeting Lessons
Which target types work best for which tiers, optimal targeting strategies.

### Timing Lessons
When to do activities, session patterns, gaps between actions.

### Tier Strategy Lessons
How each tier should operate differently, what works for new accounts vs. mature ones.

---

## Key Insights So Far

1. **Health state is real-time**: It's not just a historical metric. LinkedIn is actively evaluating stress signals minute-by-minute. Account health directly determines what activity level is safe.

2. **Rate limiting is intelligent**: LinkedIn doesn't just count submissions. It evaluates the pattern. A YELLOW-health profile submitting at GREEN rates triggers immediate warnings.

3. **Prevention > Recovery**: It's 10x easier to prevent an incident than recover from one. Better to be conservative with a profile than to hit a warning and have to spend 3+ days in recovery.

---

## Known Unknowns

Things we don't yet fully understand:

- [ ] Exact metrics LinkedIn uses for connection acceptance rate threshold
- [ ] How much activity is required to move from ORANGE back to YELLOW
- [ ] Optimal warm-up period for brand new profiles (14, 21, or 30 days?)
- [ ] Connection request rate limits per region/language
- [ ] Impact of profile view responses on overall health
- [ ] How LinkedIn weighs application success rate in health scoring

---

## Future Research Areas

### Priority 1: Application Success Rate
- How does LinkedIn track application success?
- Does it affect health scoring?
- Can failure rate trigger warnings?

### Priority 2: Regional Variations
- Do application limits vary by account location?
- Do messaging patterns matter differently by region?

### Priority 3: Temporal Patterns
- Are certain times of day better for applications?
- Do weekend patterns affect health?
- Holiday periods: do they matter?

---

## Rules Changed This Month

**From:** Health state is advisory, can be overridden
**To:** Health state determines hard activity limits

**Reason:** Observed rate limiting on YELLOW profiles when exceeding 2 apps/day

**Impact:** Expected 30% reduction in MEDIUM+ incidents

---

## Feedback Loop

When you make a rule change based on a lesson:

1. Document the change here
2. Update the affected script(s)
3. Monitor for 2+ weeks
4. Assess impact
5. Document results

Example:

```
**Change:** Reduced YELLOW app limit from 3 to 2
**Implemented:** 2026-02-15
**Monitoring Period:** 2026-02-15 to 2026-03-01
**Result:** [To be filled in with data]
**Status:** [Active | Successful | Needs Adjustment | Rolled Back]
```

---

## Communication

When a new lesson is learned:

1. Add to this document immediately
2. Update related SKILL.md files
3. Alert Z if it affects application strategy
4. Alert Rick if it affects resume/targeting
5. Alert EM if it affects portfolio health
6. Create preventive rules before next incident

---

## Historical Lessons Database

This section will accumulate lessons as we operate the portfolio over time. Each lesson represents a data point about how LinkedIn's algorithms and safety systems work. Over time, these lessons become the operational wisdom of Leroy.
