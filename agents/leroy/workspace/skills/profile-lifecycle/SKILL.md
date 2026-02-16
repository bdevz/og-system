# Skill: Profile Lifecycle Manager

## Purpose

Manage the complete lifecycle of LinkedIn profiles from creation through warming to repositioning and maturation. This includes new account warming schedules and safe profile repositioning strategies.

## What it does

**warming_protocol.py:**
- Generates daily activity targets for new profiles (Tier C)
- Tracks warming phases (Week 1-4, Month 2-3, Month 4-6)
- Monitors progress against expected milestones
- Recommends next phases based on age and engagement

**repositioning_engine.py:**
- Plans safe profile repositioning over 5-7 days
- Validates that changes are gradual and natural
- Enforces safety constraints (14 days min age, 30 days between repositionings)
- Spreads changes across different profile sections

## Why it matters

New profiles need "break-in" time. Applying immediately gets flagged as spam. Gradual warming (connections, reactions, views) makes the profile look established and natural. Profile repositioning (headline, skills, summary) requires extreme care — LinkedIn detects sudden drastic changes and flags them as suspicious.

## How to use it

### Warming schedule

```python
from profile_lifecycle.warming_protocol import get_warming_schedule

schedule = get_warming_schedule({
    "profile_id": "P-001",
    "account_age_days": 10,
    "current_date": "2026-02-15",
    "target_connection_count": 150
})

print(f"Phase: {schedule['phase_name']}")
print(f"Daily targets: {schedule['daily_targets']}")
print(f"Ready for Tier B: {schedule['tier_b_readiness_date']}")
```

### Warming progress check

```python
from profile_lifecycle.warming_protocol import check_warming_progress

progress = check_warming_progress({
    "profile_id": "P-001",
    "account_age_days": 14,
    "current_connections": 45,
    "total_reactions": 9,
    "sessions_this_week": 7,
    "current_date": "2026-02-15"
})

if progress['warming_status'] == "ON_TRACK":
    print("Keep going!")
else:
    print(f"Issues: {progress['recommendations']}")
```

### Repositioning plan

```python
from profile_lifecycle.repositioning_engine import plan_repositioning

plan = plan_repositioning({
    "profile_id": "P-001",
    "current_positioning": {"headline": "Java Developer", ...},
    "target_positioning": {"headline": "Senior Java/Cloud Architect", ...},
    "last_major_repositioning_date": "2025-12-15",
    "current_date": "2026-02-15"
})

if plan['status'] == "ALLOWED":
    for day in plan['repositioning_plan']:
        print(f"Day {day['day']}: Update {day['changes']}")
else:
    print(f"Blocked: {plan['reason']}")
```

## Warming phases

### Week 1: Foundation (Days 1-14)
**Focus:** Establish presence, light activity, initial network

**Daily targets:**
- Profile views: 5
- Profile view responses: 2
- Connection requests: 3
- Reactions: 2
- Group joins: 1
- Browse time: 5 minutes
- Applications: 0

**Expected outcomes:**
- 50 connections
- 10 reactions
- Profile viewed by several users
- Presence established

**Milestones:**
- 50 connections reached
- Basic engagement history visible
- Account looks like legitimate user

---

### Week 3: Trust Building (Days 15-28)
**Focus:** Increase engagement, industry participation, skill visibility

**Daily targets:**
- Profile views: 8
- Profile view responses: 3
- Connection requests: 5
- Reactions: 3
- Comments: 1
- Browse time: 8 minutes
- Applications: 0

**Expected outcomes:**
- Additional 50 connections (100 total)
- More visible engagement
- Skill recommendations starting

---

### Month 2-3: Presence Building (Days 29-90)
**Focus:** Consistent activity, thought leadership, community participation

**Daily targets:**
- Profile views: 10
- Profile view responses: 4
- Connection requests: 6
- Reactions: 4
- Comments: 2
- Group activity: 1
- Browse time: 10 minutes
- Applications: 0 (still)

**Expected outcomes:**
- Additional 50 connections (150 total)
- Visible activity pattern
- Profile starting to look mature

---

### Month 4-6: Maturation (Days 91-180)
**Focus:** Ready for application acceleration

**Daily targets:**
- Profile views: 8
- Profile view responses: 3
- Connection requests: 5
- Reactions: 3
- Comments: 1
- Group activity: 1
- Browse time: 8 minutes
- Applications: 1 (ready to scale)

**Outcome:** Profile ready to move to Tier B, can handle 2-5 applications per week

## Repositioning strategy

### Safety constraints

1. **Account age minimum: 14 days**
   - New accounts can't be repositioned immediately
   - Protects against artificial profiles

