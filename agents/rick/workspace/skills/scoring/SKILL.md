# Scoring skill

This skill contains deterministic matching and filtering scripts for Agent Rick. All numerical calculations run through these scripts. Rick's AI role is to interpret results and coordinate submission logic. The scripts do the math.

## Scripts

### match_calculator.py
Computes candidate-job match scores using weighted factors. Accepts structured JSON input (candidate profile + job posting), returns score 0-100 with full breakdown.

Call `calculate_match(candidate, job)` for a single match or `calculate_match_matrix(candidates, jobs)` for a batch (25 x 25 = 625 comparisons).

Skill equivalency handled automatically (Spark ≈ PySpark = 0.8 credit, etc.).

### hard_filters.py
Pre-score elimination. Returns PASS/ELIMINATE/SKIP for any candidate-job pair.

Five hard rules applied:
1. DNS list match (consultant + client conflict) -> ELIMINATE
2. Category mismatch (Java dev to DevOps with 0 overlap) -> ELIMINATE
3. Visa hard block (job rejects visa type candidate has) -> ELIMINATE
4. Already submitted (recent submission to this client) -> ELIMINATE
5. Daily application limit reached -> SKIP (defer to tomorrow)

Call `apply_hard_filters(candidate, job, submission_history, dns_list)` before scoring.

### anti_cannibalization.py
Prevents self-sabotage. Four rules prevent competing applications.

Returns ALLOW/BLOCK with rule triggered.

Call `check_cannibalization(proposed_app, application_history)` before every submission.

## Configuration

### match_weights.json
Human-editable weights and brackets. Configure:
- Factor weights (required skills 30%, preferred 10%, experience 15%, etc.)
- Score thresholds (80+ STRONG, 70-79 GOOD, 60-69 BORDERLINE, <60 WEAK)
- Skill equivalency mappings (Spark ≈ PySpark = 0.8, etc.)
- Experience, rate, location, visa, freshness, vendor tier brackets

## Logging

### scoring_log.jsonl
Append-only audit trail. Every calculation, filter decision, and anti-cann check appends a line. Never delete. Used for retrospective analysis and debugging.

## Rules

- Never modify scoring scripts without human approval.
- Weight changes logged automatically (timestamp + reason).
- If a script errors, flag it and hold the decision for human review.
- Never estimate a score. Always run the script.
- Every block has a reason. Every score has breakdown.
