# Tools available to Rick

## Scoring scripts (deterministic, Python)

### match_calculator.py
- **Purpose:** Compute candidate-job match scores using weighted factors.
- **Input:** Candidate JSON (skills, experience, rate, visa, location) + Job JSON (required skills, preferred skills, rate, location, visa requirements, vendor tier, posting freshness).
- **Output:** JSON with composite score (0-100), per-factor breakdown, skill equivalency mappings, recommendation (STRONG/GOOD/BORDERLINE/WEAK).
- **Weights:** Loaded from `match_weights.json`. Human-editable.
- **Usage:** Called for every candidate-job evaluation. Can run single match or batch (25 candidates x 25 jobs = 625 comparisons).
- **Logging:** Every calculation appends to scoring_log.jsonl with full breakdown.

### match_weights.json
- **Purpose:** Configuration for match scoring weights.
- **Content:** Weight percentages for skill overlap (required/preferred), experience alignment, rate, location, visa, posting freshness, vendor tier. Thresholds for score bands (80+, 70-79, 60-69, <60).
- **Human-editable:** Yes. Every change should include timestamp and reason.

## Hard filters (elimination logic)

### hard_filters.py
- **Purpose:** Pre-score elimination. Returns candidates that should NOT be submitted.
- **Input:** Candidate dict + Job dict + submission_history list + dns_list.
- **Output:** JSON with decision (PASS/ELIMINATE/SKIP), reason, rule_triggered.
- **Rules applied:**
  1. DNS list match (consultant + client conflict) -> ELIMINATE
  2. Category mismatch (Java dev to DevOps with 0 DevOps skills) -> ELIMINATE
  3. Visa hard block (job says "no H1B", candidate is H1B) -> ELIMINATE
  4. Already submitted (recent submission to this client) -> ELIMINATE
  5. Daily application limit reached -> SKIP (defer to tomorrow)
- **Usage:** First step before scoring any candidate.
- **Logging:** Logged in scoring_log.jsonl with block reason.

## Anti-cannibalization rules

