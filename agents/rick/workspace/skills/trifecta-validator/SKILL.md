# Trifecta Validator skill

This skill performs pre-application verification. Before any application leaves Rick's queue, three things must align perfectly:

1. **Candidate data**: Skills, experience, rate, visa, employment history as recorded in Z's database.
2. **LinkedIn profile**: Positioning, work history, skills endorsements, activity consistent with stated experience.
3. **Resume**: Keywords planted, versions correct, experience framing consistent with LinkedIn positioning.

If any of the three don't align, the hiring manager notices. The application gets rejected. Trifecta validation catches misalignment before submission.

## Scripts

### alignment_check.py
Pre-application verification checklist.

Returns: ALIGNED (ready to apply) or FAILED (list of failures + suggested fixes).

Validates:
- Candidate fit: match score, no DNS conflicts, no duplicates, visa compatible, rate compatible
- LinkedIn profile: health GREEN, positioning matches, limits not exceeded, no conflicts, work history consistent
- Resume: keywords planted, versions correct, experience framing consistent with LinkedIn

## Rules

- All three must align. If any fails, block submission.
- Every failure gets a suggested fix.
- Log every validation with result.
