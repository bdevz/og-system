# LinkedIn Selector skill

This skill selects the optimal LinkedIn profile for each candidate-job match.

A candidate may have multiple LinkedIn profiles managed by Leroy. Each has different positioning, profile health, application counts, and history. This skill picks the best profile for each application.

## Scripts

### profile_picker.py
Selects the best LinkedIn profile for a given candidate and target role.

Considers:
1. Role alignment: Does this profile's positioning match the target role?
2. Profile health: GREEN/ACTIVE status? Not banned? Not at daily limit?
3. Application count today: Hasn't hit 5-per-day max?
4. Recent usage: Avoid applying to competing roles same day from same profile.
5. Inbound history: Keep consistent if this candidate got recent inbound from this role type.

Input: candidate's profiles list + target role + application history + profile health status.

Output: selected profile ID with detailed reasoning.

## Rules

- Never select a profile that's banned, inactive, or at daily limit.
- Prefer profiles with recent success (interview callbacks, inbound leads).
- Avoid profile conflicts (same profile applying to competing roles same day).
- Keep consistent if candidate has inbound from same role type (don't switch profiles).
