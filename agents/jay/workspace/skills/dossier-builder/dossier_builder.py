"""
Dossier Builder for Agent Jay
==============================
Assembles complete research dossiers from analysis results.
Input: analysis outputs from all other skills. Output: standard dossier format for Rick.

Usage:
    from dossier_builder import build_dossier

    dossier = build_dossier(
        consultant_profile=...,
        job_posting=...,
        jd_analysis=...,
        staleness_result=...,
        tech_stack_validation=...,
        vendor_info=...,
        confidence_score=...
    )
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


def build_dossier(
    consultant_profile: dict,
    job_posting: dict,
    jd_analysis: dict,
    staleness_result: dict,
    tech_stack_validation: dict,
    vendor_info: dict,
    confidence_score: dict,
) -> dict:
    """
    Build a complete research dossier for a consultant-job match.
    This is the output sent to Rick for positioning and application building.

    Args:
        consultant_profile: From Z - consultant ID, name, skills, experience, rate, visa, etc.
        job_posting: Job ID, title, company, posting URL, raw JD text
        jd_analysis: From jd_analyzer - keywords, requirements, experience level
        staleness_result: From staleness_detector - freshness score, red flags
        tech_stack_validation: From tech_stack_mapper - stack validation, contradictions
        vendor_info: From vendor_classifier - vendor tier, ghost rate, etc.
        confidence_score: From confidence_calculator - final confidence score

    Returns:
        Complete dossier dict ready to send to Rick
    """

    # Extract key data
    consultant_id = consultant_profile.get("consultant_id", "UNKNOWN")
    consultant_name = consultant_profile.get("name", "Unknown")
    job_id = job_posting.get("job_id", "UNKNOWN")
    job_title = job_posting.get("title", "Unknown")
    company_name = job_posting.get("company", "Unknown")

    # Build the dossier
    dossier = {
        "dossier_id": f"DOSSIER-{consultant_id}-{job_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "recommendation": confidence_score.get("recommendation", "UNKNOWN"),
        "confidence_score": confidence_score.get("score", 0),
        "recommendation_label": confidence_score.get("recommendation_label", ""),

        # Consultant section
        "consultant": {
            "id": consultant_id,
            "name": consultant_name,
            "target_rate": consultant_profile.get("target_rate", 0),
            "min_rate": consultant_profile.get("min_rate", 0),
            "years_experience": consultant_profile.get("years_experience", 0),
            "visa_status": consultant_profile.get("visa_status", "unknown"),
            "visa_expires": consultant_profile.get("visa_expiration_date", None),
            "core_skills": consultant_profile.get("core_skills", []),
            "certifications": consultant_profile.get("certifications", []),
        },

        # Job section
        "job": {
            "id": job_id,
            "title": job_title,
            "company": company_name,
            "url": job_posting.get("url", ""),
            "posted_date": job_posting.get("posted_date", "unknown"),
            "posting_age_days": staleness_result.get("age_analysis", {}).get("age_days", 0),
        },

        # Vendor section
        "vendor": {
            "name": vendor_info.get("vendor_name", "unknown"),
            "tier": vendor_info.get("tier", "unknown"),
            "response_rate": vendor_info.get("response_rate", "unknown"),
            "ghost_rate": vendor_info.get("ghost_rate", "unknown"),
            "known_clients": vendor_info.get("known_clients", []),
            "notes": vendor_info.get("notes", ""),
        },

        # Posting quality assessment
        "posting_quality": {
            "staleness_score": staleness_result.get("staleness_score", 0),
            "staleness_status": staleness_result.get("staleness_status", "unknown"),
            "applicant_count": staleness_result.get("posting_metadata", {}).get("applicant_count", 0),
            "is_fresh": staleness_result.get("staleness_status") in ["FRESH", "ACCEPTABLE"],
            "red_flags": staleness_result.get("red_flags", []),
        },

        # Technology analysis
        "technology": {
            "jd_technologies": _extract_jd_technologies(jd_analysis),
            "consultant_technologies": consultant_profile.get("core_skills", []),
            "technology_match": _analyze_tech_match(jd_analysis, consultant_profile),
            "tech_stack_validation": {
                "complementary_techs": tech_stack_validation.get("complementary_techs", {}),
                "contradictions": tech_stack_validation.get("contradictions", []),
                "validation_passed": tech_stack_validation.get("validation_passed", True),
                "missing_requirements": tech_stack_validation.get("missing_requirements", []),
                "warnings": tech_stack_validation.get("warnings", []),
            },
        },

        # Requirements analysis
        "requirements": {
            "experience_level": jd_analysis.get("experience_level", "unknown"),
            "experience_years": jd_analysis.get("experience_years", {}),
            "required_technologies": jd_analysis.get("keywords", {}),
            "must_have_requirements": jd_analysis.get("requirements", {}).get("MUST_HAVE", []),
            "nice_to_have_requirements": jd_analysis.get("requirements", {}).get("NICE_TO_HAVE", []),
            "inferred_requirements": jd_analysis.get("requirements", {}).get("INFERRED", []),
        },

        # Confidence breakdown
        "confidence_analysis": {
            "score": confidence_score.get("score", 0),
            "recommendation": confidence_score.get("recommendation", "UNKNOWN"),
            "breakdown": confidence_score.get("breakdown", {}),
            "skill_match_percent": confidence_score.get("breakdown", {}).get("skill_match", {}).get("input", 0),
            "years_difference": confidence_score.get("breakdown", {}).get("experience_alignment", {}).get("input", 0),
            "rate_compatibility": confidence_score.get("breakdown", {}).get("rate_compatibility", {}).get("input", {}),
        },

        # Risk assessment
        "risk_assessment": {
            "high_risk_flags": _identify_high_risk_flags(
                staleness_result,
                tech_stack_validation,
                vendor_info,
                confidence_score
            ),
            "moderate_risk_flags": _identify_moderate_risk_flags(
                staleness_result,
                tech_stack_validation,
                vendor_info
            ),
            "overall_risk_level": _calculate_risk_level(
                staleness_result,
                tech_stack_validation,
                vendor_info,
                confidence_score
            ),
        },

        # Action items for Rick
        "action_items": {
            "resume_optimization": _get_resume_optimization_notes(jd_analysis, consultant_profile),
            "cover_letter_focus": _get_cover_letter_focus(jd_analysis),
            "required_validations": _get_required_validations(
                consultant_profile,
                jd_analysis,
                tech_stack_validation
            ),
        },

        # Full metadata for auditability
        "metadata": {
            "jd_analysis": jd_analysis,
            "staleness_result": staleness_result,
            "tech_stack_validation": tech_stack_validation,
            "vendor_info": vendor_info,
            "confidence_score": confidence_score,
        }
    }

    return dossier


def _extract_jd_technologies(jd_analysis: dict) -> Dict[str, List[str]]:
    """Extract technologies from JD analysis."""
    keywords = jd_analysis.get("keywords", {})
    result = {}
    for category, techs in keywords.items():
        if techs:
            result[category] = techs
    return result


def _analyze_tech_match(jd_analysis: dict, consultant_profile: dict) -> dict:
    """Analyze how well consultant's skills match JD technologies."""
    jd_techs = set()
    for category, techs in jd_analysis.get("keywords", {}).items():
        jd_techs.update(techs)

    consultant_skills = set(consultant_profile.get("core_skills", []))

    matching = jd_techs & consultant_skills
    missing = jd_techs - consultant_skills

    return {
        "jd_techs_count": len(jd_techs),
        "consultant_skills_count": len(consultant_skills),
        "matching_technologies": list(matching),
        "missing_technologies": list(missing),
        "match_percentage": round((len(matching) / len(jd_techs) * 100) if jd_techs else 0, 1)
    }


