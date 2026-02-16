# Hot List publisher skill

This skill generates the daily Hot List for human review. Published to #daily-hotlist via EM every morning by 07:00 ET.

## Script

### hotlist_publisher.py
Call `generate_hotlist(profiles, stats, stale_submissions, alerts)` to produce the formatted output.

## Input requirements

- prioritized_profiles: output from priority_calculator (batch), sorted by score desc
- submission_stats: aggregate counts (total active, interviews, awaiting feedback, new to bench)
- stale_submissions: submissions with no status update in 7+ days
- alerts: list of alert strings (visa urgency, conflicts, data gaps)

## Output format

The Hot List follows the standard format defined in the architecture spec:
- Header with bench stats
- P1 URGENT section (score 8.0+)
- P2 ACTIVE section (5.0-7.9)
- P3 MAINTENANCE section (3.0-4.9)
- P4 LOW/ON HOLD section (below 3.0)
- Recently placed / on hold
- Stale submissions needing follow-up
- Alerts

## Rules
- Published every business day, no exceptions.
- Human can respond with overrides (which get logged in priority-overrides.md).
- Hot List is the primary human touchpoint for daily bench management.
