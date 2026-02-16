# Tech Stack Mapper skill

Maps technology relationships and validates technology combinations.

## Script

### tech_stack_mapper.py
Maps a technology stack, finding relationships, contradictions, and version estimates. Accepts list of techs + company type, returns relationships, warnings, and validation results.

Call `map_tech_stack(tech_list, company_type)` to validate and enrich a technology stack.

**Output includes:**
- Complementary technologies: What typically goes with each tech
- Contradictions: Technologies that shouldn't coexist (AWS + Azure, Kubernetes + Docker Swarm, etc.)
- Missing requirements: Dependencies that are required but not present (Spring Boot requires Java, etc.)
- Version estimates: By company type (enterprise runs N-1/N-2, startups run latest)
- Warnings: List of validation issues
- Validation passed: Boolean flag

## Technology relationships
- Java pairs with Spring Boot, databases (PostgreSQL, MySQL, Oracle)
- Spring Boot requires Java, pairs with Spring Cloud, Spring Data
- Kubernetes requires Docker, pairs with Helm, CI/CD
- React pairs with Node.js, TypeScript, build tools
- Python pairs with Django, FastAPI, Flask
- Cloud providers (AWS, Azure, GCP) typically don't mix in same org

## Rules
- Never modify this script without human approval.
- If tech stack validation fails (contradictions or missing requirements), flag for human review.
- Version estimates are context-aware: enterprises run N-1/N-2, startups run latest.
- Validation results feed into JD analysis red flags.
