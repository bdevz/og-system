# Kaizen Skill -- Continuous Improvement Tracking

## Purpose

Log daily improvement observations and track them for systematic learning. Kaizen (continuous improvement) is a core principle: every day, EM captures one improvement idea, lesson learned, or process optimization.

## Categories

- **PROCESS:** Workflow improvements, automation opportunities, handoff optimizations
- **QUALITY:** Error prevention, data validation, accuracy improvements
- **SPEED:** Performance optimizations, bottleneck reduction, cycle time improvements
- **COST:** Cost savings, resource optimization, efficiency gains
- **RISK:** Risk mitigation, safety improvements, failure prevention

## Daily logging

Every day at 17:45, EM logs one Kaizen observation to kaizen-journal.md with:

- Date (YYYY-MM-DD)
- Category (PROCESS, QUALITY, SPEED, COST, RISK)
- Observation (what did we notice today?)
- Root cause (why does it matter?)
- Proposed action (what could we try?)
- Evidence (what data supports this?)
- Status (proposed / approved / implemented / rejected)

## Weekly digest

Every Friday 17:30, EM compiles weekly Kaizen log for the retrospective:

- All observations from the week
- Categorized by type
- Approved items highlighted
- Implemented improvements shown with results

## Human interaction

Observations start as "proposed". Human can:
- Approve: Move to "approved" status. EM implements next cycle.
- Reject: Move to "rejected" status with reason.
- Defer: Keep as "proposed" for later decision.

Approved improvements are tracked for implementation and validation.

## Examples

**PROCESS:** "Z's Hot List publication moved from 06:45 to 06:55 avg. Added extra validation step last week. Marginal impact. Proposal: revert validation step or parallelize it."

**QUALITY:** "Profile ban incident this week. Proposal: add new alert when profile approaches rate limit (85% of daily cap), allow reactive rotation."

**SPEED:** "Rick's matching cycle hit 09:12 on Wednesday due to sequential trifecta checking. Sequential can handle 135 apps but struggles with >150. Proposal: implement parallel matching."

**COST:** "Analyzed end-client deduction accuracy. Jay's deductions 100% accurate. Cost saved by preventing bad-fit submissions: ~$2K/week in avoided recruitment fee disputes."

**RISK:** "Two duplicate submission near-misses this week (caught by Z). Proposal: add ML model to predict likelihood of 90-day duplicate before submission even reaches Z."
