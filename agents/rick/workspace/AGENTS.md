# Agent Registry -- Who Rick works with

## Z (Candidate Profile Manager & Data Backbone)
- **Role:** Single source of truth for candidate profiles, submission history, do-not-submit rules.
- **Rick's relationship:** Rick receives candidate packages from Z. Rick sends submission requests to Z for final conflict/duplicate check before execution.
- **What Rick receives from Z:** Full candidate profiles (skills, experience, rate, visa, employment history), base resumes, active submission list, do-not-submit confirmations, LinkedIn profile rotation status.
- **What Rick sends to Z:** Match reports (candidate vs job analysis), trifecta-verified application packages with positioning directives, submission requests for final approval.

## Jay (Job Research & Application Intelligence)
- **Role:** Deep research analyst for job postings. Identifies which candidates might be good fits.
- **Rick's relationship:** Jay sends Rick job postings with detailed analysis. Rick scores candidates against those jobs and sends back match reports with recommended candidates ranked by fit.
- **What Rick receives from Jay:** Job posting data (JD, required skills, preferred skills, rate, location, vendor, client, posting freshness, vendor tier).
- **What Rick sends to Jay:** Match rankings (top 5 candidates for this job ranked by score), positioning recommendations for top matches.

## EM (Manager / System Orchestrator)
- **Role:** Coordination hub. All escalations and policy decisions route through EM.
- **Rick's relationship:** Rick escalates borderline matches, trifecta failures, cannibalization risks, and policy questions to EM.
- **When to contact EM:** Scores 60-70, trifecta mismatches, hard filter edge cases, cannibalization warnings, positioning strategy questions.

## Leroy (LinkedIn Profile Farm Manager)
- **Role:** Manages 100+ LinkedIn profiles. Tracks profile health, application counts, daily limits.
- **Rick's relationship:** Rick requests profile selection for application. Leroy confirms profile availability and application limit status. Leroy executes the application.
- **What Rick sends Leroy:** Application execution requests with selected profile ID, positioning directive, resume, targeted job details.
- **What Rick receives from Leroy:** Profile application confirmations, profile health alerts (bans, tier changes, daily limit reached).

## Inter-agent message format

All messages follow the standard envelope:
```
From: rick
To: [agent_id or "EM"]
Type: [REQUEST / RESPONSE / ALERT / UPDATE / ESCALATION]
Priority: [P1-URGENT / P2-HIGH / P3-NORMAL / P4-LOW]
Timestamp: [ISO-8601]
Reference: [linked candidate_id / job_id / submission_id]

Payload:
[structured data]

Context:
[brief explanation]
```

## Workflow examples

### Scoring a candidate for a job
1. Jay sends Rick a job posting with full analysis.
2. Rick runs candidate list through match_calculator against the job.
3. Rick returns ranked match list with scores and breakdowns.

### Submitting a candidate
1. Rick selects top candidate from match list.
2. Rick runs hard_filters to check for blocks (DNS, visa, category mismatch, daily limit).
3. Rick checks anti_cannibalization to confirm no competing submissions.
4. Rick generates positioning directive via position_generator.
5. Rick selects optimal LinkedIn profile via profile_picker.
6. Rick validates trifecta alignment via alignment_check.
7. Rick sends submission request to Z with full trifecta package.
8. Z checks duplicates/conflicts and approves or blocks.
9. If approved, Rick routes to Leroy for LinkedIn application execution.
