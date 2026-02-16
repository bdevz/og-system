# Business context -- Consultadd staffing operations

## The company
Consultadd is an IT consulting company. The staffing team manages a bench of 25+ IT consultants who are between client assignments. The goal: get these consultants placed at client companies as fast as possible, prioritizing those with visa urgency.

## The bench
- Approximately 25 active consultants at any given time.
- Consultants cover categories: Java Developer, Python Developer, AI-ML Engineer, DevOps Engineer, Cloud Architect.
- Each consultant may have multiple LinkedIn marketing profiles (managed by Leroy via Ads Power Browser + Zproxy).
- Consultants have varying visa statuses (H1B, OPT, CPT, GC, GC-EAD, Citizen, TN, L1) with different urgency levels.

## The CRM
- Log1 CRM is the source system for candidate data.
- Data arrives via flat file exports (CSV/Excel). No API integration yet.
- Exports include: consultant profiles, resumes, visa details, skills, rates, employment preferences.

## Business rules Z enforces

### Submission rules
1. Same consultant + same end client + last 90 days = BLOCK (right-to-represent risk)
2. Same consultant + same job posting ID = BLOCK (exact duplicate)
3. Same consultant + same client + different vendor within 30 days = WARN (vendor dispute risk)
4. Different consultant + same role + same vendor = ALLOW but LOG
5. Consultant on do-not-submit for this client = BLOCK

### Priority factors
- Visa urgency carries the most weight (35%). An expiring visa means the consultant could lose work authorization.
- Days on bench is second (25%). Longer on bench = more urgent to place.
- Market demand (20%). If there are lots of jobs matching their skills, push harder.
- Rate tier (10%). Higher rate = higher revenue per placement.
- Active submission count (10%). Fewer active submissions = needs more attention.

### Application targets
- 4-5 applications per candidate per day (respecting LinkedIn profile limits).
- Inbound leads from recruiters always prioritize over outbound applications.

### LinkedIn profiles
- Z tracks profile-to-consultant mapping but does NOT manage profile health (that's Leroy).
- Z enforces daily application limits per profile via rotation tracking.
- Z never allows the same profile to be used for conflicting applications (same client via different vendors).

## Communication channels (Slack)
- #em-dashboard: EM posts system status. Human reads here.
- #agent-feed: All inter-agent messages flow here (transparent log).
- #alerts: Critical alerts only. Human gets notified immediately.
- #inbound-leads: Leroy posts inbound leads. Rick's responses tracked here.
- #daily-hotlist: Z publishes the daily Hot List here every morning.
- #kaizen: EM posts daily improvement observations.
- #human-commands: Human posts instructions. EM interprets and routes.
