"""
Keyword Planter for Agent Rick
================================
Extracts JD keywords and maps them to candidate's actual experience.
Determines which keywords can be planted directly, which need mapping, and which are gaps.

Usage:
    from keyword_planter import plant_keywords

    result = plant_keywords(
        job_description_text,
        candidate_profile_dict
    )
"""

import json
import re
from datetime import datetime, timezone


# Skill equivalency mapping for keyword mapping
EQUIVALENCY_MAP = {
    "airflow": ["step_functions", "stepfunctions", "prefect", "dbt", "orchestration"],
    "step_functions": ["airflow", "prefect", "stepfunctions", "orchestration"],
    "jenkins": ["gitlab_ci", "gitlab-ci", "gitlabci", "circleci", "github_actions", "githubactions"],
    "gitlab_ci": ["jenkins", "circleci", "github_actions", "githubactions", "azure_devops"],
    "kubernetes": ["k8s", "docker_swarm", "dockerswarm", "openshift", "ecs"],
    "docker": ["podman", "containers", "containerization"],
    "spark": ["pyspark", "scala_spark", "hadoop", "mllib"],
    "pyspark": ["spark", "scala_spark"],
    "terraform": ["cloudformation", "cloud_formation", "ansible", "pulumi", "iac"],
    "cloudformation": ["terraform", "cloud_formation", "ansible", "pulumi"],
    "aws": ["gcp", "google_cloud", "azure", "cloud_platform", "ec2", "lambda"],
    "gcp": ["aws", "google_cloud", "azure", "cloud_platform", "bigquery"],
    "azure": ["aws", "gcp", "azure_devops", "cloud_platform"],
    "react": ["vue", "angular", "svelte", "frontend", "javascript"],
    "vue": ["react", "angular", "svelte", "frontend"],
    "angular": ["react", "vue", "frontend", "typescript"],
    "postgres": ["postgresql", "mysql", "mariadb", "oracle", "relational", "sql"],
    "mysql": ["postgres", "postgresql", "mariadb", "relational", "sql"],
    "mongodb": ["dynamodb", "dynamodb", "cassandra", "nosql", "documentdb"],
    "dynamodb": ["mongodb", "cassandra", "nosql", "table_storage"],
    "python": ["java", "go", "rust", "backend"],
    "java": ["python", "go", "kotlin", "backend"],
    "spring": ["spring_boot", "springboot", "quarkus", "micronaut"],
    "spring_boot": ["spring", "springboot", "quarkus", "micronaut"],
    "docker": ["containers", "containerd", "podman"],
    "helm": ["kustomize", "argocd", "deployment", "kubernetes"],
}


