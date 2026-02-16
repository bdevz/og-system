# User Context: Leroy's Operating Environment

## Organization

Consultadd is an IT consulting company operating a bench of technical consultants. Leroy manages the LinkedIn profile farm that represents these consultants to the market.

## Portfolio

Leroy manages 100+ LinkedIn profiles across 4 tiers:

**Tier A (10-15 profiles):** Thoroughbred profiles
- Account age: 6+ months, well-established
- Connection count: 300+ strategically built
- Daily activity: 15-30 minutes per day
- Application frequency: 2-5 applications per day
- Activity types: Applications, profile interactions, targeted connection requests
- Use case: Active outbound pipeline, high-velocity applications
- Health target: GREEN only (avoid YELLOW)

**Tier B (20-30 profiles):** Growth profiles
- Account age: 3-6 months
- Connection count: 100-300
- Daily activity: 10-20 minutes per day or every other day
- Application frequency: 0-2 applications per day
- Activity types: Lighter applications, connection building, warming activity
- Use case: Growing pipeline, position building
- Health target: GREEN/YELLOW (with YELLOW activity reduction)

**Tier C (40-60 profiles):** Warming profiles
- Account age: 1-3 months
- Connection count: 50-150
- Activity frequency: Every 2-3 days, 5-10 minutes
- Application frequency: 0-1 application per 3 days
- Activity types: Profile views, reactions, connections, minimal applications
- Use case: Trust building, brand presence, future capacity
- Health target: GREEN only (protect account early life)

**Tier D (20-40 profiles):** Dormant/Reserve profiles
- Activity: Zero activity until repositioning/warming complete
- Use case: Reserve capacity, experimental profiles
- Health target: Not tracked (no activity)

## Infrastructure

### LinkedIn Automation

**Ads Power Browser:**
- Browser fingerprinting and device emulation
- Residential IP rotation via integrated proxy management
- Session isolation per profile
- Screenshot capture for audit trails
- Real-time profile state inspection

**Zproxy (Residential Proxies):**
- Rotating residential IP pool
- Geographic targeting (US-based primarily)
- IP reputation management
- Proxy allocation per profile per day

### External Services

- Ads Power API: Profile state, activity simulation, screenshot capture
- Zproxy API: IP allocation, rotation, reputation checks
- LinkedIn: Public API (limited scope), browser-based interactions (Ads Power)

## Operational Constraints

### LinkedIn Safety Constraints

- Daily application limits: 6 applications per profile per day (hard limit)
- Connection request limits: 20 per profile per day (soft limit, varies)
- Message response time: 24-72 hours to inbound messages
- Account age minimum: 7 days before first application attempt
- Daily active time: 2-4 distinct sessions per profile
- Session duration: 5-30 minutes depending on tier

### Proxy & Fingerprinting

- One IP per profile per day maximum
- IP reputation must be >70% (checked via Zproxy API)
- Residential proxy required (not datacenter)
- Browser fingerprint consistency per profile
- Device emulation randomization (within reason)
- Geolocation alignment with candidate profile location

### Rate Limits & Quotas

- Portfolio application ceiling: 20-30 applications per day across all profiles (target: 25/day)
- Per-profile daily max: Tier A=5, Tier B=2, Tier C=1, Tier D=0
- Connection request ceiling: 100 per day across all profiles (target: 80/day)
- Message classification SLA: 15 min for Class A, 2 hours for Class B

## Workflow Integrations

### With Z (submission approval)
1. Leroy identifies opportunity from Rick's package
2. Leroy checks profile health (must be GREEN for Tier A/B, GREEN for new Tier C)
3. Leroy requests Z approval with profile ID, job ID, daily application count
4. Z responds with APPROVED + submission record ID, or BLOCKED + reason
5. If APPROVED, Leroy executes application
6. Leroy sends Z screenshot + confirmation within 5 minutes

### With Rick (inbound lead routing)
1. LinkedIn message arrives to portfolio profile
2. Leroy classifies inbound message within 15 minutes
3. If Class A: Route to Rick immediately with full sender context
4. If Class B: Queue for Rick with 2-hour window
5. If Class C/D/E: Log and continue

### With EM (daily reporting)
1. Daily at 19:00 ET, Leroy generates portfolio health snapshot
2. Report includes: GREEN/YELLOW/ORANGE/RED breakdown, applications submitted today, leads routed, any MEDIUM/HIGH/CRITICAL alerts
3. Any CRITICAL alerts sent immediately, not batched

## Key Metrics Leroy Tracks

- Portfolio health score distribution (aggregate by state)
- Applications submitted per day (actual vs. target)
- Application success rate by tier (leading indicator for health)
- Inbound leads received and routed (by class)
- Profile restrictions/bans (monthly trend)
- Proxy IP rotation efficiency (IPs used, reputation maintained)
- Time-to-classification for inbound leads (SLA adherence)
- Profile repositioning progress (% of Tier C profiles ready to advance)
