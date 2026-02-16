# Staleness Detector skill

Detects stale, dead, and low-quality job postings early.

## Script

### staleness_detector.py
Analyzes posting metadata and detects staleness/quality issues. Accepts posting metadata dict, returns staleness score (0-10), status (FRESH/ACCEPTABLE/AGING/STALE), red flags, and recommendation.

Call `detect_staleness(posting_metadata)` to assess posting quality and viability.

**Staleness Score:**
- 8+: FRESH (green light)
- 6-8: ACCEPTABLE (yellow light, check red flags)
- 4-6: AGING (orange light, human review)
- <4: STALE (red flag, likely dead)

**Red Flags Detected:**
- Posting age > 30 days or > 60 days
- Applicant volume > 200 or > 500
- Contradictory technologies
- Unrealistic experience requirements
- Vague JD (too short)
- Missing technologies or experience years
- Missing salary or location
- Duplicate posting pattern
- Reposting within 7 days of same role

**Output includes:**
- Staleness score and status
- Recommendation (green/yellow/orange/red light)
- Age analysis (days old, category)
- Volume analysis (applicant count, category)
- Complete red flag list
- Boolean flags: is_dead, needs_human_review

## Rules
- Never submit without checking staleness first.
- Posting > 30 days old gets escalated to human review.
- Posting > 500 applicants is likely dead or viral posting.
- Multiple red flags trigger escalation regardless of age.
- Staleness_detector runs first in Jay's workflow before deep analysis.
