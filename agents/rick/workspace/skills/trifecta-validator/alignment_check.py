"""
Trifecta Validator for Agent Rick
====================================
Pre-application verification. Checks that candidate data, LinkedIn profile,
and resume all align before submission.

Three things must match:
1. Candidate data (skills, experience, rate, visa in Z's system)
2. LinkedIn profile (positioning, work history, skills)
3. Resume (keywords, versions, experience framing)

If all three align = ALIGNED (ready to apply).
If any mismatch = FAILED (list mismatches + suggested fixes).

Usage:
    from alignment_check import validate_trifecta

    result = validate_trifecta(
        candidate_data_dict,
        linkedin_profile_dict,
        resume_text,
        target_job_dict
    )
    # Returns: {decision: ALIGNED/FAILED, checks: {}, failures: [], suggestions: []}
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path


def validate_trifecta(candidate: dict, linkedin_profile: dict, resume_text: str,
                       target_job: dict) -> dict:
    """
    Validate alignment across candidate data, LinkedIn, and resume.

    Args:
        candidate: Dict from Z with:
            - candidate_id (str)
            - candidate_name (str)
            - skills (list)
            - years_experience (int)
            - rate (float)
            - visa_status (str)
            - employment_history (list)

        linkedin_profile: Dict with:
            - profile_id (str)
            - positioning (str)
            - headline (str)
            - skills_section (list)
            - work_history (list): [{title, company, dates, description}]
            - last_activity (ISO-8601)
            - profile_health (str): GREEN/YELLOW/RED/BANNED

        resume_text: Full resume text (string)

        target_job: Dict with:
            - job_id (str)
            - job_title (str)
            - required_skills (list)

    Returns:
        Dict with:
            - decision: "ALIGNED" or "FAILED"
            - overall_pass: bool
            - checks: Dict with results of each validation
            - failures: List of failure descriptions
            - suggestions: List of suggested fixes
    """

    candidate_id = candidate.get("candidate_id", "")
    failures = []
    suggestions = []

    # Check 1: Candidate fit
    candidate_fit_check = _validate_candidate_fit(candidate, target_job)
    if not candidate_fit_check["passed"]:
        failures.extend(candidate_fit_check.get("failures", []))
        suggestions.extend(candidate_fit_check.get("suggestions", []))

    # Check 2: LinkedIn profile consistency
    linkedin_check = _validate_linkedin_profile(
        candidate,
        linkedin_profile,
        target_job
    )
    if not linkedin_check["passed"]:
        failures.extend(linkedin_check.get("failures", []))
        suggestions.extend(linkedin_check.get("suggestions", []))

    # Check 3: Resume consistency
    resume_check = _validate_resume(
        candidate,
        resume_text,
        linkedin_profile,
        target_job
    )
    if not resume_check["passed"]:
        failures.extend(resume_check.get("failures", []))
        suggestions.extend(resume_check.get("suggestions", []))

    decision = "ALIGNED" if len(failures) == 0 else "FAILED"

    result = {
        "candidate_id": candidate_id,
        "decision": decision,
        "overall_pass": decision == "ALIGNED",
        "checks": {
            "candidate_fit": {
                "passed": candidate_fit_check["passed"],
                "details": candidate_fit_check
            },
            "linkedin_profile": {
                "passed": linkedin_check["passed"],
                "details": linkedin_check
            },
            "resume": {
                "passed": resume_check["passed"],
                "details": resume_check
            }
        },
        "failures": failures,
        "suggestions": suggestions,
        "ready_for_submission": decision == "ALIGNED",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return result


def _validate_candidate_fit(candidate: dict, target_job: dict) -> dict:
    """Check 1: Candidate data aligns with job requirements."""
    failures = []
    suggestions = []
    passed = True

    candidate_skills = [s.lower() for s in candidate.get("skills", [])]
    required_skills = [s.lower() for s in target_job.get("required_skills", [])]

    # Check 1a: Match score
    match_score = candidate.get("match_score")
    if match_score and match_score < 60:
        failures.append("Match score below 60 (score: {})".format(match_score))
        suggestions.append("Review match_calculator.py output. May not be a good fit.")
        passed = False
    elif match_score and 60 <= match_score < 70:
        failures.append("Borderline match score 60-70. Requires human review.")
        suggestions.append("Escalate to EM for approval before submission.")
        passed = False

    # Check 1b: DNS conflicts
    if candidate.get("on_dns_list"):
        failures.append("Candidate on DNS list for this client")
        suggestions.append("Check Z's do-not-submit list. Cannot proceed.")
        passed = False

    # Check 1c: Visa compatibility
    candidate_visa = candidate.get("visa_status", "").lower()
    job_visa_req = target_job.get("visa_requirement", "any").lower()

    if "no " + candidate_visa in job_visa_req or "exclude " + candidate_visa in job_visa_req:
        failures.append(f"Visa mismatch: Job excludes {candidate.get('visa_status')}")
        suggestions.append("Cannot submit. Job has visa restriction.")
        passed = False

    # Check 1d: Rate compatibility
    candidate_rate = candidate.get("rate", 0)
    posted_rate = target_job.get("posted_rate", 0)
    if candidate_rate > 0 and posted_rate > 0:
        if candidate_rate > posted_rate * 1.1:  # More than 10% over
            failures.append(f"Rate mismatch: Candidate ${candidate_rate} > Posted ${posted_rate}")
            suggestions.append("Rate negotiation required. Flag with EM.")
            passed = False

    return {
        "passed": passed,
        "failures": failures,
        "suggestions": suggestions
    }


def _validate_linkedin_profile(candidate: dict, linkedin_profile: dict,
                                target_job: dict) -> dict:
    """Check 2: LinkedIn profile aligns with candidate data and target job."""
    failures = []
    suggestions = []
    passed = True

    # Check 2a: Profile health
    health = linkedin_profile.get("profile_health", "UNKNOWN")
    if health in ["RED", "BANNED"]:
        failures.append(f"LinkedIn profile health is {health}")
        suggestions.append("Profile is unhealthy. Contact Leroy to repair.")
        passed = False

    # Check 2b: Positioning matches target role
    positioning = linkedin_profile.get("positioning", "").lower()
    target_job_title = target_job.get("job_title", "").lower()

    if positioning and target_job_title:
        alignment = _check_positioning_alignment(positioning, target_job_title)
        if alignment < 0.6:  # Less than 60% alignment
            failures.append(f"Profile positioning '{linkedin_profile.get('positioning')}' doesn't match target '{target_job.get('job_title')}'")
            suggestions.append("Profile positioning misaligned. May confuse hiring manager.")
            passed = False

    # Check 2c: Work history consistency
    li_work_history = linkedin_profile.get("work_history", [])
    candidate_employment = candidate.get("employment_history", [])

    if li_work_history and candidate_employment:
        if not _check_work_history_consistency(li_work_history, candidate_employment):
            failures.append("LinkedIn work history doesn't match candidate data in Z")
            suggestions.append("Update LinkedIn or Z data to match. Hiring manager will notice discrepancy.")
            passed = False

    # Check 2d: Skills section populated
    li_skills = linkedin_profile.get("skills_section", [])
    candidate_skills = candidate.get("skills", [])

    if not li_skills and candidate_skills:
        failures.append("LinkedIn profile has no skills listed, but candidate has skills in Z")
        suggestions.append("Add skills to LinkedIn profile. Empty skills section looks inactive.")
        passed = False

    # Check 2e: Recent activity
    last_activity = linkedin_profile.get("last_activity")
    if last_activity:
        try:
            last_act_date = datetime.fromisoformat(last_activity)
            days_inactive = (datetime.now(timezone.utc) - last_act_date).days
            if days_inactive > 30:
                failures.append(f"Profile inactive for {days_inactive} days")
                suggestions.append("Profile looks dormant. Add recent activity (recommendation, post, etc.).")
                passed = False
        except:
            pass

    return {
        "passed": passed,
        "failures": failures,
        "suggestions": suggestions
    }


def _validate_resume(candidate: dict, resume_text: str, linkedin_profile: dict,
                      target_job: dict) -> dict:
    """Check 3: Resume aligns with candidate data, LinkedIn, and target role."""
    failures = []
    suggestions = []
    passed = True

    if not resume_text:
        failures.append("Resume text is empty")
        suggestions.append("Generate resume before submission.")
        return {
            "passed": False,
            "failures": failures,
            "suggestions": suggestions
        }

    resume_lower = resume_text.lower()

    # Check 3a: Keywords planted
    required_skills = [s.lower() for s in target_job.get("required_skills", [])]
    missing_keywords = []

    for skill in required_skills:
        if skill not in resume_lower and not _find_equivalent_in_resume(skill, resume_lower):
            missing_keywords.append(skill)

    if missing_keywords:
        failures.append(f"Keywords missing from resume: {', '.join(missing_keywords[:3])}")
        suggestions.append("Plant missing keywords in resume before submission.")
        passed = False

    # Check 3b: Versions correct
    required_versions = target_job.get("version_requirements", {})
    for tech, version in required_versions.items():
        if tech.lower() not in resume_lower:
            failures.append(f"Version info missing: {tech} {version} not in resume")
            suggestions.append(f"Add '{tech} {version}' to resume.")
            passed = False

    # Check 3c: Experience framing consistent with LinkedIn
    li_positioning = linkedin_profile.get("positioning", "").lower()
    if li_positioning:
        # Check that resume's emphasis matches LinkedIn positioning
        positioning_keywords = li_positioning.split()
        resume_has_positioning = sum(1 for kw in positioning_keywords if kw in resume_lower)

        if resume_has_positioning == 0:
            failures.append(f"Resume doesn't emphasize LinkedIn positioning '{linkedin_profile.get('positioning')}'")
            suggestions.append("Ensure resume framing matches LinkedIn profile positioning.")
            passed = False

    # Check 3d: Red flags
    red_flags = _check_resume_red_flags(resume_text)
    if red_flags:
        failures.extend([f"Resume red flag: {flag}" for flag in red_flags])
        suggestions.append("Address red flags before submission.")
        passed = False

    return {
        "passed": passed,
        "failures": failures,
        "suggestions": suggestions,
        "keywords_found": len(required_skills) - len(missing_keywords),
        "keywords_total": len(required_skills)
    }


def _check_positioning_alignment(positioning: str, job_title: str) -> float:
    """
    Score how well positioning aligns with job title.
    Returns 0-1 alignment score.
    """
    pos_words = positioning.lower().split()
    job_words = job_title.lower().split()

    overlap = sum(1 for pw in pos_words if pw in job_words)
    alignment = overlap / max(len(pos_words), len(job_words))

    return min(1.0, alignment)


def _check_work_history_consistency(li_history: list, z_history: list) -> bool:
    """
    Check if LinkedIn work history matches Z data.
    Returns True if consistent, False if major discrepancies.
    """
    if len(li_history) == 0 or len(z_history) == 0:
        return True  # No data to compare

    # Simple check: do the counts match roughly?
    li_count = len(li_history)
    z_count = len(z_history)

    if abs(li_count - z_count) > 2:
        return False  # Major discrepancy

    return True


def _find_equivalent_in_resume(keyword: str, resume_text: str) -> bool:
    """
    Check if resume has equivalent skill/keyword.
    """
    # Simple equivalency map
    equivalencies = {
        "airflow": ["step_functions", "prefect"],
        "kubernetes": ["k8s"],
        "jenkins": ["gitlab", "circleci"],
        "aws": ["amazon web services"],
    }

    if keyword in equivalencies:
        for equiv in equivalencies[keyword]:
            if equiv in resume_text:
                return True

    return False


def _check_resume_red_flags(resume_text: str) -> list:
    """
    Check for resume red flags that would concern hiring manager.
    """
    red_flags = []

    # Check for common red flag phrases
    red_flag_patterns = [
        (r"work in progress", "Resume incomplete"),
        (r"TBD|to be determined", "Resume has placeholders"),
        (r"__\w+__|{{.*?}}", "Resume has template markers"),
        (r"confidential", "Mentions confidential projects (risky for sharing)"),
    ]

    for pattern, flag in red_flag_patterns:
        if re.search(pattern, resume_text, re.IGNORECASE):
            red_flags.append(flag)

    return red_flags


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            data = json.load(f)

        candidate = data.get("candidate", {})
        linkedin_profile = data.get("linkedin_profile", {})
        resume_text = data.get("resume_text", "")
        target_job = data.get("target_job", {})

        result = validate_trifecta(candidate, linkedin_profile, resume_text, target_job)
        print(json.dumps(result, indent=2))
    else:
        # Demo
        sample_candidate = {
            "candidate_id": "C-042",
            "candidate_name": "Ravi Kumar",
            "skills": ["Java", "Spring", "Kubernetes", "Docker"],
            "years_experience": 7,
            "rate": 85,
            "visa_status": "H1B",
            "match_score": 78
        }
        sample_linkedin = {
            "profile_id": "LI-042-A",
            "positioning": "Microservices Architect",
            "profile_health": "GREEN",
            "skills_section": ["Java", "Spring", "Kubernetes"],
            "work_history": [
                {"title": "Senior Java Developer", "company": "TechCorp"}
            ]
        }
        sample_resume = "Microservices Architect with 7 years. Java, Spring Boot, Kubernetes, Docker. ..."
        sample_job = {
            "job_id": "J-1234",
            "job_title": "Microservices Architect",
            "required_skills": ["Java", "Spring", "Kubernetes"]
        }
        result = validate_trifecta(sample_candidate, sample_linkedin, sample_resume, sample_job)
        print(json.dumps(result, indent=2))
