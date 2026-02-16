# Business context -- Consultadd staffing operations

## The company
Consultadd is an IT consulting company. The staffing team manages a bench of 25+ IT consultants between client assignments. The goal: get these consultants placed at client companies as fast as possible, prioritizing those with visa urgency.

## The bench
- Approximately 25 active consultants at any given time.
- Consultants cover categories: Java Developer, Python Developer, AI-ML Engineer, DevOps Engineer, Cloud Architect.
- Each consultant has varying experience (1-15+ years), visa status (H1B, OPT, CPT, GC, GC-EAD, Citizen, TN, L1), and rate requirements ($60K-$200K+).

## Job sources
Jay researches jobs across multiple channels:
- LinkedIn Job Board (role/company search, recruiter posts)
- Dice (technical job board, recruiter posts)
- Indeed (broad job board)
- Recruiter inbound (direct messages from vendors)
- Client direct (direct job requisitions)

## Jay's workflow

1. **Receive:** Z sends prioritized consultant with full profile.
2. **Research:** Jay finds relevant job postings across sources.
3. **Analyze:** For each job, extract tech stack, validate against consultant skills.
4. **Score:** Run confidence_calculator.py. Get a number.
5. **Research vendor:** Look up in vendor-database.md. Classify tier. Flag if unknown.
6. **Check freshness:** How old is the posting? How many applicants? Is it real?
7. **Build dossier:** Compile all findings into standard dossier format.
8. **Recommend:** Pass (7+), Human review (5-6.9), or Auto-skip (<5).
9. **Send to Rick:** If passing, send dossier. Rick builds application package.
10. **Send to Z:** Request submission. Z checks for conflicts. Z approves or blocks.

## Business rules Jay enforces

### Posting validity rules
1. Posting age > 30 days = likely stale, needs human review
2. Posting with 500+ applicants = likely stale or high-volume role, needs review
3. Contradictory tech stack (e.g., Java 8 + Spring Boot 3.0) = RED FLAG
4. Vague JD (no clear tech, no years experience stated) = RED FLAG
5. Unknown vendor = escalate to EM for manual vendor check

### Consultant-job matching rules
1. Consultant must have all MUST_HAVE skills.
2. Years of experience must be within acceptable range (usually N-2 to N+3 from requirement).
3. Consultant rate must be within 15% of target (green), 30% of target (yellow), >30% (red).
4. Posting freshness 0-1 day = +2 confidence points (hot opportunity).
5. Posting freshness 1-3 days = normal scoring.
6. Posting freshness 3-7 days = -1 confidence point.
7. Posting freshness 7+ days = -2 confidence points and human review flag.

### Vendor rules
1. Tier 1 vendor = +1.5 points to confidence (known reliable).
2. Tier 2 vendor = normal (+0).
3. Tier 3 vendor = -1 point (body shop risk).
4. Unknown vendor = escalate to EM or Z for manual check.

### Rate compatibility rules
1. Within 15% of target = 10 points (ideal).
2. Within 30% of target = 6 points (acceptable).
3. Beyond 30% = 2 points (significant mismatch, human review).

## Success metrics (tracked by Z and EM)
- Submission success rate (offers / submissions).
- Average time-to-placement per consultant.
- False positive rate (submissions that score high but get no response).
- Red flag accuracy (do flagged postings actually fail?).

## Communication channels (Slack)
- **#em-dashboard:** EM posts system status. Humans read here.
- **#agent-feed:** All inter-agent messages flow here (transparent log).
- **#alerts:** Critical alerts only. Human gets notified immediately.
- **#research-log:** Jay posts research summaries, escalations, and high-value dossiers.
- **#daily-hotlist:** Z publishes the daily Hot List every morning.
- **#kaizen:** EM posts daily improvement observations.
- **#human-commands:** Human posts instructions. EM interprets and routes.
