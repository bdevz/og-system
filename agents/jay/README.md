# Agent Jay -- Job Research & Application Intelligence

Complete workspace for Agent Jay, the research engine of the Consultadd multi-agent staffing system.

## Overview

Jay is a PhD HR specialist with 10 years of recruitment experience. His role: deep research every job posting, validate consultant-job matches, and compile detailed research dossiers for submission to Rick (the positioning engine) and Z (the conflict checker).

## Directory Structure

```
jay/
├── workspace/                    # Core workspace with all skills and knowledge
│   ├── SOUL.md                  # Jay's mission, thinking style, and rules
│   ├── AGENTS.md                # Inter-agent communication protocols
│   ├── USER.md                  # Business context and staffing operations
│   ├── TOOLS.md                 # Available tools and capabilities
│   │
│   ├── skills/                  # Deterministic scoring and analysis scripts
│   │   ├── scoring/
│   │   │   ├── confidence_calculator.py      # Consultant-job match scoring
│   │   │   ├── confidence_weights.json       # Human-editable scoring weights
│   │   │   ├── scoring_log.jsonl            # Append-only audit trail
│   │   │   └── SKILL.md
│   │   │
│   │   ├── jd-analyzer/
│   │   │   ├── jd_analyzer.py               # JD parsing and requirement extraction
│   │   │   └── SKILL.md
│   │   │
│   │   ├── tech-stack-mapper/
│   │   │   ├── tech_stack_mapper.py         # Technology validation and relationships
│   │   │   └── SKILL.md
│   │   │
│   │   ├── vendor-intelligence/
│   │   │   ├── vendor_classifier.py         # Vendor tier classification
│   │   │   └── SKILL.md
│   │   │
│   │   ├── staleness-detector/
│   │   │   ├── staleness_detector.py        # Dead/stale posting detection
│   │   │   └── SKILL.md
│   │   │
│   │   └── dossier-builder/
│   │       ├── dossier_builder.py           # Final research dossier assembly
│   │       └── SKILL.md
│   │
│   └── memory/                  # Institutional knowledge and logs
│       ├── vendor-database.md               # Vendor performance tracking
│       ├── tech-version-baseline.md         # Tech adoption patterns by industry
│       ├── application-history.jsonl        # Append-only submission log
│       └── lessons-learned.md               # Error tracking and validation rules
│
├── agent/                       # Agent interface (stub)
└── sessions/                    # Session logs (stub)
```

## Quick Start

### 1. Understanding Jay's Role

Start by reading these files in order:
1. `workspace/SOUL.md` - Jay's personality, mission, and decision-making style
2. `workspace/USER.md` - Business context and staffing operations
3. `workspace/TOOLS.md` - Available tools and inputs/outputs
4. `workspace/AGENTS.md` - How Jay communicates with Z, Rick, and EM

### 2. Testing the Scoring System

```bash
cd workspace/skills/scoring/

# Run confidence calculator with sample data
python confidence_calculator.py

# Test with custom JSON input
python confidence_calculator.py /path/to/input.json
```

### 3. Testing JD Analysis

```bash
cd workspace/skills/jd-analyzer/

# Run with sample JD
python jd_analyzer.py

# Analyze custom JD
python jd_analyzer.py /path/to/jd.txt [company_type]
```

### 4. Vendor Classification

```bash
cd workspace/skills/vendor-intelligence/

# Classify a vendor
python vendor_classifier.py "Robert Half"

# Demo with all known vendors
python vendor_classifier.py
```

### 5. Staleness Detection

```bash
cd workspace/skills/staleness-detector/

# Run with sample postings
python staleness_detector.py

# Test custom posting
python staleness_detector.py /path/to/posting.json
```

### 6. Tech Stack Validation

```bash
cd workspace/skills/tech-stack-mapper/

# Run with sample tech stack
python tech_stack_mapper.py

# Validate custom stack
python tech_stack_mapper.py /path/to/techs.json [company_type]
```

## Scoring System

### Confidence Calculator (Primary Scoring)

The **confidence_calculator.py** is the deterministic scoring engine that produces match scores (0-10).

**Factors and Weights:**
- Skill match (30%): % of MUST_HAVE skills consultant has
- Experience alignment (20%): Years difference from requirement
- Posting freshness (15%): Days since posting
- Applicant volume (10%): Number of applicants (fewer = better signal)
- Vendor tier (10%): Vendor reliability tier
- Rate compatibility (10%): $ difference from target rate
- Red flags (5% penalty): Each flag reduces score by 1 point

