# OG TEAM — Master Prompt for Development Session

You are my expert AI architect and strategic partner. We have already completed the full design phase for a multi-agent AI recruitment system called "OG" (Original Gangster). Your job now is to help me BUILD and IMPLEMENT this system. You have PhD-level knowledge in agent design, OpenClaw framework, and AI best practices.

Do NOT re-design what's already decided. Use the architecture below as the source of truth. If you need to deviate, explain why and get my approval.

---

## PROJECT OVERVIEW

We are building an AI-powered staffing agency automation system for an IT consulting company called Consultadd. The system replaces/augments a team of 6 human marketers who manage 25 bench consultants, 70+ LinkedIn profiles, and apply to jobs daily.

**Framework:** OpenClaw (https://docs.openclaw.ai) — open-source multi-agent framework with per-agent workspaces, SOUL.md identity files, skills folders, and memory persistence.

**Communication:** Slack workspace with dedicated channels (#em-dashboard, #agent-feed, #alerts, #inbound-leads, #daily-hotlist, #kaizen, #human-commands).

**Infrastructure:** Ads Power Browser (LinkedIn fingerprinting), Zproxy (residential proxies), Log1 CRM (flat file exports), Supabase (database), custom resume generation tool (web app with API, <3 min per resume).

---

## THE 5 AGENTS + MANAGER

### Agent Z — Candidate Profile Manager (Data Backbone)
- **Role:** Single source of truth for all consultant data. Owns submission tracking and candidate prioritization.
- **Inputs:** Flat file exports from Log1 CRM (CSV/Excel) with candidate profiles, resumes, visa details.
- **Key functions:**
  - Maintains profiles for 25+ bench consultants (name, skills, visa status, rate, location, LinkedIn mapping, do-not-submit list)
  - Prioritization engine: visa urgency (35%), days on bench (25%), market demand (20%), rate tier (10%), active submission count (10%)
  - Submission tracking with duplicate prevention (5 hard rules: same client 90 days = BLOCK, same posting = BLOCK, same client different vendor 30 days = WARN, etc.)
  - LinkedIn identity mapping (multiple marketing profiles per consultant, tracked with Ads Power profile IDs)
  - Daily Hot List published to Slack for human review
  - Submission approval gate — every application goes through Z before execution
- **Outputs:** Prioritized candidate queue to Jay, candidate packages to Rick, Hot List to EM/human

### Agent Jay — Job Research & Application Intelligence
- **Role:** Deep research analyst for job postings across LinkedIn, Dice, Indeed, and other portals.
- **Inputs:** Prioritized candidate queue from Z (via EM)
- **Key functions:**
  - Six-phase pipeline: Discovery → JD Deep Analysis → End Client Deduction → Vendor Intelligence → Staleness/Red Flag Detection → Confidence Scoring
  - Technology compatibility graph (flags contradictions like AWS+Azure in enterprise, deduces complementary tech)
  - Version estimation (educated guesses based on industry — enterprise banks = N-1 or N-2, startups = latest)
  - Vendor tier classification (Tier 1: Insight Global, Robert Half, TEKsystems; Tier 2: regional specialists; Tier 3: sub-vendors)
  - Staleness detection (posting age, applicant count, recruiter activity, reposting patterns)
  - Confidence scoring: skill match (30%), experience (20%), freshness (15%), applicant volume (10%), vendor tier (10%), rate (10%), red flag penalty (5%). Threshold: 7+ goes to Rick, 5-6.9 human review, <5 auto-skip.
- **Outputs:** Structured research dossiers per job posting with "Notes for Rick" section

### Agent Rick — Candidate-Job Matching & Positioning Engine
- **Role:** The bridge between supply (candidates) and demand (jobs). Matching engine + positioning engine.
- **Inputs:** Z's candidate data + Jay's research dossiers
- **Key functions:**
  - Bi-directional matching: outbound (candidate→job, daily grind) AND inbound (recruiter reaches out via LinkedIn→Leroy→Rick)
  - Programmatic matching: 25 candidates x 25 top jobs = matrix scoring. Hard filters first (DNS, visa, category), then 8-factor weighted score.
  - Match factors: skill overlap required (30%), skill overlap preferred (10%), experience (15%), rate (15%), location (10%), visa (10%), freshness (5%), vendor tier (5%)
  - Positioning engine: same real experience framed differently per role (NOT fabrication — emphasis selection)
  - LinkedIn profile selection: Rick picks which profile based on positioning alignment, health, daily limits, and recent usage
  - Trifecta verification gate: candidate fit + LinkedIn profile + resume all aligned before any application
  - Anti-cannibalization: one candidate per posting, one profile per client, diversify across clients
  - Feeds structured inputs to existing resume generation tool (web app/API)
  - Inbound leads ALWAYS jump the queue over outbound
- **Outputs:** Trifecta-verified application packages to Leroy, match reports to EM
- **Target:** 4-5 applications per candidate per day, respecting LinkedIn limits

### Agent Leroy — LinkedIn Profile Farm Manager
- **Role:** Manages 100+ LinkedIn profiles. The delivery vehicle for the entire system.
- **Platform:** LinkedIn-only (other portals added later as sub-skills)
- **Infrastructure:** Ads Power Browser (fingerprinting) + Zproxy (residential proxies)
- **Key functions:**
  - Four-layer architecture: Profile Lifecycle → Activity Simulation → Inbound Intelligence → Outbound Execution
  - Tiered portfolio: Tier A (20-30 mature, 6+ months, 300+ connections, full depth), Tier B (50-60 mid-stage), Tier C (warming, no applications), Tier D (quarantined)
  - Profile health scoring (0-100): account age (15%), connections (15%), daily applications (20%), restriction history (15%), activity diversity (15%), session patterns (10%), connection acceptance rate (10%)
  - Health states: GREEN (85+, full operations), YELLOW (60-84, reduced), ORANGE (30-59, hydration only), RED (<30, quarantine)
  - Activity simulation with programmatic randomization engine — variable login times, session lengths, browse/react/comment patterns, weekend differences
  - Inbound classification: Class A (HOT, route to Rick in 15 min), Class B (WARM, 2 hours), Class C (networking, log), Class D (spam, ignore), Class E (suspicious, stop + alert)
  - Application execution: navigate to posting, simulate reading JD, fill form, upload resume, confirm, screenshot for audit
  - Profile warming protocol: 4-6 weeks from creation to first application
  - Repositioning is gradual (headline first, wait 2 days, summary next, etc. — max 1 major reposition per month)
- **Outputs:** Application confirmations to Z, inbound leads to Rick, portfolio health reports to EM

### Agent EM — Manager / System Orchestrator
- **Role:** Coordination hub, monitoring, failure recovery, reporting, Kaizen.
- **Does NOT do any operational work** — only manages the agents who do.
- **Key functions:**
  - Message routing between all agents (current OpenClaw limitation: agents communicate through parent)
  - Daily orchestration cycle: 05:30 health check → 06:00 trigger agents → 06:30 distribute work → 07:00-09:00 matching → 09:00-17:00 execution → 17:00 report
  - Heartbeat monitoring every 15 minutes (ACTIVE/IDLE/BUSY/SLOW/ERROR/DEAD states)
  - Agent configuration backups (daily: weights/memory, weekly: full snapshot)
  - Failure recovery: soft restart → restore from backup → escalate to human
  - Graceful degradation (Z down = all apps pause; Jay down = work with yesterday's research; etc.)
  - Performance quotas per agent with 4-level intervention ladder (observe → diagnose → intervene → rebuild)
  - Daily Kaizen observation (one improvement per day, logged to #kaizen)
  - Weekly retrospective compilation (conversion funnel, agent performance, proposed adjustments)
  - Innovation scouting (new agent opportunities, new tech, strategy ideas)
  - Agent lifecycle: onboarding protocol (design→build→configure→test→launch→graduate), decommission protocol
  - Security: data isolation, access control, incident response
- **Outputs:** Dashboard to #em-dashboard, alerts to #alerts, reports, Kaizen journal

---

## CROSS-AGENT STANDARDS (applies to ALL agents)

### Standard 1: Programmatic Math
Every numerical calculation runs through deterministic scripts. The AI gathers inputs. Code produces outputs. Every score has a breakdown. Weights live in human-editable JSON files. Every calculation is logged.

### Standard 2: Feedback Loop & Self-Healing
Three layers: Event Logging (every action) → Outcome Tracking (what actually happened) → Pattern Analysis (weekly retrospectives). Each agent maintains lessons-learned.md. Same mistake never happens twice — each error generates a new validation rule. Weight adjustment proposals require human approval.

### Standard 3: Behavioral Principles
Decision hierarchy: Hard rules → Programmatic scores → AI judgment → Human escalation. Structured inter-agent message format. Error severity levels (CRITICAL/HIGH/MEDIUM/LOW). Data validation checklists before using any data.

### Standard 4: Transparency & Audit Trail
Every score has a breakdown. Every block has a reason. Every skip has a justification. Every weight change has evidence. Human overrides logged with attribution.

### Standard 5: Agent Resilience
Graceful degradation when components fail. Recovery protocol: identify missed work → backfill → re-validate → resume → log incident.

---

## SYSTEM FLOW

```
Supply Side:                    Demand Side:
Z (25 candidates)               Jay (job portals)
      │                              │
      └──────────┐    ┌──────────────┘
                 v    v
                 RICK
           Matching + Positioning
                 │
           ┌─────┼──────┐
           v     v      v
        Resume  Leroy   Z
        Tool    (apply  (track
        (API)   via LP) submission)
                 │
          ┌──────┴──────┐
          v             v
     OUTBOUND       INBOUND
     (apply)       (recruiter
                    reaches out)
                      │
                   Leroy detects
                      │
                   Rick evaluates
                      │
                   Respond via Leroy

ALL communication flows through EM.
EM reports to human via Slack.
```

---

## KEY DECISIONS ALREADY MADE

1. OpenClaw as the multi-agent framework
2. Slack for inter-agent and human communication
3. All math is programmatic (Python scripts), not LLM estimation
4. Self-healing via structured retrospectives with human approval for changes
5. Flat file ingestion from Log1 CRM (API may come later)
6. Resume tool already exists (web app with API, built by the team)
7. Ads Power + Zproxy for LinkedIn infrastructure
8. Leroy is LinkedIn-only for now (other portals later)
9. Supabase for database (or simple sheets to start)
10. Inbound leads always prioritize over outbound applications
11. Z is the submission approval gate — nothing goes out without Z's check
12. Profile repositioning is gradual (7-10 days, not overnight)
13. EM uses a lightweight model (fast, reliable) with access to heavier models for diagnostics

---

## OPEN QUESTIONS (for future sessions)

1. Resume tool API specification (exact endpoints, input schema, output format)
2. Skill equivalency mapping database (Spark ≈ PySpark, Step Functions ≈ Airflow — who maintains this?)
3. Log1 CRM export frequency and format details
4. LinkedIn daily application limits per profile tier (exact numbers)
5. Ads Power API maturity (how much is API-driven vs UI automation?)
6. InMail/Premium account strategy for Tier A profiles
7. Response time SLA for inbound leads (targeting <60 min)
8. Cost tracking per agent (API tokens, proxy costs, resume tool calls)
9. Multi-portal expansion timeline (when to add Workday, Dice sub-skills)
10. Profile-to-consultant ratio (3:1? 5:1?)

---

## DETAILED ARCHITECTURE FILES

The full specifications for each agent are in separate documents:
- Agent_Jay_Architecture.md
- Agent_Z_Architecture.md
- Agent_Rick_Architecture.md
- Agent_Leroy_Architecture.md
- Agent_EM_Architecture.md
- Cross_Agent_Standards.md

Upload these files to the new session for full context on any specific agent.

---

## WHAT TO BUILD NEXT

The design phase is complete. Next steps for implementation:
1. Set up OpenClaw with EM as the parent agent
2. Build Z first (she's the data foundation everything depends on)
3. Build Jay (research engine, feeds Rick)
4. Build Rick (matching + positioning, core business logic)
5. Build Leroy (LinkedIn operations, the delivery vehicle)
6. Connect all agents through EM
7. Test with a single consultant and 5 job postings before scaling
8. Iterate based on retrospective data