2. **Time between repositionings: 30 days**
   - Max 1 major repositioning per month
   - Prevents drastic, suspicious changes

3. **Spread changes over 5-7 days**
   - One section per day
   - Appears gradual and natural

### Repositioning sequence

**Day 1: Headline update**
- Most visible change
- People notice immediately
- Get it done first when attention is fresh

**Day 2: Summary/About section**
- Less jarring than headline
- Appears as natural refinement
- Shows evolution of thinking

**Day 3: Skills reordering**
- Lowest-risk change
- Normal professional progression
- Doesn't look suspicious

**Day 4: Featured section**
- Add projects, accomplishments
- Can change without profile alert
- Demonstrates current focus

**Day 5: Experience bullets**
- Refine recent role descriptions
- Emphasize new skill areas
- Looks like natural reflection

### Validation of changes

Changes are validated for "drastic-ness":

**LOW RISK:** Headline change, skills reordering, summary expansion
**MEDIUM RISK:** Multiple sections changed, significant skill additions
**HIGH RISK:** Complete profile overhaul, many removed skills, conflicting changes

If validation shows HIGH risk, reduce scope and spread over longer period.

## Input/Output schemas

### Warming schedule

**Input:**
```json
{
  "profile_id": "P-001",
  "account_age_days": 10,
  "current_date": "2026-02-15",
  "target_connection_count": 150
}
```

**Output:**
```json
{
  "profile_id": "P-001",
  "warming_phase": "Week1",
  "phase_name": "Foundation",
  "warming_week": 2,
  "account_age_days": 10,
  "daily_targets": {
    "profile_views": 5,
    "profile_view_responses": 2,
    "connection_requests": 3,
    "reactions": 2,
    "browse_time_minutes": 5,
    "applications": 0
  },
  "expected_connections_by_phase": {
    "week_1": 50,
    "week_2": 100,
    "month_1": 150,
    "ready_for_tier_b": 150
  },
  "next_phase_date": "2026-02-22"
}
```

### Repositioning plan

**Input:**
```json
{
  "profile_id": "P-001",
  "current_positioning": {
    "headline": "Java Developer",
    "summary": "...",
    "skills": ["Java", "Spring", "SQL"]
  },
  "target_positioning": {
    "headline": "Senior Java/Cloud Architect",
    "summary": "...",
    "skills": ["Java", "Spring", "AWS", "Kubernetes"]
  },
  "last_major_repositioning_date": "2025-12-15",
  "current_date": "2026-02-15"
}
```

**Output (ALLOWED):**
```json
{
  "status": "ALLOWED",
  "profile_id": "P-001",
  "repositioning_plan": [
    {
      "day": 1,
      "date": "2026-02-15",
      "changes": ["headline"],
      "details": "Update headline...",
      "expected_disruption": "low"
    },
    {
      "day": 2,
      "date": "2026-02-16",
      "changes": ["summary"],
      ...
    }
  ],
  "total_duration_days": 5,
  "ready_for_applications": "2026-02-20"
}
```

**Output (BLOCKED):**
```json
{
  "status": "BLOCKED",
  "reason": "Recent repositioning detected",
  "last_repositioning_date": "2026-02-10",
  "days_since": 5,
  "min_days_between": 30,
  "can_reposition_after": "2026-03-12"
}
```

## Performance

- Warming schedule: <10ms
- Progress check: <20ms
- Repositioning plan: <30ms
- Repositioning validation: <15ms

## Integration points

- **Activity Simulator:** Uses warming targets for daily schedules
- **Health Calculator:** Warming profiles typically GREEN in health
- **Application Executor:** Only applies after warming complete
- **Portfolio Manager:** Tracks warming progress across profiles
- **Connection Manager:** Uses warming daily targets for connection requests

## Metrics tracked

**Warming metrics:**
- Connections built per week
- Reactions/engagement per day
- Profile view acceptance rate
- Time to reach 150 connections
- Deviation from expected milestones

**Repositioning metrics:**
- Days between repositionings
- Change magnitude per repositioning
- Profile health impact post-repositioning
- Acceptance rate after repositioning

## Safety constraints enforced

1. Accounts <14 days old cannot be repositioned
2. Max 1 repositioning per 30 days
3. Changes spread over minimum 5 days
4. One major section per day
5. Validation checks for drastic changes
6. Account age tracks repositioning history

## Future enhancements

- A/B testing different warming sequences
- Optimal timing calculations (when to advance phases)
- Machine learning predictions for readiness
- Seasonal/temporal adjustments to warming
- Integration with skill recommendation system
- Profile similarity detection (avoid clones)
