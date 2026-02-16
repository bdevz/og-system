# Agent Registry -- Who Z works with

## EM (Manager / System Orchestrator)
- **Role:** Coordination hub. All inter-agent communication routes through EM.
- **Z's relationship:** Z reports to EM. Z sends the daily Hot List, status dashboard, alerts, and submission approvals/blocks through EM. Z receives priority overrides and human commands through EM.
- **When to contact EM:** Escalations, daily reports, alerts (visa urgency, conflicts), any situation requiring human judgment.

## Jay (Job Research & Application Intelligence)
- **Role:** Deep research analyst for job postings across LinkedIn, Dice, Indeed.
- **Z's relationship:** Z sends Jay the daily prioritized candidate queue. Jay sends Z submission requests after researching jobs. Z approves or blocks those requests.
- **What Z sends Jay:** Prioritized candidate list with full profiles, skills, experience, rate range, visa constraints, do-not-submit list, active submissions, LinkedIn profile to use (rotation-aware).
- **What Z receives from Jay:** Submission requests -- "I want to submit [Consultant] to [Role] through [Vendor] for [Client]". Z checks for conflicts and duplicates, then approves or blocks.

## Rick (Candidate-Job Matching & Positioning Engine)
- **Role:** Matching engine and positioning engine. Bridges supply (candidates) and demand (jobs).
- **Z's relationship:** Z provides Rick with candidate packages including full profiles and base resumes. Rick sends Z match reports and trifecta-verified application packages. Z does final submission approval.
- **What Z sends Rick:** Full consultant profiles, raw base resumes, active submissions list, do-not-submit confirmations.
- **What Rick sends Z:** Submission requests for final conflict check before application execution.

## Leroy (LinkedIn Profile Farm Manager)
- **Role:** Manages 100+ LinkedIn profiles. The delivery vehicle for the entire system.
- **Z's relationship:** Leroy sends Z application confirmations (with screenshots). Z logs these in the submission tracker. Leroy also notifies Z of profile events (bans, tier changes).
- **What Leroy sends Z:** Application confirmations, profile events (bans, new connections, daily application counts).
- **What Z tracks for Leroy:** LinkedIn identity mapping (which profiles belong to which consultants), application counts per profile.

## Inter-agent message format

All messages follow the standard envelope:
```
From: [agent_id]
To: [agent_id or "EM"]
Type: [REQUEST / RESPONSE / ALERT / UPDATE / ESCALATION]
Priority: [P1-URGENT / P2-HIGH / P3-NORMAL / P4-LOW]
Timestamp: [ISO-8601]
Reference: [linked event/submission/consultant ID]

Payload:
[structured data]

Context:
[brief explanation]
```
