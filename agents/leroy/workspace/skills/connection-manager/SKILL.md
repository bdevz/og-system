# Skill: Connection Strategy Manager

## Purpose

Manage LinkedIn connection request targeting and execution per tier with intelligent note selection, daily limit enforcement, and human-like distribution patterns.

## What it does

- Gets connection targets for a profile filtered by tier and daily limit
- Executes connection requests with optional notes
- Applies tier-specific note strategies (70% no note, 20% generic, 10% personalized)
- Tracks note distribution and acceptance metrics
- Logs all requests for audit trail

## Why it matters

Connection requests build the foundation for future opportunities. But LinkedIn throttles connections if sent too fast or mechanically. By applying tier-specific targeting and note strategies, we build networks that look natural while respecting daily limits.

## How to use it

### Get connection targets for today

```python
from connection_manager.connection_strategy import get_connection_targets

targets = get_connection_targets({
    "profile_id": "P-001",
    "tier": "A",
    "date": "2026-02-15"
})

print(f"Available targets: {targets['targets_available']}")
print(f"Daily limit: {targets['daily_limit']}")
for target in targets['targets']:
    print(f"  - {target['name']} ({target['title']}) at {target['company']}")
```

### Execute single connection request

```python
from connection_manager.connection_strategy import execute_connection_request

result = execute_connection_request({
    "profile_id": "P-001",
    "target_id": "T-5678",
    "target_name": "Jane Recruiter",
    "target_title": "Senior Technical Recruiter",
    "target_company": "TechStaff Inc",
    "note": "Hi! I'd like to connect.",
    "proxy_ip": "192.0.2.15"
})

print(f"Connection request {result['request_id']} sent")
```

### Execute batch connections

```python
from connection_manager.connection_strategy import execute_batch_connections

batch = execute_batch_connections({
    "profile_id": "P-001",
    "tier": "A",
    "date": "2026-02-15",
    "targets": targets_list,
    "proxy_ip": "192.0.2.15"
})

print(f"Sent {batch['total_requests']} connection requests")
print(f"Notes: {batch['statistics']['note_distribution']}")
```

## Daily connection limits

| Tier | Daily Limit | Primary Target | Secondary Target |
|------|------------|-----------------|------------------|
| A | 20 | Tier 1 recruiters (40%) | Tier 2 recruiters (30%) |
| B | 15 | Tier 1 recruiters (35%) | Tier 2 recruiters (35%) |
| C | 8 | Open networkers (40%) | Alumni (30%) |
| D | 0 | None | None |

## Target distribution strategies

### Tier A (Thoroughbred)
**Focus:** High-quality recruiter and hiring manager targeting

| Category | Percentage | Target Profile |
|----------|-----------|-----------------|
| Tier 1 Recruiters | 40% | Senior Recruiter at major staffing firm |
| Tier 2 Recruiters | 30% | Recruiter at growth staffing firm |
| Hiring Managers | 20% | Engineering Manager at target client |
| Industry Peers | 10% | Senior developers, tech leads |

**Note Strategy:** 70% no note, 20% generic, 10% personalized

---

### Tier B (Growth)
**Focus:** Mixed recruiter and HR professional targeting

| Category | Percentage | Target Profile |
|----------|-----------|-----------------|
| Tier 1 Recruiters | 35% | Recruiter at major staffing firm |
| Tier 2 Recruiters | 35% | Recruiter at growth staffing firm |
| HR Professionals | 20% | HR Manager, Talent Acquisition |
| Industry Peers | 10% | Developers, fellow engineers |

**Note Strategy:** 70% no note, 25% generic, 5% personalized

---

### Tier C (Warming)
**Focus:** Network building with low-pressure approach

| Category | Percentage | Target Profile |
|----------|-----------|-----------------|
| Open Networkers | 40% | Freelancers, contractors, connectors |
| Alumni | 30% | Graduates from same school/program |
| Group Members | 20% | Members of relevant LinkedIn groups |
| Industry Peers | 10% | Peers in target industries |

**Note Strategy:** 80% no note, 15% generic, 5% personalized

---

### Tier D (Dormant)
**Focus:** No activity

## Note strategies

### No Note (70% for Tier A, 80% for Tier C)
- Just the connection request without message
- Fastest to send
- Good for open networkers and established networkers
- Most natural for large-scale connection building

