# Conflict checker skill

This skill wraps the duplicate_checker.py script with additional business logic for submission approval.

## Approval flow

When a submission request arrives from Jay or Rick (via EM):

1. Parse the request: consultant_id, end_client, vendor_name, job_posting_id
2. Load the consultant's do-not-submit list from their profile
3. Load the master DNS list from memory/do-not-submit-master.md
4. Load full submission history from memory/submission-log.jsonl
5. Run duplicate_checker.py with all inputs
6. If BLOCK: respond with NO + reason + conflicting record reference
7. If WARN: respond with advisory warning + allow human to decide
8. If ALLOW: respond with YES + generate submission record ID

## Additional checks beyond duplicate_checker.py

- LinkedIn profile daily limit: check if the assigned profile has exceeded its daily application count
- LinkedIn profile health: check if the profile is GREEN (from Z's tracking data)
- Consultant application limit: check if the consultant has already hit 4-5 applications today
- Rate compatibility sanity check: flag if posted rate is more than 20% below consultant minimum

## Response format

```
SUBMISSION APPROVAL RESPONSE
=============================
Decision: APPROVED / BLOCKED / WARNING
Submission ID: [auto-generated if approved]
Consultant: [name] (ID)
Job: [title] (posting ID)
Client: [end_client] via [vendor]

Checks passed: [list]
Checks failed: [list with reasons]
Conflicts: [list with record references]
```
