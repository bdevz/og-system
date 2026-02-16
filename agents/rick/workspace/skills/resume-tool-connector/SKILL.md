# Resume Tool Connector skill

This skill interfaces with the resume generation tool (web app with API).

The tool accepts structured positioning directives and returns customized resumes with keywords planted, formatting applied, and versions noted.

## Scripts

### api_client.py
Connector to resume generation API.

Input: Positioning directive JSON (from position_generator.py).

Output: Generated resume text with keywords planted, formatting applied, versions correct.

Features:
- Structured input/output for easy integration
- Retry logic (max 2 retries on timeout)
- Output validation (keywords present, versions correct, no obvious errors)
- For now: well-structured stub that logs API calls. Real endpoint wired later.

## Rules

- Never submit resume without keyword validation.
- Always log API calls with request + response.
- Retry on timeout (max 2 times).
- If API returns error, escalate to human.
