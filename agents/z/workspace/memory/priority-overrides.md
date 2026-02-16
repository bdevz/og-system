# Priority Overrides Log

Human-initiated overrides to the automated priority system. Every override is logged with attribution.

## Format

| Date | Consultant ID | Override Type | Old Value | New Value | Requested By | Reason |
|---|---|---|---|---|---|---|
| | | | | | | |

## Override types
- DEPRIORITIZE: Move consultant out of active queue (placed, on hold, personal leave)
- REPRIORITIZE: Force a specific priority tier regardless of calculated score
- HOLD: Temporarily pause all activity for a consultant
- RESUME: Return a held consultant to active queue
- DNS_ADD: Add entry to do-not-submit list
- DNS_REMOVE: Remove entry from do-not-submit list (requires reason)
- RATE_CHANGE: Update target or minimum rate

## Rules
- Overrides from #human-commands are interpreted by EM and routed to Z.
- Z applies the override and logs it here.
- Overrides persist until explicitly reversed.
- Weekly review: check if any overrides should be lifted.
