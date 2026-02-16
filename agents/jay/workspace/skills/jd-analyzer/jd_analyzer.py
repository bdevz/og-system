"""
JD Analyzer for Agent Jay
==========================
Analyzes job descriptions and extracts structured components.
Input: raw JD text + company type. Output: structured analysis dict.

Usage:
    from jd_analyzer import analyze_jd

    result = analyze_jd(
        jd_text="We are looking for a Senior Java Developer...",
        company_type="enterprise"
    )
"""

import json
import re
from typing import List, Dict, Tuple
from pathlib import Path


# Technology keywords organized by category
TECH_KEYWORDS = {
    "languages": {
        "Java": ["java", "jvm", "springboot", "spring"],
        "Python": ["python", "django", "flask", "fastapi"],
        "JavaScript": ["javascript", "typescript", "node", "nodejs"],
        "Go": ["golang", "go"],
        "Rust": ["rust"],
        "C++": ["c++", "cpp"],
        "C#": ["c#", "csharp", ".net"],
    },
    "frameworks": {
        "Spring Boot": ["spring boot", "springboot"],
        "React": ["react", "reactjs"],
        "Angular": ["angular"],
        "Vue": ["vue"],
        "Django": ["django"],
        "FastAPI": ["fastapi"],
        "Express": ["express"],
        "Kubernetes": ["kubernetes", "k8s"],
    },
    "databases": {
        "PostgreSQL": ["postgresql", "postgres"],
        "MySQL": ["mysql"],
        "MongoDB": ["mongodb", "mongo"],
        "Redis": ["redis"],
        "DynamoDB": ["dynamodb"],
        "Cassandra": ["cassandra"],
        "Elasticsearch": ["elasticsearch"],
    },
    "cloud_platforms": {
        "AWS": ["aws", "amazon web services"],
        "Azure": ["azure", "microsoft azure"],
        "GCP": ["gcp", "google cloud"],
    },
    "devops": {
        "Docker": ["docker"],
        "Kubernetes": ["kubernetes", "k8s"],
        "Jenkins": ["jenkins"],
        "Terraform": ["terraform"],
        "Ansible": ["ansible"],
        "CI/CD": ["ci/cd", "continuous integration", "continuous deployment"],
    },
    "methodologies": {
        "Agile": ["agile"],
        "Scrum": ["scrum"],
        "Microservices": ["microservices"],
    }
}

# Common contradictions (techs that don't usually coexist)
TECH_CONTRADICTIONS = [
    ("Java 8", "Spring Boot 3.0"),
    ("AWS", "Azure"),
    ("Kubernetes", "Docker Swarm"),
    ("Node.js", "Java"),
]


def extract_keywords(text: str) -> Dict[str, List[str]]:
    """
    Extract technology keywords from JD text.
    Returns a dict mapping tech categories to found keywords.
    """
    text_lower = text.lower()
    found = {}

    for category, keywords in TECH_KEYWORDS.items():
        found[category] = []
        for tech_name, tech_keywords in keywords.items():
            for keyword in tech_keywords:
                if keyword in text_lower:
                    if tech_name not in found[category]:
                        found[category].append(tech_name)
                    break

    return {k: v for k, v in found.items() if v}  # Remove empty categories


def classify_requirements(text: str) -> Dict[str, List[str]]:
    """
    Classify requirements as MUST_HAVE, NICE_TO_HAVE, or INFERRED.
    Simple heuristic: "must have", "required" -> MUST_HAVE
                     "nice to have", "preferred", "optional" -> NICE_TO_HAVE
                     Everything else -> INFERRED (extracted from job duties)
    """
    text_lower = text.lower()
    requirements = {
        "MUST_HAVE": [],
        "NICE_TO_HAVE": [],
        "INFERRED": []
    }

    # Very simple classification based on keywords
    # A real implementation would do NLP-based requirement extraction
    lines = text.split("\n")
    for line in lines:
        line_lower = line.lower()
        if any(phrase in line_lower for phrase in ["must have", "required", "requirements", "should have"]):
            # Likely a must-have
            if line.strip():
                requirements["MUST_HAVE"].append(line.strip())
        elif any(phrase in line_lower for phrase in ["nice to have", "preferred", "optional", "beneficial"]):
            # Likely a nice-to-have
            if line.strip():
                requirements["NICE_TO_HAVE"].append(line.strip())
        elif any(phrase in line_lower for phrase in ["we are looking", "you will", "responsibilities", "duties"]):
            # Likely inferred from job description
            if line.strip():
                requirements["INFERRED"].append(line.strip())

    return requirements


def detect_contradictions(keywords: Dict[str, List[str]]) -> List[Tuple[str, str]]:
    """
    Detect if contradictory technologies appear in the same JD.
    Returns list of (tech1, tech2) tuples that contradict.
    """
    contradictions = []
    all_techs = []
    for category_list in keywords.values():
        all_techs.extend(category_list)

    for tech1, tech2 in TECH_CONTRADICTIONS:
        if tech1 in all_techs and tech2 in all_techs:
            contradictions.append((tech1, tech2))

    return contradictions


def estimate_experience_level(text: str) -> str:
    """
    Estimate required experience level from text.
    Returns: "junior", "mid-level", "senior", "staff", or "unknown"
    """
    text_lower = text.lower()

    if any(phrase in text_lower for phrase in ["senior", "lead", "principal", "staff", "architect"]):
        return "senior"
    elif any(phrase in text_lower for phrase in ["mid-level", "mid level", "3-5 years", "3+ years"]):
        return "mid-level"
    elif any(phrase in text_lower for phrase in ["junior", "entry", "0-2 years", "entry-level"]):
        return "junior"
    else:
        return "unknown"


