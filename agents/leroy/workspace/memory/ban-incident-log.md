# Ban & Incident Log

This log records every profile ban, restriction, warning, or major incident with root cause analysis and recovery actions taken.

## Format

Each incident follows this template:

```
## INCIDENT: [Date] [Profile ID] - [Type]

**Severity:** CRITICAL | HIGH | MEDIUM | LOW

**Timeline:**
- [Time]: Event detected
- [Time]: Action taken

**Incident Details:**
- Profile: [P-XXXX]
- Account age: X days
- Daily apps that day: X
- Health state: GREEN/YELLOW/ORANGE/RED

**Root Cause Analysis:**
- Primary: [Most likely cause]
- Contributing factors:
  - [Factor 1]
  - [Factor 2]

**LinkedIn Signal:**
- Message/Warning: [Exact text if captured]
- Restriction type: [Application block, message limit, warning banner, etc.]
- Scope: [This profile only, or multiple profiles affected]

**Recovery Actions:**
- [Action 1]
- [Action 2]
- Timeline to normal: [Expected recovery time]

**Preventive Measures:**
- [Rule added/modified]
- [Monitoring increased]
- [Activity adjusted]

**Lessons Learned:**
- [Key insight 1]
- [Key insight 2]

---
```

## Active Incidents

None recorded yet. This portfolio is new.

## Historical Incidents

### INCIDENT: 2026-02-15 P-TEST-001 - Rate Limit Warning

**Severity:** MEDIUM

**Timeline:**
- 2026-02-15 14:32 UTC: Rate limit warning detected on application attempt
- 2026-02-15 14:33 UTC: Profile quarantined to HYDRATION mode
- 2026-02-15 14:35 UTC: Z alerted with incident report

**Incident Details:**
- Profile: P-TEST-001
- Account age: 45 days
- Daily apps that day: 4
- Health state: YELLOW (already reduced)
- Proxy IP: 192.0.2.10

**Root Cause Analysis:**
- Primary: Daily application rate too high for health state
- Contributing factors:
  - Health state was YELLOW (should limit to 2 apps/day)
  - 4 applications on YELLOW state profile = 2x limit
  - Account age 45 days (still in growth phase)

**LinkedIn Signal:**
- Message: "You're applying too quickly. Please slow down."
- Restriction type: Temporary application submission block
- Scope: Single profile

**Recovery Actions:**
- Reduced to HYDRATION activity (browse, react, no applications)
- Increased 24-hour session gaps
- Monitored daily for health improvement
- No applications for 3 days
- Re-evaluated health on 2026-02-18

**Preventive Measures:**
- Added stricter YELLOW state enforcement in schedule_generator
- Daily app counts now hard-capped at 2 for YELLOW profiles
- Preflight check strengthened to block if daily count >= 2 and YELLOW

**Lessons Learned:**
- Health state must drive daily limits immediately, not as suggestion
- YELLOW state means reduced activity is not optional
- Monitor daily application counts more closely

---

## Incident Categories

### Ban Incidents (CRITICAL)

Profile permanently restricted or banned from LinkedIn.

Causes:
- Repetitive rate limit violations
- Proxy IP detected as datacenter
- Profile activity pattern too mechanical
- Trust & Safety alert triggered
- Mass connection requests without engagement

Recovery: Profile typically unrecoverable. Flag for sunsetting.

---

### Restriction Incidents (HIGH)

Application submission or messaging temporarily restricted.

Causes:
- High application rate (6+ per day)
- Multiple rate limit warnings
- Unusual activity detected
- Too many failed applications

Recovery: 2-7 days in HYDRATION mode, then gradual resumption.

---

### Warning Incidents (MEDIUM)

Warning banner or message appears but functionality not blocked.

Causes:
- Moderate rate limit (4-5 apps/day on growing account)
- Suspicious pattern detected
- Connection request spike

Recovery: 1-3 days reduced activity, monitor closely.

---

### Anomaly Incidents (LOW)

Unexpected behavior, form changes, or system issues.

Causes:
- LinkedIn UI changes
- Unexpected form fields
- External ATS redirects
- Temporary network issues

Recovery: Log and monitor. Usually self-resolving.

---

## Statistics Summary

**Total Incidents (Lifetime):** 1
- CRITICAL: 0
- HIGH: 0
- MEDIUM: 1
- LOW: 0

**Most Common Root Cause:** Daily application rate violations
**Most Effective Prevention:** Strict health state enforcement
**Average Recovery Time:** 3 days

---

## Monitoring Checklist

Daily monitoring should include:

- [ ] Check for new warning banners on any profile
- [ ] Verify no profiles in RED health state
- [ ] Review applications submitted vs. daily limit
- [ ] Check connection request rates within tier limits
- [ ] Monitor proxy IP reputation (>70% threshold)
- [ ] Inspect session patterns for mechanical behavior
- [ ] Review any new error messages from Ads Power

---

## Escalation Path

1. **Detection:** Leroy monitors activity, spots warning/restriction
2. **Quarantine:** Profile moved to ORANGE/RED state immediately
3. **Alert:** Human notified, Z notified (especially for applications in progress)
4. **Analysis:** Root cause analysis performed
5. **Recovery:** Gradual activity resumption per profile state
6. **Documentation:** Incident logged with lessons learned
7. **Prevention:** Rules updated to prevent recurrence

---

## Notes

- Every incident is an opportunity to learn and improve rules
- Pattern analysis: if multiple profiles hit same issue, it's a system-level problem
- Trust & Safety incidents require immediate escalation (do not attempt recovery)
- Document everything: detection time, exact message, account metrics, recovery steps
