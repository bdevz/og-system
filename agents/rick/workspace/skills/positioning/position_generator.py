"""
Position Generator for Agent Rick
===================================
Generates positioning directives for resume customization.
Given a candidate profile + job analysis, determines the optimal positioning angle
and identifies keywords/experience framing to emphasize.

Positioning is EMPHASIS SELECTION. Never fabrication. If candidate lacks a skill,
we acknowledge it as a gap, not claim it.

Usage:
    from position_generator import generate_positioning

    directive = generate_positioning({
        "candidate_id": "C-042",
        "skills": ["Java", "Spring", "Microservices", "Kubernetes"],
        "years_experience": 7,
        "work_history": [...]
    }, {
        "job_id": "J-1234",
        "job_title": "Microservices Architect",
        "required_skills": ["Java", "Spring", "Kubernetes"],
        "preferred_skills": ["Docker", "AWS"],
        "industry": "FinTech",
        "seniority_level": "Senior"
    })
"""

import json
from datetime import datetime, timezone
from pathlib import Path


# Positioning angle templates per category
POSITIONING_TEMPLATES = {
    "Java": {
        "Enterprise Backend": {
            "angles": ["Enterprise Java Backend Engineer", "Senior Java Application Developer", "Enterprise Systems Architect"],
            "emphasize": ["enterprise frameworks", "scalability", "monolithic/modular design", "long-term maintenance"],
            "deemphasize": ["microservices", "cloud-native", "startup projects"]
        },
        "Microservices": {
            "angles": ["Microservices Architect", "Distributed Systems Engineer", "Cloud-native Java Specialist"],
            "emphasize": ["microservices patterns", "API design", "distributed systems", "scalability", "cloud platforms"],
            "deemphasize": ["monolith experience", "legacy code"]
        },
        "Full Stack": {
            "angles": ["Full Stack Java Developer", "Java Backend + Frontend Engineer"],
            "emphasize": ["backend Java", "frontend experience", "end-to-end feature ownership"],
            "deemphasize": ["infrastructure/DevOps work"]
        }
    },
    "Python": {
        "Data Engineering": {
            "angles": ["Data Engineering Specialist", "Python Data Pipeline Engineer", "ETL Architect"],
            "emphasize": ["data pipelines", "data processing", "SQL", "distributed systems", "orchestration"],
            "deemphasize": ["web frameworks", "DevOps"]
        },
        "Backend": {
            "angles": ["Python Backend Engineer", "REST API Developer", "Web Application Architect"],
            "emphasize": ["REST APIs", "web frameworks", "database design", "scalability"],
            "deemphasize": ["data science", "data engineering"]
        },
        "ML Engineering": {
            "angles": ["Machine Learning Engineer", "ML-focused Python Developer", "ML Infrastructure Engineer"],
            "emphasize": ["model training", "ML frameworks", "data science", "Python ecosystems"],
            "deemphasize": ["web backend", "data engineering"]
        }
    },
    "DevOps": {
        "Cloud Infrastructure": {
            "angles": ["Cloud Infrastructure Architect", "AWS/GCP/Azure Specialist", "Infrastructure-as-Code Engineer"],
            "emphasize": ["cloud platforms", "infrastructure automation", "IaC tools", "scaling"],
            "deemphasize": ["application development"]
        },
        "Kubernetes": {
            "angles": ["Kubernetes Specialist", "Container Orchestration Engineer", "Cloud-native Infrastructure Expert"],
            "emphasize": ["Kubernetes", "containers", "microservices deployment", "scaling"],
            "deemphasize": ["traditional infrastructure", "VMs"]
        },
        "CI/CD": {
            "angles": ["DevOps Engineer", "CI/CD Automation Specialist", "Pipeline Engineer"],
            "emphasize": ["automation", "CI/CD systems", "deployment pipelines", "monitoring"],
            "deemphasize": ["infrastructure maintenance"]
        }
    }
}

