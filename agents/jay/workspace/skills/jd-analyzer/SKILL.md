# JD Analyzer skill

Extracts and classifies job description components for analysis.

## Script

### jd_analyzer.py
Analyzes a job description and returns structured components. Accepts raw JD text + company type, returns JSON with keywords, requirements, tech contradictions, experience level, version estimates, and red flags.

Call `analyze_jd(jd_text, company_type)` to get structured analysis.

**Output includes:**
- Keywords: Technologies found, organized by category (languages, frameworks, databases, cloud, devops, methodologies)
- Requirements: Classified as MUST_HAVE, NICE_TO_HAVE, INFERRED
- Contradictions: Technology pairs that don't usually coexist (e.g., AWS + Azure in enterprise context)
- Experience level: "junior", "mid-level", "senior", "staff", or "unknown"
- Experience years: Min and max years with confidence rating
- Version estimates: Estimated versions by technology and company type
- Red flags: Indicators of low-quality postings (contradictions, unrealistic requirements, vague JD, etc.)

## Rules
- Never modify this script without human approval.
- If JD analysis produces contradictions, flag it for human review before scoring.
- Version estimates are context-aware: enterprises run N-1/N-2, startups run latest.
- Red flags feed into confidence_calculator.py scoring.
