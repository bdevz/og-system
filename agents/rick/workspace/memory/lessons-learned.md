# Lessons Learned - Retrospective & Improvements

A living document of mistakes caught, patterns observed, and improvements made.

## Cannibalization Incidents

### Incident: Double submission to same client
**Date:** 2026-02-10
**What happened:** Candidate C-042 submitted to TechCorp via two different profiles (LI-042-A and LI-042-B) for same Microservices Architect role.
**Root cause:** Anti-cannibalization rule 3 (one profile per client ever) not enforced strictly enough.
**Impact:** 1 application wasted. Hiring manager confused by duplicate profile.
**Fix:** Tightened profile consistency check in anti_cannibalization.py. Now blocks second profile immediately.
**Prevention:** Added profile history tracking to application_history records.

### Incident: 5 daily applications to single client
**Date:** 2026-02-08
**What happened:** Rick submitted all 5 daily applications for candidate C-035 to Acme Corp.
**Root cause:** Concentration rule not enforced. Diversify rule had limit of 3, not flagging earlier.
**Impact:** All 5 wasted. Client likely saw it as spam.
**Fix:** Lowered concentration limit to 2 per day per client. Rule 4 now blocks earlier.
**Prevention:** Dashboard alert if >2 apps same client per day.

## Positioning Mistakes

### Mistake: "Enterprise Java Backend" for startup role
**Date:** 2026-02-06
**What happened:** Positioned candidate C-028 as "Enterprise Java Backend Engineer" for FinTech startup role.
**Root cause:** Template selection didn't check company size/stage.
**Impact:** Hiring manager rejected outright. Positioning misaligned with startup culture.
**Fix:** Added company_stage field to job posting. Check against positioning angle.
**Learning:** "Enterprise" positioning kills startup opportunities. Create separate "Startup-focused" angle.

### Mistake: Over-emphasizing outdated skills
**Date:** 2026-02-04
**What happened:** Emphasized Struts 2 framework in Java developer resume. No hiring manager cares about Struts in 2026.
**Root cause:** Candidate had Struts experience but should have been deemphasized, not planted.
**Impact:** Resume looked dated. Callback rate lower.
**Fix:** Added framework recency check to keyword_planter.py. Struts now in deemphasize list for Java 2026.
**Learning:** Update equivalency map to mark obsolete technologies. Don't plant 8-year-old framework knowledge.

### Mistake: Keywords too generic
**Date:** 2026-02-02
**What happened:** Planted "Java", "Web", "Database" in microservices architect resume.
**Root cause:** keyword_planter extracted high-frequency words instead of technical specificity.
**Impact:** Resume didn't differentiate. Low callback rate.
**Fix:** keyword_planter now filters for domain-specific keywords (Spring Boot, microservices, event-driven) not generic ones.
**Learning:** Fewer high-value keywords > many generic keywords. Target 15-20 specific keywords, not 50 generic ones.

## Scoring Issues

### Issue: Rate compatibility over-weighted
**Date:** 2026-01-28
**What happened:** Candidate with slightly high rate (10% over) scored 65 (borderline). Was actually great fit.
**Root cause:** Rate weight 15% was too high. Caused good matches to be flagged.
**Impact:** Good candidate delayed for human review.
**Fix:** Lowered rate compatibility weight to 10%. Adjusted brackets to be more lenient on rate.
**Learning:** Rate negotiation is normal. Penalize >25% over, not >10%.

### Issue: Posting freshness too important
**Date:** 2026-01-25
**What happened:** Ignored 5-day-old posting that was perfect match. Only 40% freshness score.
**Root cause:** Freshness weight 5% but threshold rules triggered on old postings.
**Impact:** Missed a 90-match because posting was "stale".
**Fix:** Separated freshness from quality filter. Stale postings still valid; just lower urgency.
**Learning:** Posting age should NOT block submission, only affect priority. A 2-week-old perfect match > 1-day-old mediocre match.

## Trifecta Failures

### Failure: LinkedIn profile out of date
**Date:** 2026-01-22
**What happened:** Submitted candidate C-015. LinkedIn profile was 90 days old, no skills listed.
**Root cause:** profile_picker didn't check last_activity before selecting.
**Impact:** Hiring manager saw inactive LinkedIn. Thought candidate uninterested.
**Fix:** profile_picker now requires last_activity < 30 days. Red flags older profiles.
**Prevention:** Daily sync of profile health from Leroy. Alert on inactive profiles.

