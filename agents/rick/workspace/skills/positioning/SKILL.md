# Positioning skill

This skill contains scripts for generating candidate positioning directives and extracting/planting job description keywords.

Positioning is emphasis selection, not fabrication. The scripts help frame candidate experience in ways that maximize fit for target roles without inventing skills.

## Scripts

### position_generator.py
Generates positioning directives that guide resume customization.

Input: candidate profile (skills, experience, work history) + job analysis (role title, required/preferred skills, client industry, seniority level).

Output: structured directive with:
- Primary positioning angle (e.g., "Microservices Architect" vs "Enterprise Java Backend")
- Skills to emphasize
- Skills to de-emphasize
- Experience framing suggestions
- Keywords to plant in resume
- Version requirements

Used before calling resume generation tool.

### keyword_planter.py
Extracts JD keywords and maps them to candidate's actual experience.

Input: job description text + candidate profile.

Output: keyword mapping showing which JD keywords have:
- DIRECT PLANT: Candidate has exact skill match
- MAPPED PLANT: Candidate has equivalent skill (e.g., "Airflow" job requirement → candidate has "Step Functions")
- MISSING: Candidate lacks skill (flag gap, recommend positioning angle instead)

Used during resume generation to maximize ATS pass-through.

## Rules

- Positioning is emphasis selection, never fabrication.
- If candidate lacks a required skill, acknowledge it as a gap rather than claiming it.
- Positioning angles are customizable per role and client industry.
- Keyword mapping respects skill equivalencies (Jenkins ≈ GitLab CI, etc.).
- Every positioning directive logged with justification.