### Generic Note (20% for Tier A, 15% for Tier C)
- Short, professional message
- Examples:
  - "Hi! I'd like to connect and expand my professional network."
  - "Hi! Let's connect and share industry insights."
  - "Would love to grow my network. Let's connect!"
- Shows intent without being too specific
- Works for recruiters and HR

### Personalized Note (10% for Tier A, 5% for Tier C)
- References target's company or background
- Examples:
  - "Hi! I noticed your work at TechStaff and would love to connect."
  - "Hi! As a Senior Recruiter, I think we'd have great insights to share."
  - "Hi! I'm impressed with your background. Let's connect!"
- Higher acceptance rate but slower to execute
- Reserved for high-value targets (Tier 1 recruiters, hiring managers)

## Input/Output schemas

### Get connection targets

**Input:**
```json
{
  "profile_id": "P-001",
  "tier": "A",
  "date": "2026-02-15",
  "daily_limit": 20
}
```

**Output:**
```json
{
  "profile_id": "P-001",
  "date": "2026-02-15",
  "tier": "A",
  "tier_name": "Thoroughbred",
  "daily_limit": 20,
  "targets_available": 20,
  "targets": [
    {
      "target_id": "T-512847",
      "category": "tier1_recruiters",
      "name": "Sarah Johnson",
      "title": "Senior Technical Recruiter",
      "company": "Cognizant",
      "connection_count": 1250
    }
  ],
  "target_distribution": {
    "tier1_recruiters": 0.40,
    "tier2_recruiters": 0.30,
    "hiring_managers": 0.20,
    "industry_peers": 0.10
  },
  "note_strategy": {
    "no_note": 0.70,
    "generic_note": 0.20,
    "personalized_note": 0.10
  }
}
```

### Execute connection request

**Input:**
```json
{
  "profile_id": "P-001",
  "target_id": "T-5678",
  "target_name": "Jane Recruiter",
  "target_title": "Senior Technical Recruiter",
  "target_company": "TechStaff Inc",
  "note": "Hi! I noticed your work at TechStaff and would love to connect.",
  "proxy_ip": "192.0.2.15"
}
```

**Output:**
```json
{
  "request_id": "CONN-REQ-20260215103245-45678",
  "profile_id": "P-001",
  "target_id": "T-5678",
  "target_name": "Jane Recruiter",
  "target_title": "Senior Technical Recruiter",
  "status": "SENT",
  "note_sent": true,
  "note_type": "personalized",
  "proxy_ip": "192.0.2.15",
  "timestamp": "2026-02-15T10:32:45Z"
}
```

### Execute batch connections

**Input:**
```json
{
  "profile_id": "P-001",
  "tier": "A",
  "date": "2026-02-15",
  "targets": [...],
  "proxy_ip": "192.0.2.15"
}
```

**Output:**
```json
{
  "profile_id": "P-001",
  "date": "2026-02-15",
  "tier": "A",
  "total_requests": 20,
  "requests": [...],
  "statistics": {
    "note_distribution": {
      "none": 14,
      "generic": 4,
      "personalized": 2
    },
    "no_note_percentage": 70.0,
    "with_note_percentage": 30.0
  },
  "timestamp": "2026-02-15T10:45:12Z"
}
```

## Performance

- Get targets: <50ms
- Single connection request: <5ms
- Batch of 20: <100ms

## Integration points

- **Schedule Generator:** Tells when to send connections
- **Activity Simulator:** Connection requests are scheduled as part of daily activity
- **Portfolio Manager:** Tracks total connections sent per day
- **Learning System:** Connection acceptance rates feed into profile health

## Metrics tracked

- Connections sent per profile per day
- Connection acceptance rate (leading indicator of account health)
- Note effectiveness (acceptance rate by note type)
- Target category performance (which categories have best acceptance)
- Regional patterns (if tracking by timezone)

## Safety constraints

- Daily limit enforced per tier
- No more than 20 per day per profile (LinkedIn hard limit)
- Time gaps between requests (randomized 3-15 seconds)
- IP not reused across profiles same day
- Human-like note distribution (not all generic, not all personalized)

## Future enhancements

- Machine learning to predict acceptance rates per target
- Budget-aware targeting (focus on high-value targets when nearing limit)
- Relationship history tracking (don't re-request if already connected)
- A/B testing of notes (track which performs better)
- Temporal patterns (when do acceptances happen)
