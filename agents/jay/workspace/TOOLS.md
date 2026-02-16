# Tools available to Jay

## Scoring scripts (deterministic, Python)

### confidence_calculator.py
- **Purpose:** Compute confidence score for a consultant-job match.
- **Input:** JSON with skill_match_percent, years_experience_diff, posting_freshness_days, applicant_count, vendor_tier, consultant_rate, target_rate, red_flags_list.
- **Output:** JSON with composite confidence score (0-10), per-factor breakdown, thresholds (pass/review/skip), recommendation.
- **Weights:** Skill match 30%, Experience alignment 20%, Posting freshness 15%, Applicant volume 10%, Vendor tier 10%, Rate compatibility 10%, Red flags 5%.
- **Thresholds:** 7+ = pass to Rick, 5-6.9 = human review, <5 = auto-skip.
- **Logging:** Every calculation appended to scoring_log.jsonl.

Call `calculate_confidence(inputs)` for a single job-consultant pair or `calculate_batch_confidence(list)` for a sorted batch.

## Analysis scripts (deterministic, Python)

### jd_analyzer.py
- **Purpose:** Extract and classify job description components.
- **Input:** Raw JD text, company type (enterprise/startup/mid-market).
- **Output:** Structured dict with keywords, requirement classification (MUST_HAVE/NICE_TO_HAVE/INFERRED), tech compatibility flags, version estimates, experience level.
- **Usage:** First step in analyzing any new posting.

Call `analyze_jd(jd_text, company_type)` to get structured analysis.

### tech_stack_mapper.py
- **Purpose:** Map technology relationships, flag contradictions, estimate versions.
- **Input:** Set of technologies extracted from JD.
- **Output:** Complementary techs, contradictions (if any), version estimates by industry type.
- **Maintains:** TECH_RELATIONSHIPS dict (e.g., "Kubernetes" → ["Docker", "Helm", "CI/CD"]), TECH_CONTRADICTIONS list.
- **Usage:** Called after JD analysis to validate and enrich tech stack.

Call `map_tech_stack(tech_list, company_type)` to get relationships and validate stack.

### vendor_classifier.py
- **Purpose:** Classify vendor into tier and look up known info.
- **Input:** Vendor name.
- **Output:** Tier (1/2/3/Niche), known client list, response rate, ghost rate, last activity, confidence of classification.
- **Maintains:** vendor-database.md as the knowledge base. Grows with every submission outcome.
- **Tiers:**
  - Tier 1: Insight Global, Robert Half, TEKsystems, Infosys, Cognizant, TCS, Wipro, Accenture
  - Tier 2: Regional specialists, niche firms with good track record
  - Tier 3: Sub-vendors, body shops, low success rate
  - Niche: Small firms with direct relationships
- **Usage:** Called when analyzing any job posting to assess vendor reliability.

Call `classify_vendor(vendor_name)` to get tier and known info.

### staleness_detector.py
- **Purpose:** Detect stale/dead postings and identify red flags.
- **Input:** Posting metadata (age_days, applicant_count, title, company, tech_stack, experience_required).
- **Output:** Staleness score, red flag list (contradictory tech, unrealistic experience, vague JD, duplicate posting, etc.), recommendation (FRESH/STALE/DEAD).
- **Usage:** Called early to filter out low-signal postings.

Call `detect_staleness(posting_metadata)` to assess posting quality and age.

## Database and memory files

### vendor-database.md
Human-editable vendor knowledge base. Tier 1/2/3 known vendors with columns: Vendor, Tier, Submissions, Responses, Interviews, Placements, Ghost Rate, Last Activity, Known End Clients, Notes.

### tech-version-baseline.md
Technology version estimates by industry type. Enterprise vs startup versions for major techs: Java, Python, Spring Boot, Kubernetes, React, AWS, Azure, etc.

### application-history.jsonl
Append-only log of all submissions sent via Jay's recommendations. Structure: timestamp, consultant_id, job_id, vendor, confidence_score, outcome (pending/rejected/interview/offered).

### lessons-learned.md
Lessons learned from submission outcomes and research errors. Format: Lesson [NNN] -- [Date], What happened, Root cause, Fix applied, Status, Impact since applied.

## Configuration

### confidence_weights.json
Human-editable weights file. Change weights here, not in code. Every weight change should include a reason and timestamp. Mirror of Z's priority_weights.json structure.

### scoring_log.jsonl
Append-only audit trail. Every confidence calculation appends a line. Never delete entries. Used for retrospective analysis and validation rule discovery.

## Rules
- Never modify scoring scripts without human approval.
- Weight changes are logged automatically.
- If a script errors, flag it and hold the decision for human review.
- Never estimate a score. Always run the script.
- Update vendor-database.md and tech-version-baseline.md weekly based on submission outcomes.
