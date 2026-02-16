# Priority engine skill

This skill orchestrates the daily prioritization cycle. It ties together the visa urgency calculator, priority calculator, and CRM data to produce the ranked candidate queue.

## Daily cycle

1. Load current consultant profiles from memory
2. Calculate visa urgency for each consultant (visa_urgency_calculator.py)
3. Determine market demand level per category (from Jay's data or defaults)
4. Determine rate tier per consultant (based on rate distribution across bench)
5. Count active submissions per consultant (from submission log)
6. Feed all inputs to priority_calculator.py
7. Produce sorted priority queue with tiers (P1/P2/P3/P4)
8. Apply any manual overrides from priority-overrides.md
9. Send queue to EM for distribution to Jay

## Rate tier classification

Rate tier is relative to the current bench:
- TOP_QUARTILE: target_rate in top 25% of active bench
- MID: target_rate in middle 50%
- BOTTOM: target_rate in bottom 25%

This is calculated programmatically from the current bench data.

## Market demand (placeholder)

Until Jay provides real market demand data:
- Java Developer: HIGH
- Python Developer: HIGH
- AI-ML Engineer: MEDIUM
- DevOps Engineer: HIGH
- Cloud Architect: MEDIUM

These defaults are overridden when Jay's research data is available.

## Manual overrides

Humans can override priorities via #human-commands. Overrides are logged in memory/priority-overrides.md with timestamp, reason, and who requested it.
