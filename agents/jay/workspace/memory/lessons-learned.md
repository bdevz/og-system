# Lessons Learned -- Agent Jay

Every mistake that gets past Jay becomes a new validation rule. Same mistake never happens twice.

## Template

```
## Lesson [NNN] -- [Date]
**What happened:** [description of the incident]
**Root cause:** [why it happened]
**Fix applied:** [new rule, validation, or process change]
**Status:** Active / Superseded by Lesson [NNN]
**Impact since applied:** [how many times the fix has prevented recurrence]
```

## Active lessons

(None yet -- this file is populated as the system operates and learns from errors.)

---

## Historical lessons (when populated)

Will contain entries like:

```
## Lesson 001 -- 2026-02-20
**What happened:** Submitted consultant for job with contradictory tech stack (Java 8 + Spring Boot 3.0). Consultant was overqualified on Java version but underqualified on Spring Boot 3.0 version assumptions. Submission was rejected.
**Root cause:** Tech stack validation passed contradictory versions without flagging. Didn't check version compatibility rules.
**Fix applied:** Added explicit version compatibility check in tech_stack_mapper.py. Added red flag for incompatible version combinations. Added validation rule to confidence_calculator.py to reduce score when contradictions exist.
**Status:** Active
**Impact since applied:** 3 similar submissions caught before sending
```

## Categories for tracking

### Technology matching errors
- Missed skill mismatches
- Incorrect version assumptions
- Contradictory tech stacks not flagged

### Vendor reliability errors
- Submitted through vendor with high ghost rate
- Missed tier classification
- Unknown vendor not escalated

### Posting quality errors
- Submitted stale posting that never got response
- Missed red flags in JD
- Submitted duplicate posting

### Confidence scoring errors
- Score too high for poor match
- Score too low for good match
- Red flag penalties miscalibrated

### Consultant profile errors
- Consulted outdated profile from Z
- Missed visa urgency
- Rate mismatch not caught

## Quality metrics
- Monthly false positive rate (high confidence → no response)
- Monthly false negative rate (low confidence → got interview)
- Median time to implement lesson fixes
- Most common lesson categories
