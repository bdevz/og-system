# Scoring skill

This skill contains deterministic scoring scripts for Agent Z. All numerical calculations run through these scripts. Z's AI role is to gather inputs and interpret results. The scripts do the math.

## Scripts

### priority_calculator.py
Computes consultant priority scores using weighted factors. Accepts structured JSON input, returns score with full breakdown. Logs every calculation to scoring_log.jsonl.

Call `calculate_priority(inputs)` for a single consultant or `calculate_batch_priorities(list)` for a sorted batch.

### visa_urgency_calculator.py
Determines visa urgency tier from visa type and expiration date. Pure date arithmetic. Returns tier (CRITICAL/HIGH/MEDIUM/LOW/NA), days remaining, and urgency score.

Call `calculate_visa_urgency(inputs)` for one consultant or `calculate_batch_visa_urgency(list)` for a sorted batch.

### duplicate_checker.py
Checks a submission request against the full submission history using 5 hard rules. Returns ALLOW/BLOCK/WARN with every rule that fired and every conflicting record.

Call `check_submission(request, history, dns_list)` before approving any submission.

## Configuration

### priority_weights.json
Human-editable weights file. Change weights here, not in code. Every weight change should include a reason and timestamp.

### scoring_log.jsonl
Append-only audit trail. Every calculation appends a line. Never delete entries. Used for retrospective analysis.

## Rules
- Never modify scoring scripts without human approval.
- Weight changes are logged automatically.
- If a script errors, flag it and hold the decision for human review.
- Never estimate a score. Always run the script.
