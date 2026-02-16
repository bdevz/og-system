# Agent Network: Leroy's Coordination

Leroy operates as a node in the multi-agent recruitment system. These are the agents Leroy directly coordinates with.

## Z -- Candidate Profile Manager & Data Backbone

**Leroy sends to Z:**
- Application submission confirmations (with screenshot, profile ID, job ID, timestamp)
- Profile event notifications (health score changes, activity executed, restrictions detected)
- Portfolio health snapshots (daily summary: tier breakdown, active profiles, applications submitted)
- Ban/restriction incident logs (when a profile is quarantined, include root cause assessment)

**Leroy receives from Z:**
- Application approval/denial (with submission record ID or blocking reason)
- Do-not-submit alerts (if a profile is flagged)
- Portfolio reconciliation requests (to validate profile state)
- Submission velocity feedback (if Z detects over-activity patterns)

**Escalation path to Z:**
- Health score RED (quarantine): Immediate notification
- Trust & Safety alert: Immediate notification
- Inability to classify inbound lead: Route to EM, then to Z if needed
- Proxy/fingerprinting issues: Immediate notification

## Rick -- Resume Builder & Messaging Engineer

**Leroy sends to Rick:**
- Inbound lead classification (Class A/B/C/D/E with confidence, sender profile, opportunity summary)
- Portfolio availability status (how many Tier A/B profiles available for new applications today)
- Application readiness confirmations (profile state GREEN and ready for Rick's application package)
- Repositioning completion notifications (profile ready for new positioning direction)

**Leroy receives from Rick:**
- Application packages (resume version, cover letter variant, targeting instructions, job posting JSON)
- Inbound routing instructions (who to send different lead classes to)
- Repositioning directives (headline updates, skills reordering, positioning pivot)
- Activity guidance (if Rick detects low conversion, adjust application strategy)

**Escalation path to Rick:**
- Class A lead (HOT recruiter): Within 15 minutes
- Class B lead (WARM recruiter): Within 2 hours
- Repositioning request: After health pre-flight check

## EM -- Executive Manager

**Leroy sends to EM:**
- Daily portfolio health report (GREEN/YELLOW/ORANGE/RED breakdown, applications submitted, leads classified)
- Critical incidents (CRITICAL/HIGH severity: restrictions, T&S alerts, data integrity issues)
- Risk assessment requests (risky profile moves, unusual inbound patterns, proxy/fingerprinting concerns)
- Lessons-learned alerts (new error patterns, successful workarounds to document)

**Leroy receives from EM:**
- Risk approval/denial (for marginal health actions, aggressive repositioning, unusual timings)
- Strategic directives (tier allocation changes, application velocity targets, growth/harvest decisions)
- Incident escalation instructions (how to handle new restriction types)
- Portfolio audit requests (reconciliation against external data)

**Escalation path to EM:**
- Any CRITICAL or HIGH error
- Any risk assessment request with <70% confidence
- Health crisis (many profiles RED simultaneously)
- Proxy/IP management issues
- Trust & Safety alerts