def _identify_high_risk_flags(
    staleness_result: dict,
    tech_stack_validation: dict,
    vendor_info: dict,
    confidence_score: dict
) -> List[str]:
    """Identify high-risk flags that should block submission."""
    flags = []

    # Staleness risk
    if staleness_result.get("staleness_status") == "STALE":
        flags.append("posting_is_stale")
    if staleness_result.get("red_flag_count", 0) > 3:
        flags.append("multiple_red_flags_detected")

    # Tech stack risk
    if not tech_stack_validation.get("validation_passed", True):
        flags.append("tech_stack_validation_failed")
    if tech_stack_validation.get("contradictions"):
        flags.append("contradictory_technologies_in_stack")

    # Vendor risk
    if vendor_info.get("tier") == "3":
        flags.append("tier_3_body_shop_vendor")
    if vendor_info.get("ghost_rate") and "%" in str(vendor_info.get("ghost_rate", "")):
        try:
            ghost_percent = float(vendor_info.get("ghost_rate", "0").strip("%"))
            if ghost_percent > 50:
                flags.append("vendor_high_ghost_rate")
        except:
            pass

    # Confidence risk
    if confidence_score.get("score", 0) < 5:
        flags.append("low_confidence_score")

    return flags


def _identify_moderate_risk_flags(
    staleness_result: dict,
    tech_stack_validation: dict,
    vendor_info: dict
) -> List[str]:
    """Identify moderate-risk flags that warrant human attention."""
    flags = []

    # Staleness
    if staleness_result.get("staleness_status") == "AGING":
        flags.append("posting_is_aging")
    if staleness_result.get("posting_metadata", {}).get("applicant_count", 0) > 100:
        flags.append("high_applicant_volume")

    # Tech stack
    if tech_stack_validation.get("warnings"):
        flags.append("tech_stack_warnings")
    if tech_stack_validation.get("missing_requirements"):
        flags.append("missing_required_technologies")

    # Vendor
    if vendor_info.get("tier") == "2":
        flags.append("tier_2_regional_vendor")

    return flags


