"""
Resume Tool API Client for Agent Rick
=======================================
Interface with resume generation tool (web app with API).

Accepts structured positioning directives and returns customized resumes.

The tool takes:
- Candidate profile
- Positioning directive (angle, emphasis, keywords, versions)
- Target role details

And generates:
- Customized resume with keywords planted
- Formatting applied per positioning
- Versions correct
- ATS-optimized

Usage:
    from api_client import generate_resume

    resume = generate_resume(
        positioning_directive_dict,
        candidate_dict,
        base_resume_text
    )
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# For now: stub implementation that logs API calls
# Real endpoint wired in future
API_ENDPOINT = "https://resume-tool.consultadd.ai/api/v1/generate"
API_TIMEOUT_SECONDS = 30
MAX_RETRIES = 2

LOG_FILE = Path(__file__).parent / "api_calls.jsonl"


def generate_resume(positioning_directive: dict, candidate: dict,
                    base_resume: str) -> dict:
    """
    Generate customized resume via API.

    Args:
        positioning_directive: Dict from position_generator with:
            - primary_angle (str)
            - skills_emphasize (list)
            - skills_deemphasize (list)
            - experience_frame (str)
            - keywords_to_plant (dict)
            - version_requirements (dict)

        candidate: Dict with:
            - candidate_id (str)
            - candidate_name (str)
            - skills (list)

        base_resume: Plain text base resume to customize

    Returns:
        Dict with:
            - success (bool)
            - resume_text (str): Generated resume
            - keywords_planted (list)
            - versions_included (dict)
            - validation_passed (bool)
            - timestamp (ISO-8601)
    """

    candidate_id = candidate.get("candidate_id", "")
    api_request = _build_api_request(positioning_directive, candidate, base_resume)

    # Call API with retry logic
    api_response = _call_api_with_retry(api_request)

    if not api_response.get("success"):
        return {
            "success": False,
            "candidate_id": candidate_id,
            "error": api_response.get("error", "API call failed"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    # Validate response
    resume_text = api_response.get("resume_text", "")
    validation = _validate_resume_output(
        resume_text,
        positioning_directive,
        api_response
    )

    result = {
        "success": True,
        "candidate_id": candidate_id,
        "resume_text": resume_text,
        "keywords_planted": validation.get("keywords_planted", []),
        "versions_included": validation.get("versions_included", {}),
        "validation": {
            "passed": validation.get("passed", False),
            "issues": validation.get("issues", [])
        },
        "api_request_id": api_response.get("request_id", ""),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    _log_api_call(api_request, api_response, result)

    return result


def _build_api_request(positioning: dict, candidate: dict, base_resume: str) -> dict:
    """
    Build structured API request for resume tool.
    """
    return {
        "candidate_id": candidate.get("candidate_id", ""),
        "candidate_name": candidate.get("candidate_name", ""),
        "base_resume": base_resume,
        "positioning": {
            "primary_angle": positioning.get("primary_angle", ""),
            "skills_emphasize": positioning.get("skills_emphasize", []),
            "skills_deemphasize": positioning.get("skills_deemphasize", []),
            "experience_frame": positioning.get("experience_frame", ""),
            "keywords_to_plant": positioning.get("keywords_to_plant", {}),
            "version_requirements": positioning.get("version_requirements", {})
        },
        "formatting": {
            "style": "ATS-optimized",  # Safe for ATS scanning
            "length": "auto"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def _call_api_with_retry(request: dict) -> dict:
    """
    Call resume generation API with retry logic.
    Max 2 retries on timeout or transient error.

    For now: STUB that logs what would be sent.
    Returns mock successful response.
    """

    retry_count = 0
    last_error = None

    while retry_count < MAX_RETRIES + 1:
        try:
            # STUB: In real implementation, would do:
            # response = requests.post(
            #     API_ENDPOINT,
            #     json=request,
            #     timeout=API_TIMEOUT_SECONDS
            # )
            # return response.json()

            # For now: mock successful response
            mock_response = {
                "success": True,
                "request_id": f"REQ-{request['candidate_id']}-{int(time.time())}",
                "resume_text": _generate_mock_resume(request),
                "status": "completed",
                "processing_time_ms": 1200
            }
            return mock_response

        except Exception as e:
            last_error = str(e)
            retry_count += 1
            if retry_count <= MAX_RETRIES:
                time.sleep(2 ** retry_count)  # Exponential backoff
            continue

    # All retries exhausted
    return {
        "success": False,
        "error": f"API call failed after {MAX_RETRIES} retries: {last_error}"
    }


def _generate_mock_resume(request: dict) -> str:
    """
    Generate a mock resume for testing.
    In production, this would come from the API.
    """
    candidate_name = request.get("candidate_name", "Candidate")
    positioning = request.get("positioning", {})
    base_resume = request.get("base_resume", "")

    # Simple template for demo
    mock_resume = f"""
{candidate_name}
{positioning.get('primary_angle', 'Professional')}

