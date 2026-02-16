# Technology Version Baseline

Estimated technology versions by industry type. Used for version compatibility checking and to identify outdated or cutting-edge requirements.

## Enterprise (Conservative adoption, N-1/N-2 versions)

Banks, insurance, government, Fortune 500 companies typically run established versions.

| Technology | Typical Version | Rationale | Min Acceptable | Max Used |
|---|---|---|---|---|
| Java | 11 or 17 | LTS versions preferred | 8 | 21 |
| Spring Boot | 2.7.x | Mature, stable | 2.x | 3.x |
| Python | 3.8 or 3.9 | Stability focus | 3.6 | 3.11 |
| React | 16.x or 17.x | Mature, stable | 15.x | 18.x |
| Angular | 12+ | Enterprise support | 10+ | 16+ |
| PostgreSQL | 11+ | Reliable | 9.6 | 14+ |
| MySQL | 5.7 or 8.0 | Stability | 5.6 | 8.0 |
| Kubernetes | 1.24+ | Recent but stable | 1.20+ | 1.28 |
| Docker | 20.x or 23.x | Recent | 18.x | 24.x |
| AWS | Any recent region | Cloud-agnostic | Any | Latest |
| Azure | Any recent region | Cloud-agnostic | Any | Latest |

## Mid-market (Balanced adoption, current N-1 versions)

Growing companies, mid-sized tech firms, startups with funding.

| Technology | Typical Version | Rationale | Min Acceptable | Max Used |
|---|---|---|---|---|
| Java | 11 or 17 | Mix of LTS and current | 8 | 21 |
| Spring Boot | 3.x | Current stable | 2.x | 3.x |
| Python | 3.9 or 3.10 | Recent but stable | 3.7 | 3.11 |
| React | 18.x | Current | 16.x | 19.x |
| Angular | 14+ | Recent | 12+ | 17+ |
| PostgreSQL | 13+ | Recent | 12+ | 15+ |
| MySQL | 8.0+ | Current | 5.7 | 8.0 |
| Kubernetes | 1.25+ | Recent | 1.23+ | 1.28 |
| Docker | 23.x | Current | 20.x | 24.x |
| Node.js | 18.x or 20.x | LTS | 16.x | 20.x |
| TypeScript | 4.8+ | Recent | 4.0+ | 5.x |

## Startup (Bleeding edge, latest versions)

Early-stage companies, tech-forward organizations, greenfield projects.

| Technology | Typical Version | Rationale | Min Acceptable | Max Used |
|---|---|---|---|---|
| Java | 17 or 21 | Latest LTS | 17 | 21+ |
| Spring Boot | 3.x | Latest | 3.x | 3.x |
| Python | 3.10 or 3.11 | Latest | 3.9 | 3.12+ |
| React | 18.x or 19.x | Latest | 18.x | 19.x+ |
| Angular | 16+ | Latest | 15+ | 17+ |
| PostgreSQL | 14+ | Latest | 13+ | 16+ |
| MySQL | 8.0+ | Latest | 8.0 | 8.0 |
| Kubernetes | 1.26+ | Latest | 1.25+ | 1.28 |
| Docker | 24.x | Latest | 23.x | 24.x |
| Node.js | 20.x | Latest LTS | 18.x | 21+ |
| TypeScript | 5.x | Latest | 4.9+ | 5.x+ |

## Red flags for version conflicts

These combinations typically indicate:
- Outdated job descriptions (not updated)
- Contradictory requirements
- Body shop copy-paste errors

| Combination | Issue | Recommendation |
|---|---|---|
| Java 8 + Spring Boot 3.0 | Incompatible | Escalate - likely error in JD |
| Python 2.7 | End-of-life | Flag as outdated requirement |
| React 15 + TypeScript 5 | Unusual mix | Likely copy-paste error |
| Kubernetes 1.10 | Very outdated | Flag as stale posting |
| AWS + Azure + GCP | Cloud strategy unclear | Escalate - likely multi-cloud but unusual |

## Version estimation rules

1. **If version explicitly stated in JD:** Use stated version
2. **If only tech name stated:**
   - Enterprise: Use N-1/N-2 baseline
   - Startup: Use current/latest baseline
3. **If version seems outdated (>5 years):** Flag as red flag
4. **If version is newer than available:** Flag as error
5. **If contradictory versions:** Flag as red flag and escalate

## Update schedule

- Update quarterly based on new releases
- Monitor major version releases in each tech
- Track EOL (end-of-life) dates for older versions
- Adjust baselines annually based on industry trends