def estimate_experience_years(text: str) -> Tuple[int, int, str]:
    """
    Extract experience requirements from text.
    Returns: (min_years, max_years, confidence)
    confidence: "high", "medium", "low"
    """
    # Look for patterns like "3+ years", "3-5 years", "5 years experience"
    patterns = [
        r"(\d+)\s*\+\s*years",  # "3+ years"
        r"(\d+)\s*-\s*(\d+)\s*years",  # "3-5 years"
        r"(\d+)\s*years?\s*(?:of|experience|working)",  # "3 years of experience"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        if matches:
            if isinstance(matches[0], tuple):
                # Range match
                return int(matches[0][0]), int(matches[0][1]), "high"
            else:
                # Single number match
                years = int(matches[0])
                return years, years + 3, "medium"  # Assume max is +3 years

    return 0, 20, "low"  # Default: unknown


def estimate_version(tech_name: str, company_type: str, text: str) -> str:
    """
    Estimate technology version based on company type and context.
    Returns: estimated version string or "unknown"
    """
    text_lower = text.lower()

    # Look for explicit version mentions
    version_patterns = [
        rf"{tech_name.lower()}\s+(\d+\.\d+)",
        rf"{tech_name.lower()}\s+v(\d+\.\d+)",
    ]

    for pattern in version_patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(1)

    # Estimate based on company type
    # Enterprise typically runs N-1 or N-2 versions
    # Startups run latest
    version_estimates = {
        "Java": {
            "enterprise": "11 or 17",
            "mid-market": "11 or 17",
            "startup": "17 or 21"
        },
        "Spring Boot": {
            "enterprise": "2.7.x",
            "mid-market": "3.x",
            "startup": "3.x"
        },
        "Python": {
            "enterprise": "3.8 or 3.9",
            "mid-market": "3.9 or 3.10",
            "startup": "3.10 or 3.11"
        },
        "React": {
            "enterprise": "16.x or 17.x",
            "mid-market": "18.x",
            "startup": "18.x or 19.x"
        },
        "Kubernetes": {
            "enterprise": "1.24+",
            "mid-market": "1.25+",
            "startup": "1.26+"
        },
    }

    if tech_name in version_estimates:
        return version_estimates[tech_name].get(company_type, "unknown")

    return "unknown"


def analyze_jd(jd_text: str, company_type: str = "mid-market") -> dict:
    """
    Analyze a job description and return structured components.

    Args:
        jd_text: Raw job description text
        company_type: "enterprise", "mid-market", or "startup"

    Returns:
        Dict with keywords, requirements, contradictions, experience estimate, version estimates.
    """
    if not jd_text:
        return {
            "error": "Empty JD text",
            "keywords": {},
            "requirements": {},
            "contradictions": [],
            "experience_level": "unknown",
            "experience_years": (0, 20, "low"),
            "version_estimates": {},
            "red_flags": ["empty_jd"]
        }

    keywords = extract_keywords(jd_text)
    requirements = classify_requirements(jd_text)
    contradictions = detect_contradictions(keywords)
    experience_level = estimate_experience_level(jd_text)
    experience_years = estimate_experience_years(jd_text)

    # Version estimates for found technologies
    all_techs = []
    for category_techs in keywords.values():
        all_techs.extend(category_techs)

    version_estimates = {}
    for tech in all_techs:
        version_estimates[tech] = estimate_version(tech, company_type, jd_text)

    # Red flags
    red_flags = []
    if contradictions:
        red_flags.append("contradictory_technologies")
    if experience_years[1] - experience_years[0] > 10:
        red_flags.append("unrealistic_experience_range")
    if len(jd_text) < 200:
        red_flags.append("vague_jd_too_short")
    if not keywords:
        red_flags.append("no_technologies_specified")
    if not requirements.get("MUST_HAVE"):
        red_flags.append("no_explicit_requirements")

    return {
        "keywords": keywords,
        "requirements": requirements,
        "contradictions": contradictions,
        "experience_level": experience_level,
        "experience_years": {
            "min": experience_years[0],
            "max": experience_years[1],
            "confidence": experience_years[2]
        },
        "version_estimates": version_estimates,
        "red_flags": red_flags,
        "company_type": company_type,
        "analysis_timestamp": None
    }


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Read JD from file
        with open(sys.argv[1], "r") as f:
            jd_text = f.read()
        company_type = sys.argv[2] if len(sys.argv) > 2 else "mid-market"
        result = analyze_jd(jd_text, company_type)
        print(json.dumps(result, indent=2))
    else:
        # Demo with sample JD
        sample_jd = """
        Senior Java Developer - Enterprise Scale

        We are looking for an experienced Senior Java Developer to join our team.

        Requirements:
        - 5+ years of Java development experience
        - Strong knowledge of Spring Boot 2.7 and microservices architecture
        - Experience with Kubernetes and Docker
        - PostgreSQL or MySQL database experience
        - Must have: AWS or Azure cloud experience
        - Nice to have: Kafka message queuing experience

        Responsibilities:
        - Design and implement microservices using Spring Boot
        - Lead technical discussions and code reviews
        - Mentor junior developers
        - Optimize application performance

        This is an enterprise role requiring strong architectural knowledge.
        """

        result = analyze_jd(sample_jd, "enterprise")
        print(json.dumps(result, indent=2))
