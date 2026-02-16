"""
Tech Stack Mapper for Agent Jay
================================
Maps technology relationships, flags contradictions, estimates versions.
Input: set of technologies. Output: complementary techs, contradictions, version estimates.

Usage:
    from tech_stack_mapper import map_tech_stack, check_contradictions

    result = map_tech_stack(
        ["Java", "Spring Boot", "Kubernetes", "Docker", "PostgreSQL"],
        company_type="enterprise"
    )
"""

import json
from typing import List, Dict, Tuple, Set
from pathlib import Path


# Technology relationships: what goes with what
TECH_RELATIONSHIPS = {
    "Java": {
        "complementary": ["Spring Boot", "Maven", "Gradle", "JUnit", "Mockito", "Spring Data"],
        "frameworks": ["Spring Boot", "Jakarta EE", "Quarkus"],
        "databases": ["PostgreSQL", "MySQL", "Oracle", "DB2"],
        "tools": ["Maven", "Gradle", "Git", "Jenkins"],
    },
    "Spring Boot": {
        "complementary": ["Java", "Spring Data", "Spring Security", "Spring Cloud", "Spring Actuator"],
        "requires": ["Java"],
        "databases": ["PostgreSQL", "MySQL", "MongoDB", "H2"],
    },
    "Python": {
        "complementary": ["Django", "FastAPI", "Flask", "NumPy", "Pandas", "TensorFlow"],
        "frameworks": ["Django", "FastAPI", "Flask"],
        "databases": ["PostgreSQL", "MySQL", "MongoDB"],
    },
    "Django": {
        "complementary": ["Python", "Django REST Framework", "Celery", "PostgreSQL"],
        "requires": ["Python"],
    },
    "Kubernetes": {
        "complementary": ["Docker", "Helm", "kubectl", "CI/CD", "Container Registry"],
        "requires": ["Docker"],
        "tools": ["Helm", "Istio", "Prometheus"],
    },
    "Docker": {
        "complementary": ["Kubernetes", "Docker Compose", "Container Registry", "CI/CD"],
        "can_pair_with": ["Kubernetes", "Docker Swarm"],
    },
    "React": {
        "complementary": ["Node.js", "TypeScript", "Redux", "Jest", "Webpack"],
        "backend": ["Node.js", "Python", "Java"],
    },
    "Angular": {
        "complementary": ["TypeScript", "RxJS", "Jasmine", "Karma"],
        "backend": ["Node.js", "Python", "Java"],
    },
    "AWS": {
        "complementary": ["EC2", "S3", "RDS", "Lambda", "DynamoDB", "CloudWatch"],
        "does_not_pair_with": ["Azure", "GCP"],  # Usually one cloud per org
    },
    "Azure": {
        "complementary": ["App Service", "Azure SQL", "Cosmos DB", "Azure Functions"],
        "does_not_pair_with": ["AWS", "GCP"],
    },
    "GCP": {
        "complementary": ["Cloud Run", "Cloud SQL", "Firestore", "Pub/Sub"],
        "does_not_pair_with": ["AWS", "Azure"],
    },
    "PostgreSQL": {
        "complementary": ["pgAdmin", "Flyway", "Liquibase"],
    },
    "MongoDB": {
        "complementary": ["Mongoose", "Mongo Atlas"],
    },
    "Kafka": {
        "complementary": ["Schema Registry", "Confluent", "Zookeeper"],
    },
    "CI/CD": {
        "complementary": ["Jenkins", "GitLab CI", "GitHub Actions", "CircleCI"],
        "tools": ["Jenkins", "GitLab", "GitHub", "CircleCI"],
    },
}

# Contradictions: these shouldn't appear together in same enterprise environment
TECH_CONTRADICTIONS = [
    # Cloud providers
    ("AWS", "Azure"),
    ("AWS", "GCP"),
    ("Azure", "GCP"),
    # Orchestration
    ("Kubernetes", "Docker Swarm"),
    # ORM/data layer
    ("Hibernate", "JPA"),  # Usually one choice
    ("Sequelize", "TypeORM"),  # Node ORMs
    # Backend frameworks (usually pick one per codebase)
    ("Spring Boot", "Quarkus"),
    ("Django", "FastAPI"),  # Usually one choice
    ("Express", "Fastify"),  # Node frameworks
    # Frontend frameworks
    ("React", "Angular"),
    ("React", "Vue"),
    ("Angular", "Vue"),
]

# Version compatibility rules
VERSION_COMPATIBILITY = {
    "Java": {
        "8": {"Spring Boot": ["1.x", "2.x"], "Quarkus": None},
        "11": {"Spring Boot": ["2.x", "3.x"], "Quarkus": ["2.x", "3.x"]},
        "17": {"Spring Boot": ["3.x"], "Quarkus": ["2.x", "3.x"]},
    }
}

# Industry-specific tech adoption patterns
INDUSTRY_VERSIONS = {
    "enterprise": {
        "Java": "11 or 17",
        "Spring Boot": "2.7.x",
        "Python": "3.8 or 3.9",
        "React": "16.x or 17.x",
        "PostgreSQL": "11+",
        "Kubernetes": "1.24+",
    },
    "mid-market": {
        "Java": "11 or 17",
        "Spring Boot": "3.x",
        "Python": "3.9 or 3.10",
        "React": "18.x",
        "PostgreSQL": "13+",
        "Kubernetes": "1.25+",
    },
    "startup": {
        "Java": "17 or 21",
        "Spring Boot": "3.x",
        "Python": "3.10 or 3.11",
        "React": "18.x or 19.x",
        "PostgreSQL": "14+",
        "Kubernetes": "1.26+",
    },
}