### anti_cannibalization.py
- **Purpose:** Prevent Rick's own submissions from competing and sabotaging conversion.
- **Input:** Proposed_application dict + application_history list.
- **Output:** JSON with decision (ALLOW/BLOCK), rule_triggered, explanation.
- **Rules applied:**
  1. One candidate per job posting (no duplicate profile submissions to same job).
  2. One candidate per client per vendor per week (no competing submissions from same agency).
  3. One profile per client (never two different "candidates" of same person to same client).
  4. Diversify across clients (don't burn all 5 daily apps on one client).
- **Usage:** Check before submitting any candidate.
- **Logging:** Logged in scoring_log.jsonl with rule triggered.

## Positioning scripts

### position_generator.py
- **Purpose:** Generate positioning directives for resume customization.
- **Input:** Candidate profile (skills, experience, work history) + Job analysis (role title, required skills, client industry, seniority level).
- **Output:** JSON with positioning directive including: primary angle, skills to emphasize, skills to de-emphasize, experience frame suggestions, keywords to plant, version requirements.
- **Usage:** Called after candidate selected for submission.
- **Example output:**
  ```json
  {
    "candidate_id": "C-042",
    "job_id": "J-1234",
    "primary_angle": "Microservices Architect",
    "skills_emphasize": ["Microservices", "Spring Boot", "Docker", "Kubernetes"],
    "skills_deemphasize": ["Legacy monolith work"],
    "experience_frame": "Focus on distributed system projects; minimize enterprise monolith experience",
    "keywords_to_plant": ["event-driven", "scalability", "cloud-native", "async messaging"],
    "version_requirements": {"java": "11+", "spring": "5.0+", "docker": "latest"},
    "positioning_rationale": "Job emphasizes microservices at scale. Candidate has this but also has monolith experience. Frame as scaling experience."
  }
  ```

### keyword_planter.py
- **Purpose:** Extract JD keywords and map to candidate's actual experience.
- **Input:** Job description (text) + Candidate profile (skills, experience).
- **Output:** JSON with keyword mapping: required keyword -> candidate match (DIRECT/MAPPED/MISSING), ATS pass-through recommendation.
- **Rules:**
  - Required keyword -> exact match in candidate -> DIRECT PLANT
  - Required keyword -> equivalent skill -> MAPPED PLANT (e.g., "Airflow" in JD -> "Step Functions as orchestration equivalent" in resume)
  - Required keyword -> not in candidate -> MISSING (flag gap, recommend positioning angle instead)
- **Usage:** Part of trifecta validation and resume generation prep.

## LinkedIn profile selection

### profile_picker.py
- **Purpose:** Select optimal LinkedIn profile for each candidate-job match.
- **Input:** Candidate's profile list + target role + application history + linkedin profile health status.
- **Output:** JSON with selected profile ID, health status, reasoning, application count for today.
- **Selection criteria:**
  1. Role alignment: profile positioning vs target role title/description.
  2. Profile health: must be Active/GREEN (not banned, not at daily limit yet).
  3. Application count: hasn't hit daily limit (5 per day max).
  4. Recent usage: avoid profile conflicts (same profile not applied to competing roles same day).
  5. Inbound history: keep consistent if candidate received recent inbound from this role type.
- **Usage:** Called before every application submission.
- **Logging:** Logged with selection reasoning.

## Trifecta validation

### alignment_check.py (Trifecta Validator)
- **Purpose:** Pre-application verification checklist. Ensure candidate data, LinkedIn, and resume align.
- **Input:** Candidate data dict + LinkedIn profile object + Resume text + Job posting.
- **Output:** JSON with ALIGNED/FAILED decision, checklist results, failures list with suggested fixes.
- **Validation checklist:**
  - Candidate fit: match score above 70, no DNS conflicts, no duplicates, visa compatible, rate compatible.
  - LinkedIn profile: health GREEN, positioning matches role, daily limits not exceeded, no conflicts with other apps, work history consistent with resume.
  - Resume: keywords planted, versions correct, experience framing consistent with LinkedIn positioning, no obvious red flags for client.
- **Usage:** Last step before Z approval request.
- **Output example:**
  ```json
  {
    "decision": "ALIGNED",
    "overall_pass": true,
    "checklist": {
      "candidate_fit": {
        "passed": true,
        "match_score": 78,
        "dns_clear": true,
        "no_duplicates": true,
        "visa_compatible": true,
        "rate_compatible": true
      },
      "linkedin_profile": {
        "passed": true,
        "health": "GREEN",
        "positioning_match": "strong",
        "daily_limit_ok": true,
        "no_conflicts": true,
        "history_consistent": true
      },
      "resume": {
        "passed": true,
        "keywords_planted": ["microservices", "kubernetes", "docker"],
        "versions_correct": true,
        "framing_consistent": true,
        "no_red_flags": true
      }
    },
    "ready_for_submission": true
  }
  ```

## Resume tool connector

### api_client.py (Resume Tool Connector)
- **Purpose:** Interface with resume generation tool (web app with API).
- **Input:** Positioning directive JSON.
- **Output:** Generated resume PDF/text with keywords planted, formatting applied, versions noted.
- **Features:**
  - Accepts structured positioning input from position_generator.
  - Sends to resume generation API.
  - Returns generated resume.
  - Retry logic (max 2 retries on timeout).
  - Validates output (keywords present, versions correct, no obvious errors).
  - For now: well-structured stub that logs what it would send. Real API endpoint wired later.
- **Usage:** Called after positioning directive generated and validated.

## Memory and templates

### positioning-templates.md
- Template positioning angles per category (Java, Python, DevOps, AI-ML).
- Updated based on conversion feedback.
- Used to seed positioning_generator suggestions.

### keyword-effectiveness.md
- Tracks which keywords correlate with interview callbacks.
- Empty initially, filled by feedback loop from Leroy/EM.
- Used to optimize keyword planting strategy.

### lessons-learned.md
- Retrospective notes on failed matches, bad positioning angles, cannibalization incidents.
- Used to prevent repeated mistakes.

## Logging and audit

### scoring_log.jsonl
- Append-only audit trail of all scoring calculations, hard filter decisions, anti-cann checks.
- Every calculation logged with: timestamp, candidate_id, job_id, decision, full breakdown, rule triggered (if blocked).
- Used for retrospective analysis and error investigation.

## Rules

- Never modify scoring scripts without human approval.
- Weight changes are logged automatically.
- If a script errors, flag it and hold the decision for human review.
- Never estimate a score. Always run the script.
- Every decision logged with full context.