SKILL_CATEGORIES = {
    "Java": ["java", "spring", "spring boot", "microservices", "jpa", "hibernate", "maven", "gradle"],
    "Python": ["python", "pandas", "django", "flask", "fastapi", "pyspark", "tensorflow", "pytorch"],
    "Cloud": ["aws", "gcp", "azure", "cloud", "ec2", "lambda", "gke", "aks"],
    "Kubernetes": ["kubernetes", "k8s", "helm", "docker", "container", "orchestration"],
    "DevOps": ["devops", "jenkins", "gitlab", "circleci", "terraform", "ansible", "cloudformation"],
    "Data": ["sql", "spark", "airflow", "snowflake", "bigquery", "datawarehouse", "etl"],
    "Frontend": ["react", "vue", "angular", "javascript", "typescript", "html", "css"]
}


def generate_positioning(candidate: dict, job: dict) -> dict:
    """
    Generate positioning directive for a candidate-job pairing.

    Args:
        candidate: Dict with keys:
            - candidate_id (str)
            - candidate_name (str, optional)
            - skills (list): Candidate's actual skills
            - years_experience (int): Total years
            - work_history (list, optional): List of past roles with descriptions
            - education (str, optional)

        job: Dict with keys:
            - job_id (str)
            - job_title (str)
            - required_skills (list)
            - preferred_skills (list, optional)
            - industry (str, optional)
            - seniority_level (str): "Entry", "Mid", "Senior", "Staff"
            - description (str, optional): Full job description

    Returns:
        Dict with positioning directive:
            - primary_angle: Recommended positioning
            - skills_emphasize: List of skills to highlight
            - skills_deemphasize: List to minimize
            - experience_frame: How to present past experience
            - keywords_to_plant: For ATS and hiring manager
            - version_requirements: Version specifics (Java 11+, etc.)
            - positioning_rationale: Why this angle
            - gaps: Skills missing from candidate
    """

    candidate_id = candidate.get("candidate_id", "")
    candidate_name = candidate.get("candidate_name", "")
    candidate_skills = [s.lower() for s in candidate.get("skills", [])]
    job_title = job.get("job_title", "")
    required_skills = [s.lower() for s in job.get("required_skills", [])]
    preferred_skills = [s.lower() for s in job.get("preferred_skills", [])]
    industry = job.get("industry", "").lower()

    # Determine primary category
    primary_category = _determine_primary_category(candidate_skills)
    secondary_category = _determine_secondary_category(candidate_skills, primary_category)

    # Select positioning angle
    angle, angle_config = _select_positioning_angle(
        job_title,
        primary_category,
        secondary_category,
        candidate_skills,
        required_skills,
        preferred_skills
    )

    # Identify emphasis and deemphasis
    skills_emphasize = angle_config.get("emphasize", [])
    skills_deemphasize = angle_config.get("deemphasize", [])

    # Build experience frame
    experience_frame = _build_experience_frame(
        candidate.get("work_history", []),
        skills_emphasize,
        industry
    )

    # Extract keywords to plant
    keywords = _extract_keywords(required_skills, preferred_skills, candidate_skills)

    # Identify gaps
    gaps = _identify_gaps(required_skills, candidate_skills)

    # Version requirements
    versions = _extract_version_requirements(job.get("description", ""))

    result = {
        "candidate_id": candidate_id,
        "candidate_name": candidate_name,
        "job_id": job.get("job_id", ""),
        "job_title": job_title,
        "primary_angle": angle,
        "primary_category": primary_category,
        "secondary_category": secondary_category,
        "skills_emphasize": skills_emphasize,
        "skills_deemphasize": skills_deemphasize,
        "experience_frame": experience_frame,
        "keywords_to_plant": keywords,
        "gaps": gaps,
        "version_requirements": versions,
        "positioning_rationale": _generate_rationale(
            angle,
            primary_category,
            skills_emphasize,
            gaps
        ),
        "resume_framing": {
            "title_suggestion": f"{primary_category.title()} - {angle}",
            "summary_angle": angle,
            "highlight_projects": _suggest_highlight_projects(
                candidate.get("work_history", []),
                skills_emphasize
            )
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ready_for_resume_tool": len(gaps) == 0 or len(gaps) <= 2  # Flag if gaps too large
    }

    return result


def _determine_primary_category(candidate_skills: list) -> str:
    """Determine primary skill category."""
    max_overlap = 0
    primary = "General"

    for category, skills in SKILL_CATEGORIES.items():
        overlap = sum(1 for cs in candidate_skills if any(s in cs or cs in s for s in skills))
        if overlap > max_overlap:
            max_overlap = overlap
            primary = category

    return primary


def _determine_secondary_category(candidate_skills: list, primary: str) -> str:
    """Determine secondary skill category."""
    for category, skills in SKILL_CATEGORIES.items():
        if category != primary:
            overlap = sum(1 for cs in candidate_skills if any(s in cs or cs in s for s in skills))
            if overlap >= 2:
                return category
    return ""


def _select_positioning_angle(job_title: str, primary: str, secondary: str,
                              candidate_skills: list, required_skills: list,
                              preferred_skills: list) -> tuple:
    """
    Select the best positioning angle based on job title and skills.
    Returns (angle_string, angle_config_dict).
    """
    job_lower = job_title.lower()

    # Try to match job title to positioning angles
    if primary in POSITIONING_TEMPLATES:
        templates = POSITIONING_TEMPLATES[primary]

        # Try to match job keywords to template keys
        for template_key, template_config in templates.items():
            template_key_lower = template_key.lower()
            if any(kw in job_lower for kw in template_key_lower.split()):
                # Found a match
                angles = template_config.get("angles", [template_key])
                return angles[0], template_config

        # No direct match, pick most relevant based on skills
        best_match = None
        best_score = 0

        for template_key, template_config in templates.items():
            emphasize = [s.lower() for s in template_config.get("emphasize", [])]
            overlap = sum(1 for em in emphasize if any(s in em or em in s for s in candidate_skills))
            if overlap > best_score:
                best_score = overlap
                best_match = (template_config.get("angles", [template_key])[0], template_config)

        if best_match:
            return best_match

    # Fallback: generic angle based on job title
    if "architect" in job_lower:
        return "Solutions Architect", {
            "angles": ["Solutions Architect"],
            "emphasize": ["system design", "scalability", "technical leadership"],
            "deemphasize": ["basic implementation"]
        }
    elif "senior" in job_lower:
        return "Senior Engineer", {
            "angles": ["Senior Engineer"],
            "emphasize": ["leadership", "mentorship", "architecture"],
            "deemphasize": []
        }
    else:
        return "Software Engineer", {
            "angles": ["Software Engineer"],
            "emphasize": required_skills[:3],
            "deemphasize": []
        }


def _build_experience_frame(work_history: list, emphasize_skills: list, industry: str) -> str:
    """
    Build guidance for how to frame past experience in resume.
    """
    if not work_history:
        return "Present technical skills and achievements from all roles."

    frame_parts = []

    for role in work_history:
        role_title = role.get("title", "")
        role_desc = role.get("description", "").lower()

        # Check if this role aligns with emphasis skills
        aligned = any(skill.lower() in role_desc for skill in emphasize_skills)

        if aligned:
            frame_parts.append(f"Highlight: {role_title} - focus on {', '.join(emphasize_skills[:2])} accomplishments")

    if frame_parts:
        return ". ".join(frame_parts)
    else:
        return f"Present experience demonstrating {', '.join(emphasize_skills[:3])}. Minimize non-aligned work."


def _extract_keywords(required: list, preferred: list, candidate_skills: list) -> dict:
    """Extract and categorize keywords to plant in resume."""
    candidate_lower = [s.lower() for s in candidate_skills]

    direct_plant = []
    for req in required:
        if any(r.lower() == req for r in candidate_lower):
            direct_plant.append(req)

    mapped_keywords = []
    # Keywords candidate has related skills for but different exact match
    for req in required:
        if req not in direct_plant:
            for skill in candidate_skills:
                if _is_equivalent(req.lower(), skill.lower()):
                    mapped_keywords.append({
                        "job_keyword": req,
                        "candidate_equivalent": skill,
                        "plant_as": f"{skill} (equivalent to {req})"
                    })
                    break

    return {
        "direct_plant": direct_plant,
        "mapped_keywords": mapped_keywords,
        "total_coverage": len(direct_plant) + len(mapped_keywords),
        "total_required": len(required)
    }


def _identify_gaps(required_skills: list, candidate_skills: list) -> list:
    """Identify required skills candidate is missing."""
    candidate_lower = [s.lower() for s in candidate_skills]
    gaps = []

    for req in required_skills:
        req_lower = req.lower()
        has_exact = any(r.lower() == req_lower for r in candidate_lower)
        has_equivalent = any(_is_equivalent(req_lower, cs.lower()) for cs in candidate_lower)

        if not has_exact and not has_equivalent:
            gaps.append(req)

    return gaps


def _extract_version_requirements(description: str) -> dict:
    """Extract version requirements from job description."""
    version_dict = {}

    # Simple pattern matching for common version requirements
    import re

    patterns = [
        (r"java\s+(\d+(\.\d+)?)", "java"),
        (r"python\s+(\d+(\.\d+)?)", "python"),
        (r"kubernetes\s+(\d+(\.\d+)?)", "kubernetes"),
        (r"spring\s+(\d+(\.\d+)?)", "spring"),
        (r"docker\s+(\d+(\.\d+)?)", "docker"),
    ]

    for pattern, key in patterns:
        match = re.search(pattern, description.lower())
        if match:
            version_dict[key] = match.group(1)

    return version_dict


def _is_equivalent(skill1: str, skill2: str) -> bool:
    """Check if two skills are functionally equivalent."""
    equivalencies = {
        "airflow": ["step functions", "prefect", "dbt"],
        "kubernetes": ["k8s", "docker swarm", "openshift"],
        "jenkins": ["gitlab ci", "circleci", "github actions"],
        "spark": ["pyspark", "scala spark"],
        "terraform": ["cloudformation", "ansible", "pulumi"],
    }

    for base, alts in equivalencies.items():
        if base in skill1 or base in skill2:
            for alt in alts:
                if alt in skill1 or alt in skill2:
                    return True

    return False


def _suggest_highlight_projects(work_history: list, emphasis_skills: list) -> list:
    """Suggest which projects to highlight based on emphasis skills."""
    suggestions = []

    for role in work_history:
        role_desc = role.get("description", "").lower()
        matching_skills = sum(1 for skill in emphasis_skills if skill.lower() in role_desc)

        if matching_skills >= 2:
            suggestions.append({
                "role": role.get("title", ""),
                "reason": f"Demonstrates {matching_skills} key skills",
                "priority": "HIGH" if matching_skills >= 3 else "MEDIUM"
            })

    return suggestions


def _generate_rationale(angle: str, primary_category: str, emphasize: list, gaps: list) -> str:
    """Generate explanation for the positioning choice."""
    rationale = f"Positioning as '{angle}' ({primary_category} focus) "
    rationale += f"emphasizes {', '.join(emphasize[:3])}. "

    if gaps:
        rationale += f"Note: {len(gaps)} gaps ({', '.join(gaps[:2])}). "
        rationale += "Flag with hiring manager as growth opportunity or training area."
    else:
        rationale += "Strong alignment with all required skills."

    return rationale


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            data = json.load(f)

        candidate = data.get("candidate", {})
        job = data.get("job", {})

        result = generate_positioning(candidate, job)
        print(json.dumps(result, indent=2))
    else:
        # Demo
        sample_candidate = {
            "candidate_id": "C-042",
            "candidate_name": "Ravi Kumar",
            "skills": ["Java", "Spring", "Spring Boot", "Microservices", "Kubernetes", "Docker"],
            "years_experience": 7,
            "work_history": [
                {
                    "title": "Senior Java Developer",
                    "company": "TechCorp",
                    "description": "Built microservices using Spring Boot and Kubernetes"
                }
            ]
        }
        sample_job = {
            "job_id": "J-1234",
            "job_title": "Microservices Architect",
            "required_skills": ["Java", "Spring", "Kubernetes"],
            "preferred_skills": ["Docker", "AWS"],
            "industry": "FinTech",
            "seniority_level": "Senior"
        }
        result = generate_positioning(sample_candidate, sample_job)
        print(json.dumps(result, indent=2))