def _calculate_risk_level(
    staleness_result: dict,
    tech_stack_validation: dict,
    vendor_info: dict,
    confidence_score: dict
) -> str:
    """Calculate overall risk level: LOW, MEDIUM, HIGH, CRITICAL."""
    risk_score = 0

    # Staleness impact
    if staleness_result.get("staleness_status") == "STALE":
        risk_score += 3
    elif staleness_result.get("staleness_status") == "AGING":
        risk_score += 1

    # Tech validation impact
    if not tech_stack_validation.get("validation_passed", True):
        risk_score += 2
    if tech_stack_validation.get("warnings"):
        risk_score += 1

    # Vendor impact
    if vendor_info.get("tier") == "3":
        risk_score += 2
    elif vendor_info.get("tier") == "unknown":
        risk_score += 1

    # Confidence impact
    if confidence_score.get("score", 0) < 5:
        risk_score += 2
    elif confidence_score.get("score", 0) < 6:
        risk_score += 1

    if risk_score >= 5:
        return "CRITICAL"
    elif risk_score >= 3:
        return "HIGH"
    elif risk_score >= 1:
        return "MEDIUM"
    else:
        return "LOW"


def _get_resume_optimization_notes(jd_analysis: dict, consultant_profile: dict) -> List[str]:
    """Generate notes for resume optimization."""
    notes = []

    # Tech stack emphasis
    jd_techs = []
    for category, techs in jd_analysis.get("keywords", {}).items():
        jd_techs.extend(techs)

    if jd_techs:
        notes.append(f"Emphasize experience with: {', '.join(jd_techs[:3])}")

    # Experience level
    exp_level = jd_analysis.get("experience_level", "unknown")
    if exp_level:
        notes.append(f"Target experience level: {exp_level}")

    # Requirements matching
    must_haves = jd_analysis.get("requirements", {}).get("MUST_HAVE", [])
    if must_haves:
        notes.append(f"Highlight all {len(must_haves)} must-have requirements")

    return notes


def _get_cover_letter_focus(jd_analysis: dict) -> List[str]:
    """Generate focus areas for cover letter."""
    focus = []

    # Company context
    focus.append("Address company's technology strategy")

    # Experience level alignment
    exp_level = jd_analysis.get("experience_level", "unknown")
    if exp_level in ["senior", "staff"]:
        focus.append("Emphasize leadership and mentoring experience")
    elif exp_level == "mid-level":
        focus.append("Balance technical depth with growth mindset")

    # Technology fit
    focus.append("Demonstrate hands-on experience with listed technologies")

    # Problem solving
    focus.append("Include relevant technical problem-solving examples")

    return focus


def _get_required_validations(
    consultant_profile: dict,
    jd_analysis: dict,
    tech_stack_validation: dict
) -> List[str]:
    """Generate required validations before submission."""
    validations = []

    # Visa check
    visa_status = consultant_profile.get("visa_status", "unknown")
    if visa_status not in ["GC", "Citizen"]:
        validations.append(f"Verify {visa_status} eligibility for this client")

    # Tech stack check
    if not tech_stack_validation.get("validation_passed", True):
        validations.append("Resolve tech stack contradictions before submission")

    # Experience level
    jd_years = jd_analysis.get("experience_years", {})
    consultant_years = consultant_profile.get("years_experience", 0)
    if jd_years.get("max", 20) and consultant_years > jd_years.get("max", 20) + 3:
        validations.append("Consultant overqualified - address in cover letter")
    elif jd_years.get("min", 0) and consultant_years < jd_years.get("min", 0):
        validations.append("Consultant below minimum years - escalate to EM")

    # Rate validation
    consultant_rate = consultant_profile.get("target_rate", 0)
    if consultant_rate == 0:
        validations.append("Verify consultant's current rate before submission")

    return validations


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Read dossier inputs from file
        with open(sys.argv[1], "r") as f:
            inputs = json.load(f)
        dossier = build_dossier(
            consultant_profile=inputs.get("consultant_profile", {}),
            job_posting=inputs.get("job_posting", {}),
            jd_analysis=inputs.get("jd_analysis", {}),
            staleness_result=inputs.get("staleness_result", {}),
            tech_stack_validation=inputs.get("tech_stack_validation", {}),
            vendor_info=inputs.get("vendor_info", {}),
            confidence_score=inputs.get("confidence_score", {}),
        )
        print(json.dumps(dossier, indent=2))
    else:
        print("Dossier Builder - usage: python dossier_builder.py <inputs.json>")
        print("\nDemo mode: create JSON with all required inputs and pass as argument.")
