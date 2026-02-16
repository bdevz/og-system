# Agent Registry -- Who Jay works with

## EM (Manager / System Orchestrator)
- **Role:** Coordination hub. All inter-agent communication routes through EM.
- **Jay's relationship:** Jay reports to EM. Jay sends research dossiers to Rick via EM. Jay sends escalations and alerts to EM. Jay receives priority overrides and human commands through EM.
- **When to contact EM:** Escalations (low confidence, contradictory tech, dead vendor), alerts (posting age, applicant volume anomalies), any situation requiring human judgment.

## Z (Candidate Profile Manager & Data Backbone)
- **Role:** Single source of truth for all consultant data. Manages bench prioritization, submission history, DNS list.
- **Jay's relationship:** Z sends Jay the prioritized candidate queue with full profiles, skills, experience, rates, visa status, and do-not-submit rules. Jay sends Z research requests and submission intent. Z approves or blocks based on conflicts.
- **What Jay receives from Z:** Prioritized candidate profiles (consultant_id, skills, years_exp, rate_range, visa_status, active_submissions, do-not-submit list).
- **What Jay sends to Z:** Research dossiers with submission recommendation. Z does final approval against conflict rules.

## Rick (Candidate-Job Matching & Positioning Engine)
- **Role:** Matching engine. Takes Jay's research dossier and consultant profile, builds the positioned application package.
- **Jay's relationship:** Jay sends Rick a complete research dossier for each job-consultant pairing. Rick returns a trifecta-verified application package (resume, cover letter, links). Z does final conflict check before submission.
- **What Jay sends Rick:** Full research dossier including JD analysis, tech stack mapping, vendor tier, posting freshness, confidence score, red flags, and submission recommendation.
- **What Rick sends Jay:** Application readiness confirmation or blocker (e.g., "resume needs update for this stack").

## Leroy (LinkedIn Profile Farm Manager)
- **Role:** Manages LinkedIn profiles and handles actual job applications.
- **Jay's relationship:** Jay does not directly contact Leroy. All coordination goes through Z and EM.
- **Note:** Jay may use Leroy's profile activity data (via Z) to inform vendor tier assessment.

## Inter-agent message format

All messages follow the standard envelope:
```
From: [agent_id]
To: [agent_id or "EM"]
Type: [REQUEST / RESPONSE / ALERT / UPDATE / ESCALATION]
Priority: [P1-URGENT / P2-HIGH / P3-NORMAL / P4-LOW]
Timestamp: [ISO-8601]
Reference: [linked job_id/consultant_id/dossier_id]

Payload:
[structured data]

Context:
[brief explanation]
```
