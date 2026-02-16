# Skill: Activity Schedule Generator

## Purpose

Generate randomized daily LinkedIn activity schedules per profile per tier that simulate human-like behavior while maintaining operational constraints.

## What it does

- Accepts profile tier, date, health state
- Generates randomized session times, durations, and activity mix
- Respects tier-specific activity bounds and daily limits
- Applies health state constraints (RED = zero, YELLOW = capped apps)
- Returns structured daily schedule with timestamps and activity counts

## Why it matters

LinkedIn detects robotic patterns. Activity that looks mechanical gets flagged and restricted. By randomizing:
- Login times within windows (morning/afternoon/evening)
- Session durations and activity mixes
- Inter-session gaps
- Weekend/weekday variation

We maintain account health and avoid restrictions.

## How to use it

### Single profile schedule

```python
from activity_simulator.schedule_generator import generate_schedule

schedule = generate_schedule({
    "profile_id": "P-001",
    "tier": "A",
    "date": "2026-02-15",
    "health_state": "GREEN",
    "primary_timezone": "EST"
})

for session in schedule["schedule"]:
    print(f"Session {session['session']} at {session['login_time']}")
    for activity in session['activities']:
        print(f"  - {activity['activity']}: {activity.get('count', activity.get('duration'))}")
```

### Batch portfolio schedule

```python
from activity_simulator.schedule_generator import generate_batch_schedules

portfolio = [
    {"profile_id": "P-001", "tier": "A", "health_state": "GREEN", "primary_timezone": "EST"},
    {"profile_id": "P-002", "tier": "B", "health_state": "YELLOW", "primary_timezone": "CST"},
    {"profile_id": "P-003", "tier": "C", "health_state": "GREEN", "primary_timezone": "PST"}
]

schedules = generate_batch_schedules(portfolio, date="2026-02-15")

for schedule in schedules:
    print(f"{schedule['profile_id']}: {schedule['total_sessions']} sessions, {schedule['total_duration_minutes']} min")
```

### CLI usage

```bash
# Demo with sample profiles
python schedule_generator.py

# Single profile from JSON
python schedule_generator.py profile_schedule_input.json

# Batch from JSON array
python schedule_generator.py portfolio_schedules.json
```

## Input schema

```json
{
  "profile_id": "P-001",
  "tier": "A",
  "date": "2026-02-15",
  "health_state": "GREEN",
  "primary_timezone": "EST"
}
```

### Field descriptions

- **profile_id**: Unique identifier
- **tier**: A (thoroughbred), B (growth), C (warming), D (dormant)
- **date**: YYYY-MM-DD for the schedule
- **health_state**: GREEN, YELLOW, ORANGE, RED
- **primary_timezone**: EST, CST, PST, etc. (affects login window times)

## Output schema

```json
{
  "profile_id": "P-001",
  "date": "2026-02-15",
  "tier": "A",
  "health_state": "GREEN",
  "schedule": [
    {
      "session": 1,
      "login_time": "2026-02-15T08:15:30Z",
      "duration_minutes": 22,
      "activities": [
        { "activity": "browse", "duration": 8, "count": 1 },
        { "activity": "reactions", "count": 4 },
        { "activity": "profile_views", "count": 3 },
        { "activity": "connection_requests", "count": 2 },
        { "activity": "applications", "count": 2 }
      ]
    },
    {
      "session": 2,
      "login_time": "2026-02-15T13:45:15Z",
      "duration_minutes": 18,
      "activities": [...]
    }
  ],
  "total_sessions": 2,
  "total_duration_minutes": 40,
  "activities_summary": {
    "browse": 1,
    "reactions": 7,
    "profile_views": 6,
    "connection_requests": 5,
    "applications": 2
  },
  "timestamp": "2026-02-15T12:00:00Z"
}
```

## Tier specifications

### Tier A: Thoroughbred (Daily, 15-30 min)
- Sessions: 2 per day
- Duration: 15-30 min per session
- Activities: Diverse mix
  - Browse: 5-10 minutes per session
  - Reactions: 3-5 per session
  - Profile views: 3-5 per session
  - Comments: 0-1 per session
  - Connection requests: 2-5 per session
  - Applications: 1-3 per session
