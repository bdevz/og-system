# Scoring skill

This skill contains deterministic scoring scripts for Agent Jay. All numerical calculations run through these scripts. Jay's role is to gather inputs and interpret results. The scripts do the math.

## Scripts

### confidence_calculator.py
Computes confidence scores for consultant-job matches using weighted factors. Accepts structured JSON input, returns score with full breakdown. Logs every calculation to scoring_log.jsonl.

Call `calculate_confidence(inputs)` for a single match or `calculate_batch_confidence(list)` for a sorted batch.

**Factors and weights:**
- Skill match (30%): Percentage of MUST_HAVE skills consultant has
- Experience alignment (20%): Years difference from requirement
- Posting freshness (15%): Days since posting
- Applicant volume (10%): Number of applicants (fewer = better signal)
- Vendor tier (10%): Vendor reliability tier
- Rate compatibility (10%): Percentage difference from target rate
- Red flags (5% penalty): Each flag reduces score

**Thresholds:**
- 7.0+ = PASS to Rick
- 5.0-6.9 = REVIEW (human judgment)
- <5.0 = SKIP (low confidence)

## Configuration

### confidence_weights.json
Human-editable weights file. Change weights here, not in code. Every weight change should include a reason and timestamp.

### scoring_log.jsonl
Append-only audit trail. Every confidence calculation appends a line. Never delete entries. Used for retrospective analysis and validation rule discovery.

## Rules
- Never modify scoring scripts without human approval.
- Weight changes are logged automatically.
- If a script errors, flag it and hold the decision for human review.
- Never estimate a score. Always run the script.
- Every calculation logged to scoring_log.jsonl with full breakdown.