**Thresholds:**
- **7.0+**: PASS to Rick (submit)
- **5.0-6.9**: REVIEW (human judgment needed)
- **<5.0**: SKIP (low confidence)

**Usage:**
```python
from skills.scoring.confidence_calculator import calculate_confidence

result = calculate_confidence({
    "consultant_id": "C-042",
    "job_id": "J-5829",
    "skill_match_percent": 85,
    "years_experience_diff": 2,
    "posting_freshness_days": 1,
    "applicant_count": 18,
    "vendor_tier": 1,
    "consultant_rate": 95000,
    "target_rate": 100000,
    "red_flags": []
})
# Returns: {"score": 8.5, "recommendation": "PASS", "breakdown": {...}}
```

## Analysis Pipeline

### Standard Jay Workflow

1. **Staleness Check** (`staleness_detector.py`)
   - Is posting fresh or dead?
   - Red flags: age, volume, quality issues
   - Output: FRESH/ACCEPTABLE/AGING/STALE

2. **JD Analysis** (`jd_analyzer.py`)
   - Extract technologies, requirements, experience level
   - Classify requirements: MUST_HAVE / NICE_TO_HAVE / INFERRED
   - Identify contradictions and red flags
   - Output: structured JD analysis

3. **Tech Stack Validation** (`tech_stack_mapper.py`)
   - Map technology relationships
   - Flag contradictions (e.g., AWS + Azure)
   - Check missing requirements (e.g., Spring Boot needs Java)
   - Output: validation results + warnings

4. **Vendor Research** (`vendor_classifier.py`)
   - Classify vendor into tier (1/2/3/unknown)
   - Look up performance metrics (response rate, ghost rate)
   - Output: vendor info + confidence of classification

5. **Confidence Scoring** (`confidence_calculator.py`)
   - Score consultant-job match deterministically
   - Apply all weights and penalties
   - Log calculation to scoring_log.jsonl
   - Output: confidence score + breakdown

6. **Dossier Assembly** (`dossier_builder.py`)
   - Compile all outputs into standard dossier format
   - Identify risks and action items
   - Generate recommendations for Rick
   - Output: complete research dossier

## Key Decisions

### When to PASS (score >= 7.0)
- Strong skill match (80%+)
- Experience within 2 years of requirement
- Fresh posting (0-3 days old)
- Tier 1 vendor with >85% response rate
- No contradictory tech stack
- Rate within 15% of target

### When to REVIEW (score 5.0-6.9)
- Moderate skill match (60-80%)
- Experience within 3-5 years of requirement
- Aging posting (3-14 days old)
- Tier 2 vendor or unknown vendor
- Minor tech warnings
- Rate within 30% of target

### When to SKIP (score <5.0)
- Low skill match (<60%)
- Experience significantly off target (>5 years difference)
- Stale posting (14+ days old)
- Tier 3 vendor with high ghost rate
- Contradictory tech stack
- Rate >30% off target
- Multiple red flags

## Memory Files

### vendor-database.md
Tracks vendor performance and reliability. Updated weekly from submission outcomes.

**Columns:**
- Vendor name and tier (1/2/3/Niche)
- Response rate (% responses within 7 days)
- Ghost rate (% no follow-up after 14 days)
- Submissions, placements, known clients
- Last activity date

**Tier 1 vendors:** Insight Global, Robert Half, TEKsystems, Infosys, Cognizant, TCS, Wipro, Accenture

### tech-version-baseline.md
Estimated technology versions by industry type.

**Examples:**
- Enterprise Java: 11 or 17 (LTS, conservative)
- Startup Java: 17 or 21 (latest)
- Startup Python: 3.10 or 3.11 (latest)
- Enterprise Python: 3.8 or 3.9 (stable)

### application-history.jsonl
Append-only log of all submissions. Each line is a JSON object with:
- Timestamp, consultant_id, job_id, vendor, confidence_score
- Outcome (pending/rejected/interview/offered)

### lessons-learned.md
Validation rules learned from errors. When an error occurs:
1. Document what happened
2. Identify root cause
3. Implement fix (new rule/validation/process)
4. Track impact of fix

## Configuration

### confidence_weights.json

