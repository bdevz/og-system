# Skill: Profile Health Scoring

## Purpose

Compute LinkedIn profile health score (0-100) and health state (GREEN/YELLOW/ORANGE/RED) based on account metrics. This is the core decision engine for activity level determination.

## What it does

- Accepts profile metrics (account age, connection count, daily app count, restriction history, activity diversity, session patterns, acceptance rate)
- Applies deterministic weighted scoring algorithm
- Returns health score, state classification, factor breakdown, and recommended actions
- Logs every calculation for audit trail and analysis

## Why it matters

Profile health determines operational constraints:
- GREEN (85-100): Full operations, no restrictions
- YELLOW (60-84): Reduced activity, max 2 apps/day
- ORANGE (30-59): Hydration only, no applications
- RED (0-29): Quarantine, zero activity

## How to use it

### Single profile health check

```python
from scoring.health_calculator import calculate_health

result = calculate_health({
    "profile_id": "P-001",
    "account_age_days": 180,
    "connection_count": 350,
    "daily_application_count": 2,
    "days_since_last_restriction": 45,
    "activity_diversity_score": 85,
    "session_pattern_regularity_score": 90,
    "connection_request_acceptance_rate": 75
})

print(f"Profile {result['profile_id']} health: {result['score']} ({result['state']})")
print(f"Recommended actions: {result['recommended_actions']}")
```

### Portfolio health snapshot

```python
from scoring.health_calculator import calculate_portfolio_health

portfolio = calculate_portfolio_health(profile_list)

print(f"Portfolio average health: {portfolio['average_health_score']}")
print(f"State distribution: {portfolio['state_distribution']}")
print(f"Critical actions needed: {portfolio['immediate_actions']}")
```

### CLI usage

```bash
# Demo with sample data
python health_calculator.py

# Single profile from JSON
python health_calculator.py profile_data.json

# Batch portfolio from JSON array
python health_calculator.py portfolio_list.json
```

## Input schema

```json
{
  "profile_id": "P-001",
  "account_age_days": 180,
  "connection_count": 350,
  "daily_application_count": 2,
  "days_since_last_restriction": 45,
  "activity_diversity_score": 85,
  "session_pattern_regularity_score": 90,
  "connection_request_acceptance_rate": 75
}
```

### Field descriptions

- **profile_id**: Unique identifier for the LinkedIn profile
- **account_age_days**: How many days since profile was created
- **connection_count**: Total number of 1st-degree connections
- **daily_application_count**: How many LinkedIn applications submitted today
- **days_since_last_restriction**: Days since last LinkedIn warning/restriction (-1 if never restricted)
- **activity_diversity_score**: 0-100, measure of activity variety (applications, connections, reactions, views, etc.)
- **session_pattern_regularity_score**: 0-100, how human-like are login/activity patterns (higher = more random, more human)
- **connection_request_acceptance_rate**: 0-100, % of sent connection requests that are accepted

## Output schema

```json
{
  "profile_id": "P-001",
  "score": 78,
  "state": "YELLOW",
  "state_definition": {...},
  "breakdown": {
    "account_age": { "raw_score": 100, "weight": 0.15, "contribution": 15 },
    "connection_count": { "raw_score": 100, "weight": 0.15, "contribution": 15 },
    ...
  },
  "recommended_actions": ["reduce_daily_applications_to_2"],
  "weights_version": "1.0.0",
  "next_check": "2026-02-16T12:00:00Z",
  "timestamp": "2026-02-15T12:00:00Z"
}
```

## Weight configuration

Weights are defined in `health_weights.json` and are human-editable. Current weights:

- Account age: 15%
- Connection count: 15%
- Daily application count: 20% (highest sensitivity to over-activity)
- Days since last restriction: 15%
- Activity diversity: 15%
- Session pattern regularity: 10%
- Connection request acceptance rate: 10%

To adjust weights, edit `health_weights.json`. All future calculations will use the new weights.

## Health state decision logic

### GREEN (85-100)
- Healthy account, no risk signals
- **Activity allowed:** Full tier operations (Tier A/B/C standard activity)
- **Applications:** Up to tier daily limit (A=5, B=2, C=1)
- **Action:** Continue normal operations
- **Monitor:** Weekly health checks

### YELLOW (60-84)
- Account showing stress indicators
- **Activity allowed:** Light activity, max 2 applications per day
- **Applications:** Forced to max 2/day regardless of tier
- **Action:** Reduce activity, increase session gaps
- **Monitor:** Daily health checks

### ORANGE (30-59)
- Account at risk, needs recovery
- **Activity allowed:** Hydration only (browsing, reactions, light engagement)
- **Applications:** ZERO applications
- **Action:** Stop all applications, hydration only
- **Monitor:** Twice daily health checks

### RED (0-29)
- Account compromised or severely restricted
- **Activity allowed:** ZERO activity
- **Applications:** ZERO applications
- **Action:** Immediate quarantine, alert human and Z
- **Monitor:** Continuous investigation

## State transitions

Automatic state transitions occur when:
1. Score crosses threshold (e.g., GREEN→YELLOW when score drops below 85)
2. Hard restrictions detected (e.g., ANY→RED when Trust & Safety alert)
3. Daily application limit exceeded (e.g., GREEN→YELLOW when daily apps hit 4+)

## Audit trail

Every health calculation is logged to `scoring_log.jsonl` with:
- Event type
- Timestamp
- Profile ID
- Score and state
- Full breakdown of all factors
- Weights version used

This allows:
- Replay of any calculation
- Trend analysis over time
- Debugging of state changes
- Compliance reporting

## Error handling

- Missing input: Returns error with missing field name
- Invalid profile_id: Still processes, logs with "UNKNOWN"
- Extreme values: Clamped to valid ranges, logged as anomaly
- File I/O errors: Raised with clear message

## Performance

- Single profile: <10ms
- Portfolio of 100: <500ms
- Batch logging: Append-only, <5ms per entry

## Integration points

- **Activity Scheduler**: Uses health state to determine activity volume
- **Application Executor**: Uses health state to determine if applications allowed
- **Daily Reporting**: Includes portfolio health snapshot
- **Risk Assessment**: Triggers escalation if many profiles RED