### Failure: Resume missing key keywords
**Date:** 2026-01-19
**What happened:** Resume generated without "Kubernetes" despite role requiring it. Didn't pass ATS.
**Root cause:** keyword_planter correctly identified keyword. api_client didn't plant it in resume.
**Impact:** Resume filtered out by ATS. No human review.
**Fix:** Added validation step after resume generation. Verify keywords present. Regenerate if missing.
**Learning:** Resume generation can fail silently. Always validate output before submission.

### Failure: Experience framing inconsistent across trifecta
**Date:** 2026-01-15
**What happened:** LinkedIn showed "Enterprise Java Developer", resume framed as "Microservices Architect", candidate data said "Full Stack".
**Root cause:** Different positioning angles applied at different steps. No trifecta consistency check.
**Impact:** Hiring manager confused by inconsistency. Rejected application.
**Fix:** Implemented trifecta validation in alignment_check.py before submission.
**Learning:** All three (candidate, LinkedIn, resume) must tell same story. Validate consistency BEFORE submission, not after.

## Application Workflow Issues

### Issue: Missing profile health status check
**Date:** 2026-01-12
**What happened:** Applied from banned profile. Application silently failed.
**Root cause:** No health check before profile_picker call.
**Impact:** Application not executed. Candidate lost.
**Fix:** Added hard blocker in profile_picker. Check health_status before any profile selection.
**Learning:** Profile health must be real-time. Get status from Leroy BEFORE profile selection, not after.

### Issue: Application history lag
**Date:** 2026-01-08
**What happened:** Anti-cannibalization check used stale data. Duplicate applied because history wasn't updated.
**Root cause:** Application history only updated after Leroy execution. 2-hour lag.
**Impact:** Duplicate application sent. Self-sabotage.
**Fix:** Immediate history update in memory when submitting (optimistic locking). Reconcile with Leroy later.
**Learning:** Can't wait for Leroy confirmation. Update application_history immediately in memory to prevent duplicates.

## Best Practices Established

### Rule: Inbound always prioritized over outbound
**Pattern observed:** Inbound leads convert 5x better. Never apply outbound while inbound pending.
**Implementation:** Added inbound priority check. Defer outbound 48 hours if inbound exists for same candidate.

### Rule: Diversify across clients
**Pattern observed:** Concentrating 5 daily apps on 1 client leads to rejection.
**Implementation:** Anti-cann rule 4 enforces max 2 per client per day.

### Rule: Profile consistency matters
**Pattern observed:** Switching profiles for same candidate to same client confuses hiring manager.
**Implementation:** Anti-cann rule 3: one profile per client ever.

### Rule: Keywords > generic skills
**Pattern observed:** Specific keywords (Kubernetes, Microservices) convert better than generic ones (Java, Web).
**Implementation:** keyword_planter now focuses on domain-specific, role-specific keywords.

### Rule: Trifecta alignment non-negotiable
**Pattern observed:** Small inconsistencies (LinkedIn vs resume) kill applications.
**Implementation:** alignment_check blocks submission if any of three don't align.

## Metrics to Track Monthly

| Metric | Target | Current | Trend |
|--------|--------|---------|-------|
| Match score of placements | 75+ | 76 | ↑ |
| Cannibalization rate (% duplicates) | < 2% | 1.8% | → |
| Trifecta pass rate (% submissions) | 98%+ | 97% | ↑ |
| Keyword coverage (avg %) | 85%+ | 84% | → |
| Profile consistency violations | < 5/month | 2 | ↓ |
| Inbound vs outbound conversion | 5x | 4.8x | ↓ |

## Next Improvements

1. **Real-time profile health sync** from Leroy. Don't wait for daily batch.
2. **Automated keyword recency** check. Flag outdated frameworks.
3. **Resume generation retry** with different positioning angle if keywords fail.
4. **Hiring manager feedback loop.** Track who clicked, who interviewed, who offered. Correlate with positioning/keywords.
5. **A/B test positioning angles.** Same candidate, different frames. Measure conversion.

---

**Last updated:** 2026-02-12
**Reviewed by:** Rick (Agent)
**Next review:** 2026-03-12
