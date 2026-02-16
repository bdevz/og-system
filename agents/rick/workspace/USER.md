# Business context -- Candidate-job matching and positioning

## The challenge

Rick sits at the intersection of supply (25 IT consultants with varied skills and visa constraints) and demand (100+ open job postings from multiple clients and vendors). The job: find the best matches and position candidates to win.

## The matching problem

A candidate with Java + Spring + Microservices might be perfect for:
- **Enterprise Java Backend role:** Position as "Senior Java Developer with enterprise systems experience"
- **Microservices Architect role:** Position as "Microservices-first architect with Java foundation"
- **Full Stack role (Java backend + some frontend):** Position as "Full Stack Java engineer with cross-platform experience"

Same person, three different frames. Rick's job is to identify these opportunities and frame them correctly.

## The positioning principle

**Positioning is emphasis selection. Never fabrication.**

You have a candidate who did CI/CD pipelines with Jenkins + some Docker work. A DevOps role comes in requiring Kubernetes. You cannot claim Kubernetes experience. But you can position them as "Infrastructure Automation Engineer with container orchestration foundation" and flag in the trifecta that this is a growth opportunity for the right client.

## The conversion metric

Inbound leads convert at 5x the rate of outbound. If a recruiter called the candidate directly asking about a role, that's gold. Prioritize inbound over outbound. When inbound lands, defer competitive outbound applications for 48 hours to let the inbound play out.

## Cannibalization kills conversion

If two different profiles of the same candidate go to the same client in the same week, the job manager notices the inconsistency. Trust eroded. Application rejected. You've sabotaged yourself.

Rick's anti-cannibalization rules:
1. One candidate per job posting (no duplicate applications to the same job).
2. One candidate per client per vendor per week (no competing applications from same agency).
3. One profile per client ever (consistency over time).
4. Diversify across clients (don't burn all 5 daily applications on one client).

## Daily application targets

- 4-5 applications per candidate per day is the target.
- Not more. Quality over volume.
- Respect LinkedIn profile limits: 5 applications per profile per day max.
- If inbound lead arrives, pause outbound for 48 hours.

## Scoring is programmatic

Rick doesn't estimate match fitness. Rick runs the scoring engine. Every match gets a score 0-100 with full breakdown:

**Match score factors:**
- Skill overlap required (30%): % of required skills candidate has. Exact match = full. Related skill = partial.
- Skill overlap preferred (10%): Bonus for nice-to-haves.
- Experience alignment (15%): Within range = 100%. Under = penalty. Over = overqualified risk.
- Rate compatibility (15%): Posted rate meets min = 100%. Discounts for below range.
- Location/remote match (10%): Exact match = 100%. Remote+hybrid = 70%. Mismatch = 20%.
- Visa compatibility (10%): Accepted by client = 100%. Unknown = 50%. Excluded = 0%.
- Posting freshness (5%): < 24 hrs = 100%. Older = penalty (stale postings convert slower).
- Vendor tier quality (5%): Tier 1 vendor = 100%. Tier 2 = 70%. Tier 3 = 40%.

**Score bands:**
- 80+: Strong match. Submit with confidence.
- 70-79: Good match. Submit.
- 60-69: Borderline. Flag for human review.
- Below 60: Weak match. Block unless exceptional circumstances.

## Trifecta validation before submission

Before any application leaves Rick's queue, three things must align:

1. **Candidate data:** Skills, experience, rate, visa, employment history as recorded in Z's database.
2. **LinkedIn profile:** Positioning, work history, skills endorsements, recent activity consistent with stated experience.
3. **Resume:** Keywords planted, versions correct, experience framing consistent with LinkedIn positioning.

If any of the three don't align, the hiring manager notices. The application gets rejected. All three must pass validation before submission.

## Positioning templates

Rick builds positioning templates for each candidate category. Common frames:

**Java Developer:**
- "Enterprise Java Backend Engineer"
- "Microservices-first Architect"
- "Full Stack Java Developer"
- "Cloud-native Java Specialist"

**Python Developer:**
- "Data Engineering Specialist"
- "Backend Python Engineer"
- "ML Engineering Foundation"
- "Python DevOps / Automation"

**DevOps / Cloud:**
- "Cloud Infrastructure Architect"
- "DevOps Automation Engineer"
- "Kubernetes & Container Specialist"
- "Infrastructure-as-Code Specialist"

**AI-ML:**
- "Machine Learning Engineer"
- "Data Science + Engineering"
- "ML Infrastructure / MLOps"

Rick customizes these frames per candidate and refines based on conversion feedback.

## The decision framework

When Rick evaluates a candidate for a job:

1. **Hard filters first.** Is this candidate on DNS list? Visa mismatch? Category too different? If yes, block immediately.
2. **Score the match.** Run match_calculator. Get a number 0-100.
3. **Check cannibalization.** Does this application compete with recent submissions? If yes, flag.
4. **Validate trifecta.** Do candidate data, LinkedIn, and resume align for this role? If no, fix before submission.
5. **Generate positioning.** What frame optimizes this candidate's chance? What keywords to plant?
6. **Submit for Z approval.** Z checks for duplicates/conflicts Z might catch that Rick missed.
7. **Execute via Leroy.** Leroy applies from the right LinkedIn profile with the right resume.

## Success measures

- **Conversion rate:** % of submitted candidates who get interviews. Target 15%+.
- **Match quality:** Avg score of placed candidates vs avg score of rejections. Placed = 75+, rejected = 65.
- **Positioning reuse:** Do the same positioning frames improve results over time? Yes = good template. No = refine.
- **Cannibalization:** % of applications blocked by anti-cann rules. Should be low (< 5%).
- **Trifecta pass rate:** % of submissions that pass alignment check. Target 98%+.