- Daily app target: 2-5
- Connection request limit: 20/day
- Use case: High-velocity applications, diverse engagement

### Tier B: Growth (Daily/Every Other, 10-20 min)
- Sessions: 1-2 per day
- Duration: 10-20 min per session
- Activities: Moderate mix
  - Browse: 5-7 minutes per session
  - Reactions: 2-3 per session
  - Profile views: 2-3 per session
  - Comments: None
  - Connection requests: 3-8 per session
  - Applications: 0-1 per session
- Daily app target: 0-2
- Connection request limit: 15/day
- Use case: Growing pipeline, connection building

### Tier C: Warming (Every 2-3 Days, 5-10 min)
- Sessions: 1 per day (but skipped 40% of days)
- Duration: 5-10 min per session
- Activities: Light mix
  - Browse: 3-5 minutes per session
  - Reactions: 1-2 per session
  - Profile views: 3-5 per session
  - Comments: None
  - Connection requests: 3-5 per session
  - Applications: None
- Daily app target: 0
- Connection request limit: 8/day
- Use case: Account warming, trust building

### Tier D: Dormant (Zero Activity)
- Sessions: 0
- Activities: None
- Use case: Reserve capacity

## Health state constraints

### GREEN (85-100)
- Full activity as per tier specs
- Applications allowed at tier rate (Tier A 2-5, B 0-2, C 0)

### YELLOW (60-84)
- Activity allowed but capped
- Max 2 applications per day (override tier limit)
- Session gaps increased
- Activity diversity maintained

### ORANGE (30-59)
- Hydration only (browse, reactions, views)
- Zero applications
- Minimal connections
- Large session gaps

### RED (0-29)
- Zero activity
- No output, profile is quarantined

## Randomization

### Login times
- Randomized within tier-defined windows
- Morning: 7:30-9:30 (Tier A), 8:00-10:00 (Tier B), 9:00-11:00 (Tier C)
- Afternoon: 12:00-14:30 (Tier A), 13:00-15:00 (Tier B)
- Evening: 16:00-18:30 (Tier A)
- Variance: ±15 minutes from base window

### Session duration
- Random within tier bounds
- Variance: ±3 minutes

### Activity counts
- Random within tier bounds for each activity type
- Order randomized

### Inter-session gaps
- 2-5 hours between sessions
- Randomized per day

### Weekend behavior
- 50% probability of any activity
- If activity occurs, volume reduced 40-50%

## Human-like patterns

The generator applies patterns that make activity look human:

1. **Variable timing**: No two logins at exact same time
2. **Activity order randomization**: Activities occur in different sequences
3. **Occasional skips**: 10% chance to skip planned activities
4. **Session extension**: 5% chance to extend session if engaged
5. **Quick returns**: 20% chance to log back in within 1 hour
6. **Weekend reduction**: Weekends have 50% lower activity
7. **Vacation patterns**: Can schedule 1-week quiet periods

## Safety constraints

All schedules enforce hard limits:
- Max 6 applications per day (absolute LinkedIn limit)
- Max 20 connection requests per day
- Min 3 seconds between actions
- Max 2 consecutive sessions without 2-5 hour gap
- Required 2-5 hour gap between sessions

## Performance

- Single profile: <50ms
- Batch of 100: <5s
- Memory efficient, no database calls

## Integration points

- **Activity Executor**: Uses schedule to time actions
- **Connection Manager**: Uses connection request counts
- **Application Executor**: Uses application schedule
- **Portfolio Manager**: Plans daily activity mix

## Example output interpretation

Given this output:
```json
{
  "profile_id": "P-001",
  "tier": "A",
  "total_sessions": 2,
  "activities_summary": {
    "applications": 2,
    "connection_requests": 4,
    "reactions": 6,
    "profile_views": 5
  }
}
```

Instructions for executor:
1. Login at morning window time, session 1 (15-30 min)
   - Browse feed 5-10 min
   - React to 3-5 posts
   - View 3-5 profiles
   - Send 2-5 connection requests
   - Submit 1-3 applications
2. Wait 2-5 hours
3. Login at afternoon window time, session 2
   - Similar activity mix based on remaining budget
4. No evening session for Tier A this day (randomized)
