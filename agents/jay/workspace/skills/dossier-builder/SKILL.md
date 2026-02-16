# Dossier Builder skill

Assembles complete research dossiers from all analysis components.

## Script

### dossier_builder.py
Compiles outputs from all other Jay skills into a standard research dossier. This is the final output sent to Rick for application positioning.

Call `build_dossier(consultant_profile, job_posting, jd_analysis, staleness_result, tech_stack_validation, vendor_info, confidence_score)` to generate complete dossier.

**Dossier structure includes:**
- Dossier ID and timestamp
- Recommendation (PASS/REVIEW/SKIP) with confidence score
- Consultant profile (skills, experience, rate, visa)
- Job details (title, company, posting age)
- Vendor assessment (tier, ghost rate, track record)
- Posting quality assessment (staleness, red flags)
- Technology analysis (match percentage, stack validation)
- Requirements analysis (MUST_HAVE, NICE_TO_HAVE, INFERRED)
- Confidence breakdown (all scoring factors)
- Risk assessment (high/moderate/low/critical)
- Action items for Rick (resume optimization, cover letter focus, required validations)
- Full metadata for auditability

**Output goes to:**
- Rick: Full dossier for positioning and application building
- Z: Submission request with risk level and recommendation

## Rules
- Never output a dossier with unresolved contradictions or tech stack validation failures.
- Dossier is final research output before submission request to Z.
- All dossiers are logged in application-history.jsonl for retrospective analysis.
- Dossier builder runs last in Jay's workflow.