def plant_keywords(job_description: str, candidate: dict) -> dict:
    """
    Extract JD keywords and map them to candidate's skills.

    Args:
        job_description: Full job description text to extract keywords from
        candidate: Dict with keys:
            - candidate_id (str)
            - skills (list): Candidate's skills
            - work_history (list, optional): Past roles and descriptions

    Returns:
        Dict with keyword mapping:
            - direct_plant: Keywords candidate has exact match for
            - mapped_keywords: Keywords candidate has equivalents for
            - missing_keywords: Keywords candidate lacks
            - ats_pass_through_score: Coverage % (0-100)
            - recommendations: How to handle gaps
    """

    candidate_id = candidate.get("candidate_id", "")
    candidate_skills = [s.lower() for s in candidate.get("skills", [])]
    candidate_skills_str = " ".join(candidate_skills)

    # Extract keywords from JD
    required_keywords = _extract_technical_keywords(job_description)

    direct_plant = []
    mapped_keywords = []
    missing_keywords = []

    for keyword in required_keywords:
        keyword_lower = keyword.lower()

        # Check for exact match
        if keyword_lower in candidate_skills or _word_match(keyword_lower, candidate_skills_str):
            direct_plant.append({
                "keyword": keyword,
                "candidate_skill": keyword_lower,
                "mapping_type": "DIRECT",
                "confidence": "HIGH"
            })
        else:
            # Check for equivalent match
            equivalent = _find_equivalent(keyword_lower, candidate_skills)
            if equivalent:
                mapped_keywords.append({
                    "job_keyword": keyword,
                    "candidate_equivalent": equivalent,
                    "mapping_type": "MAPPED",
                    "plant_as": f"{equivalent} (equivalent to {keyword})",
                    "confidence": "MEDIUM"
                })
            else:
                missing_keywords.append({
                    "keyword": keyword,
                    "candidate_has": False,
                    "recommendation": "FLAG_AS_GAP or GROWTH_OPPORTUNITY"
                })

    # Calculate ATS pass-through score
    total_required = len(required_keywords)
    coverage = len(direct_plant) + len(mapped_keywords)
    ats_score = round((coverage / total_required * 100) if total_required > 0 else 0, 1)

    result = {
        "candidate_id": candidate_id,
        "direct_plant": direct_plant,
        "mapped_keywords": mapped_keywords,
        "missing_keywords": missing_keywords,
        "summary": {
            "total_required_keywords": total_required,
            "direct_matches": len(direct_plant),
            "mapped_matches": len(mapped_keywords),
            "missing": len(missing_keywords),
            "ats_pass_through_score": ats_score,
            "coverage_percentage": ats_score
        },
        "resume_instructions": _generate_resume_instructions(direct_plant, mapped_keywords, missing_keywords),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return result


def _extract_technical_keywords(text: str) -> list:
    """
    Extract likely technical keywords from job description.
    Looks for capitalized words, acronyms, and known tech terms.
    """
    keywords = set()

    # Patterns for tech keywords
    patterns = [
        r"\b([A-Z][a-z]+(?:Script|Framework|Platform|Tool|Engine|Service))\b",  # Capitalized tech terms
        r"\b([A-Z]{2,})\b",  # Acronyms
        r"\b(Java|Python|JavaScript|TypeScript|Go|Rust|Scala|Kotlin)\b",
        r"\b(React|Vue|Angular|Svelte)\b",
        r"\b(AWS|GCP|Azure|DigitalOcean)\b",
        r"\b(Kubernetes|Docker|Podman)\b",
        r"\b(PostgreSQL|MySQL|MongoDB|DynamoDB|Redis|Cassandra)\b",
        r"\b(Spring|Django|Flask|FastAPI|Express)\b",
        r"\b(Jenkins|GitLab|CircleCI|GitHub Actions)\b",
        r"\b(Terraform|Ansible|Pulumi|CloudFormation)\b",
        r"\b(Spark|Hadoop|Kafka|RabbitMQ)\b",
        r"\b(Machine Learning|ML|AI|TensorFlow|PyTorch|Scikit)\b",
        r"\b(Microservices|REST API|GraphQL|gRPC)\b",
        r"\b(CI/CD|DevOps|SRE|Infrastructure)\b",
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            keyword = match.group(1) or match.group(0)
            keywords.add(keyword)

    # Also extract hyphenated and underscore terms
    hyphenated = re.findall(r"\b[\w-]+(?:-|_)[\w-]+\b", text)
    keywords.update(hyphenated)

    # Convert to lowercase for consistency
    return [kw.lower().replace("-", "_").replace(" ", "_") for kw in keywords if kw]


def _word_match(keyword: str, text: str) -> bool:
    """Check if keyword appears as a complete word in text."""
    pattern = r"\b" + re.escape(keyword) + r"\b"
    return bool(re.search(pattern, text, re.IGNORECASE))


def _find_equivalent(job_keyword: str, candidate_skills: list) -> str:
    """
    Find if candidate has an equivalent skill to the job keyword.
    Returns the candidate skill if found, None otherwise.
    """
    # Normalize job keyword
    normalized_keyword = job_keyword.replace(" ", "_").replace("-", "_").lower()

    # Check direct equivalency mappings
    if normalized_keyword in EQUIVALENCY_MAP:
        candidates = EQUIVALENCY_MAP[normalized_keyword]
        for candidate_skill in candidate_skills:
            normalized_skill = candidate_skill.replace(" ", "_").replace("-", "_").lower()
            if normalized_skill in candidates or normalized_skill == normalized_keyword:
                return candidate_skill

    # Reverse lookup
    for base_skill, equivalents in EQUIVALENCY_MAP.items():
        if normalized_keyword in equivalents:
            for candidate_skill in candidate_skills:
                normalized_skill = candidate_skill.replace(" ", "_").replace("-", "_").lower()
                if normalized_skill == base_skill:
                    return candidate_skill

    return None


def _generate_resume_instructions(direct: list, mapped: list, missing: list) -> dict:
    """
    Generate instructions for resume customization based on keyword analysis.
    """
    instructions = {
        "high_priority": [],
        "medium_priority": [],
        "gaps_to_address": [],
        "overall_strategy": ""
    }

    # High priority: directly mention these keywords
    for kw in direct:
        instructions["high_priority"].append({
            "keyword": kw["keyword"],
            "action": "Plant directly in resume. High ATS signal.",
            "placement": ["skills section", "relevant project descriptions"]
        })

    # Medium priority: mention equivalents with context
    for kw in mapped:
        instructions["medium_priority"].append({
            "job_keyword": kw["job_keyword"],
            "candidate_skill": kw["candidate_equivalent"],
            "action": f"Plant as '{kw['candidate_equivalent']}' - equivalent to {kw['job_keyword']}",
            "placement": ["project descriptions", "technical summary"]
        })

    # Gaps
    for kw in missing:
        instructions["gaps_to_address"].append({
            "keyword": kw["keyword"],
            "action": "FLAG: Candidate lacks this skill. Consider flagging as growth opportunity or training area.",
            "recommendation": "Mention willingness to learn or adjacent experience"
        })

    # Overall strategy
    coverage = (len(direct) + len(mapped)) / (len(direct) + len(mapped) + len(missing)) * 100 if (len(direct) + len(mapped) + len(missing)) > 0 else 0
    if coverage >= 80:
        instructions["overall_strategy"] = "Strong keyword coverage. Emphasize direct matches. Mention mapped equivalents in context."
    elif coverage >= 60:
        instructions["overall_strategy"] = "Good coverage. Emphasize direct matches. Use mapped equivalents strategically. Mention transferable skills for gaps."
    else:
        instructions["overall_strategy"] = "Limited coverage. Emphasize any direct matches. Frame mapped equivalents strongly. Consider flagging gaps as growth areas with hiring manager."

    return instructions


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            data = json.load(f)

        job_description = data.get("job_description", "")
        candidate = data.get("candidate", {})

        result = plant_keywords(job_description, candidate)
        print(json.dumps(result, indent=2))
    else:
        # Demo
        sample_jd = """
        We are looking for a Senior Java Developer with 5+ years of experience.
        Required: Java, Spring Boot, Kubernetes, Docker, AWS, REST APIs, PostgreSQL
        Preferred: Terraform, Jenkins, Microservices, Event-driven architecture
        This is a cloud-native, DevOps-friendly team.
        """
        sample_candidate = {
            "candidate_id": "C-042",
            "candidate_name": "Ravi Kumar",
            "skills": ["Java", "Spring", "Spring Boot", "Docker", "AWS", "PostgreSQL", "REST APIs"]
        }
        result = plant_keywords(sample_jd, sample_candidate)
        print(json.dumps(result, indent=2))