def check_contradictions(tech_list: List[str]) -> List[Tuple[str, str]]:
    """
    Check if any contradictory technologies appear in the list.
    Returns list of (tech1, tech2) tuples that contradict.
    """
    tech_set = set(tech_list)
    contradictions = []

    for tech1, tech2 in TECH_CONTRADICTIONS:
        if tech1 in tech_set and tech2 in tech_set:
            contradictions.append((tech1, tech2))

    return contradictions


def get_complementary_techs(tech_list: List[str]) -> Dict[str, List[str]]:
    """
    For each tech in the list, return complementary/related technologies.
    Returns dict mapping tech -> list of recommended complementary techs.
    """
    result = {}

    for tech in tech_list:
        if tech in TECH_RELATIONSHIPS:
            complementary = TECH_RELATIONSHIPS[tech].get("complementary", [])
            # Filter to only those not already in the list
            result[tech] = [t for t in complementary if t not in tech_list]
        else:
            result[tech] = []

    return result


def check_version_compatibility(tech1: str, version1: str, tech2: str) -> bool:
    """
    Check if tech2 is compatible with tech1 at the given version.
    Returns True if compatible or compatibility unknown, False if incompatible.
    """
    # Very simplified version check
    # A real implementation would use semantic versioning
    return True  # Default to compatible if not in our knowledge base


def estimate_versions(tech_list: List[str], company_type: str = "mid-market") -> Dict[str, str]:
    """
    Estimate technology versions based on company type.
    Returns dict mapping tech -> estimated version.
    """
    if company_type not in INDUSTRY_VERSIONS:
        company_type = "mid-market"

    versions = {}
    industry_map = INDUSTRY_VERSIONS[company_type]

    for tech in tech_list:
        if tech in industry_map:
            versions[tech] = industry_map[tech]
        else:
            versions[tech] = "unknown"

    return versions


def map_tech_stack(tech_list: List[str], company_type: str = "mid-market") -> dict:
    """
    Map a technology stack, finding relationships, contradictions, and version estimates.

    Args:
        tech_list: List of technology names
        company_type: "enterprise", "mid-market", or "startup"

    Returns:
        Dict with relationships, contradictions, version estimates, and validation results.
    """
    if not tech_list:
        return {
            "tech_list": [],
            "complementary_techs": {},
            "contradictions": [],
            "version_estimates": {},
            "requires": [],
            "warnings": ["empty_tech_stack"]
        }

    # Remove duplicates and normalize
    tech_list = list(set(tech_list))

    # Check contradictions
    contradictions = check_contradictions(tech_list)

    # Get complementary techs
    complementary = get_complementary_techs(tech_list)

    # Estimate versions
    versions = estimate_versions(tech_list, company_type)

    # Check for missing required technologies
    requires = []
    for tech in tech_list:
        if tech in TECH_RELATIONSHIPS:
            if "requires" in TECH_RELATIONSHIPS[tech]:
                for required in TECH_RELATIONSHIPS[tech]["requires"]:
                    if required not in tech_list:
                        requires.append(f"{tech} requires {required}")

    # Generate warnings
    warnings = []
    if contradictions:
        warnings.append("contradictory_technologies")
    if requires:
        warnings.append("missing_required_technologies")
    if not complementary:
        warnings.append("no_complementary_technologies_found")

    return {
        "tech_list": tech_list,
        "complementary_techs": complementary,
        "contradictions": contradictions,
        "missing_requirements": requires,
        "version_estimates": versions,
        "company_type": company_type,
        "warnings": warnings,
        "validation_passed": len(contradictions) == 0 and len(requires) == 0
    }


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Read tech list from file (JSON array)
        with open(sys.argv[1], "r") as f:
            data = json.load(f)
        company_type = sys.argv[2] if len(sys.argv) > 2 else "mid-market"
        result = map_tech_stack(data, company_type)
        print(json.dumps(result, indent=2))
    else:
        # Demo with sample tech stack
        sample_stack = ["Java", "Spring Boot", "Kubernetes", "Docker", "PostgreSQL", "AWS"]

        print("=== DEMO 1: Valid Enterprise Stack ===\n")
        result = map_tech_stack(sample_stack, "enterprise")
        print(json.dumps(result, indent=2))

        # Demo 2: Contradictory stack
        print("\n\n=== DEMO 2: Contradictory Stack (AWS + Azure) ===\n")
        bad_stack = ["Java", "AWS", "Azure", "Kubernetes"]
        result = map_tech_stack(bad_stack, "enterprise")
        print(json.dumps(result, indent=2))

        # Demo 3: Missing requirements
        print("\n\n=== DEMO 3: Missing Required Tech (Spring Boot without Java) ===\n")
        incomplete = ["Spring Boot", "PostgreSQL"]
        result = map_tech_stack(incomplete, "enterprise")
        print(json.dumps(result, indent=2))