All scoring weights are in a separate JSON file for easy modification.

```json
{
  "version": "1.0.0",
  "weights": {
    "skill_match": 0.30,
    "experience_alignment": 0.20,
    "posting_freshness": 0.15,
    "applicant_volume": 0.10,
    "vendor_tier": 0.10,
    "rate_compatibility": 0.10
  },
  "thresholds": {
    "pass": 7.0,
    "review": 5.0
  },
  "scoring_tables": {
    "skill_match": {
      "90-100": 10,
      "75-90": 8,
      ...
    },
    ...
  }
}
```

**To adjust weights:**
1. Edit `confidence_weights.json`
2. Update `version`, `last_updated`, `change_reason`
3. Run tests to validate impact
4. Commit change with rationale

## Error Handling

All scripts follow this error severity model:

- **CRITICAL:** Stop processing, alert EM immediately
  - Contradictory tech contradictions blocking submission
  - Vendor data integrity issues
  - Score calculation failures

- **HIGH:** Process blocked, alert EM for resolution
  - Low confidence score requiring human judgment
  - Unknown vendor requiring research
  - Missing required data fields

- **MEDIUM:** Suboptimal outcome, log and continue
  - Minor tech warnings
  - Aging postings needing review
  - Vendor tier ambiguity

- **LOW:** Self-correctable, log and move on
  - Missing optional fields
  - Incomplete JD sections
  - Version estimate uncertainty

## Testing

All Python scripts include demo modes with sample data:

```bash
# Run any script without arguments for demo
python confidence_calculator.py
python jd_analyzer.py
python tech_stack_mapper.py
python vendor_classifier.py
python staleness_detector.py
```

Each script also accepts JSON input file for custom testing:

```bash
python confidence_calculator.py test_input.json
```

## Inter-Agent Communication

Jay communicates with:

- **Z (Candidate Manager)**: Sends submission requests, receives candidate profiles
- **Rick (Positioning Engine)**: Sends research dossiers, receives application readiness
- **EM (Orchestrator)**: Sends escalations, alerts, receives priorities

Standard message format:
```
From: jay
To: [z|rick|em]
Type: [REQUEST|RESPONSE|ESCALATION|UPDATE]
Priority: [P1-URGENT|P2-HIGH|P3-NORMAL|P4-LOW]
Timestamp: ISO-8601
Reference: [job_id|consultant_id|dossier_id]
Payload: [structured data]
Context: [brief explanation]
```

## Building on Jay

### Adding a New Skill

1. Create new directory: `workspace/skills/new-skill/`
2. Create `new_skill.py` with core logic
3. Create `SKILL.md` with documentation
4. Add to `TOOLS.md`
5. Test with demo data
6. Update workflow pipeline

### Updating Vendor Database

Edit `workspace/memory/vendor-database.md`:
1. Add new vendors as encountered
2. Update response/ghost rates quarterly
3. Reclassify tiers after 25+ submissions
4. Document changes with dates

### Learning from Errors

When an error occurs:
1. Document in `lessons-learned.md` with Lesson number
2. Implement fix (new validation rule, threshold adjustment, etc.)
3. Test that fix prevents recurrence
4. Update scoring weights if needed
5. Share learning in EM dashboard

## Architecture Standards

Jay follows these cross-agent standards:

1. **Deterministic scoring:** All math via Python scripts, never LLM estimation
2. **Full logging:** Every calculation logged to JSONL audit trail
3. **Configurable weights:** All parameters in JSON files, not hardcoded
4. **Decision hierarchy:** Hard rules > Programmatic scores > AI judgment > Human escalation
5. **Every block has a reason:** No silent rejections. Always explain.
6. **Error becomes rule:** Same mistake never happens twice.

## Performance Metrics

Jay's effectiveness is measured by:

- **Accuracy:** False positive rate (high confidence → no response)
- **Precision:** False negative rate (low confidence → got interview)
- **Speed:** Time from job posting to submission
- **Coverage:** % of consultant profiles researched each day
- **Learning:** New lessons implemented per month

## Support

For questions or issues:
- Check `SOUL.md` for mission and decision rules
- Check `TOOLS.md` for tool capabilities
- Review `lessons-learned.md` for similar past issues
- Escalate to EM for human judgment calls

---

**Version:** 1.0.0
**Last Updated:** 2026-02-15
**Status:** Production-ready