PROFESSIONAL SUMMARY
Experienced {positioning.get('primary_angle', 'professional')} specializing in {', '.join(positioning.get('skills_emphasize', [])[:3])}.

CORE SKILLS
{', '.join(positioning.get('skills_emphasize', []))}

EXPERIENCE
[Customized based on positioning directive]
{positioning.get('experience_frame', 'Professional experience with relevant project focus.')}

EDUCATION
[From base resume]
""".strip()

    return mock_resume


def _validate_resume_output(resume_text: str, positioning: dict,
                            api_response: dict) -> dict:
    """
    Validate that generated resume meets quality standards.
    """
    issues = []
    keywords_planted = []
    versions_included = {}

    # Check 1: Keywords planted
    resume_lower = resume_text.lower()
    keywords_to_plant = positioning.get("keywords_to_plant", {})

    if isinstance(keywords_to_plant, dict):
        direct_keywords = keywords_to_plant.get("direct_plant", [])
        for keyword in direct_keywords:
            if keyword.lower() in resume_lower:
                keywords_planted.append(keyword)
            else:
                issues.append(f"Keyword '{keyword}' not planted in resume")
    else:
        # Assume it's a list
        for keyword in keywords_to_plant:
            if isinstance(keyword, dict):
                kw = keyword.get("keyword", "")
            else:
                kw = keyword
            if kw.lower() in resume_lower:
                keywords_planted.append(kw)

    # Check 2: Versions correct
    version_requirements = positioning.get("version_requirements", {})
    for tech, version in version_requirements.items():
        version_str = f"{tech} {version}".lower()
        if version_str in resume_lower or tech.lower() in resume_lower:
            versions_included[tech] = version
        else:
            issues.append(f"Version {tech} {version} not in resume")

    # Check 3: Resume not empty
    if len(resume_text.strip()) < 200:
        issues.append("Resume text too short (< 200 characters)")

    # Check 4: No obvious errors
    error_patterns = [
        ("{{", "Template markers present"),
        ("__", "Placeholder markers present"),
        ("TBD", "Incomplete sections (TBD)")
    ]
    for pattern, message in error_patterns:
        if pattern in resume_text:
            issues.append(message)

    passed = len(issues) == 0

    return {
        "passed": passed,
        "keywords_planted": keywords_planted,
        "versions_included": versions_included,
        "issues": issues
    }


def _log_api_call(request: dict, api_response: dict, result: dict):
    """
    Log API call for audit and debugging.
    """
    log_entry = {
        "event_type": "resume_api_call",
        "timestamp": result["timestamp"],
        "candidate_id": request.get("candidate_id", ""),
        "success": result["success"],
        "request_id": result.get("api_request_id", ""),
        "validation_passed": result.get("validation", {}).get("passed", False),
        "keywords_planted": len(result.get("keywords_planted", [])),
        "issues": result.get("validation", {}).get("issues", [])
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            data = json.load(f)

        positioning = data.get("positioning", {})
        candidate = data.get("candidate", {})
        base_resume = data.get("base_resume", "")

        result = generate_resume(positioning, candidate, base_resume)
        print(json.dumps(result, indent=2))
    else:
        # Demo
        sample_positioning = {
            "primary_angle": "Microservices Architect",
            "skills_emphasize": ["Microservices", "Kubernetes", "Docker", "Spring Boot"],
            "skills_deemphasize": ["Monolith", "Legacy"],
            "experience_frame": "Focus on distributed system projects",
            "keywords_to_plant": {
                "direct_plant": ["Microservices", "Kubernetes", "Docker", "Spring Boot"]
            },
            "version_requirements": {"java": "11+", "spring": "5.0+"}
        }
        sample_candidate = {
            "candidate_id": "C-042",
            "candidate_name": "Ravi Kumar",
            "skills": ["Java", "Spring", "Kubernetes"]
        }
        sample_base = "Senior Java Developer with 7 years experience..."

        result = generate_resume(sample_positioning, sample_candidate, sample_base)
        print(json.dumps(result, indent=2))
