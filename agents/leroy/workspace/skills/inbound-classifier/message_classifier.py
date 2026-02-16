"""
Message Classifier for Agent Leroy
===================================
Classifies inbound LinkedIn messages into A/B/C/D/E classes based on sender profile,
message content, and pattern matching against rules.

Usage:
    from inbound_classifier.message_classifier import classify_message

    result = classify_message({
        "message_id": "MSG-1234",
        "profile_id": "P-001",
        "sender_name": "John Smith",
        "sender_title": "Senior Recruiter",
        "sender_company": "TechStaff Inc",
        "message_text": "Hi, we have a great Python role for a midlevel developer...",
        "timestamp": "2026-02-15T10:30:00Z"
    })
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path


RULES_FILE = Path(__file__).parent / "classifier_rules.json"


def load_rules() -> dict:
    """Load classification rules from config."""
    with open(RULES_FILE, "r") as f:
        return json.load(f)


def _normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    return text.lower().strip()


def _contains_keywords(text: str, keywords: list) -> tuple:
    """Check if text contains any keywords. Returns (found, count, matched_keywords)."""
    text_lower = _normalize_text(text)
    matched = []
    count = 0

    for keyword in keywords:
        if keyword.lower() in text_lower:
            matched.append(keyword)
            # Count occurrences
            count += text_lower.count(keyword.lower())

    return len(matched) > 0, count, matched


def _check_trust_safety(message_text: str, rules: dict) -> bool:
    """Check if message is a Trust & Safety alert."""
    trust_keywords = rules["keyword_lists"]["trust_safety_keywords"]
    has_keywords, _, _ = _contains_keywords(message_text, trust_keywords)
    return has_keywords


def _check_recruiter_title(title: str, rules: dict) -> bool:
    """Check if sender has recruiter-like title."""
    recruiter_titles = rules["keyword_lists"]["recruiter_titles"]
    title_lower = _normalize_text(title)

    for recruiter_title in recruiter_titles:
        if recruiter_title.lower() in title_lower:
            return True

    return False


def _check_specific_tech(message_text: str, rules: dict) -> tuple:
    """Check for specific tech/role mentions. Returns (has_tech, count, matched)."""
    tech_keywords = rules["keyword_lists"]["specific_role_keywords"]
    return _contains_keywords(message_text, tech_keywords)


def _check_availability(message_text: str, rules: dict) -> bool:
    """Check for availability/interest questions."""
    avail_keywords = rules["keyword_lists"]["availability_keywords"]
    has_keywords, _, _ = _contains_keywords(message_text, avail_keywords)
    return has_keywords


def _check_tier1_firm(company: str, rules: dict) -> bool:
    """Check if company is a known Tier 1 staffing firm."""
    tier1_firms = rules["company_rules"]["known_tier1_staffing"]
    company_lower = _normalize_text(company)

    for firm in tier1_firms:
        if firm.lower() in company_lower:
            return True

    return False


def _check_tier2_firm(company: str, rules: dict) -> bool:
    """Check if company is a known Tier 2 staffing firm."""
    tier2_firms = rules["company_rules"]["known_tier2_staffing"]
    company_lower = _normalize_text(company)

    for firm in tier2_firms:
        if firm.lower() in company_lower:
            return True

    return False


def _check_mlm(message_text: str, rules: dict) -> bool:
    """Check for MLM indicators."""
    mlm_keywords = rules["keyword_lists"]["mlm_keywords"]
    has_keywords, _, _ = _contains_keywords(message_text, mlm_keywords)
    return has_keywords


def _check_insurance(message_text: str, rules: dict) -> bool:
    """Check for insurance indicators."""
    insurance_keywords = rules["keyword_lists"]["insurance_keywords"]
    has_keywords, _, _ = _contains_keywords(message_text, insurance_keywords)
    return has_keywords


def _check_sales_pitch(message_text: str, rules: dict) -> bool:
    """Check for generic sales pitch indicators."""
    sales_keywords = rules["keyword_lists"]["sales_pitch_keywords"]
    has_keywords, _, _ = _contains_keywords(message_text, sales_keywords)
    return has_keywords


def _classify_message(inputs: dict, rules: dict) -> tuple:
    """
    Classify message into class A/B/C/D/E with confidence score.
    Returns (class, confidence, reasoning).
    """
    message_text = inputs.get("message_text", "")
    sender_title = inputs.get("sender_title", "")
    sender_company = inputs.get("sender_company", "")

    # Check for SUSPICIOUS/E first (overrides everything)
    if _check_trust_safety(message_text, rules):
        return ("E", 1.0, ["LinkedIn Trust & Safety alert"])

    # Check for SPAM/D
    if _check_mlm(message_text, rules):
        return ("D", 0.95, ["MLM indicators detected"])

    if _check_insurance(message_text, rules):
        return ("D", 0.95, ["Insurance pitch detected"])

    if _check_sales_pitch(message_text, rules):
        return ("D", 0.80, ["Generic sales pitch"])

    # Check for HOT/A
    is_recruiter = _check_recruiter_title(sender_title, rules)
    has_tech, tech_count, matched_tech = _check_specific_tech(message_text, rules)
    has_availability = _check_availability(message_text, rules)
    is_tier1 = _check_tier1_firm(sender_company, rules)
    is_tier2 = _check_tier2_firm(sender_company, rules)

    a_indicators = []
    a_score = 0.0

    if is_recruiter:
        a_indicators.append("recruiter_title")
        a_score += 0.3

    if has_tech:
        a_indicators.append(f"specific_tech: {', '.join(matched_tech[:3])}")
        a_score += 0.3

    if has_availability:
        a_indicators.append("availability_question")
        a_score += 0.2

    if is_tier1:
        a_indicators.append("tier1_firm")
        a_score += 0.25
    elif is_tier2:
        a_indicators.append("tier2_firm")
        a_score += 0.15

    # Class A if recruiter + tech/availability + good firm
    if is_recruiter and (has_tech or has_availability) and (is_tier1 or is_tier2):
        return ("A", min(0.95, a_score), a_indicators)

    # Class A if strong indicators
    if a_score >= 0.7:
        return ("A", a_score, a_indicators)

    # Check for WARM/B
    b_indicators = []
    b_score = 0.0

    if is_recruiter:
        b_indicators.append("recruiter_title")
        b_score += 0.3

    # HR but not dedicated recruiter
    if "hr" in _normalize_text(sender_title) and not is_recruiter:
        b_indicators.append("hr_title")
        b_score += 0.2

    # Vague opportunity mention without specific role
    if has_availability or "opportunity" in _normalize_text(message_text):
        b_indicators.append("opportunity_mention")
        b_score += 0.2

    if b_score >= 0.5:
        return ("B", b_score, b_indicators)

    # Check for NETWORKING/C
    # Generic connection, industry peer, alumni
    message_lower = _normalize_text(message_text)
    c_indicators = []

    if "connect" in message_lower or "connect with you" in message_lower:
        c_indicators.append("generic_connection")

    if any(keyword in message_lower for keyword in ["industry", "peers", "alumni", "group", "fellow"]):
        c_indicators.append("industry_peer_or_group")

    if c_indicators:
        return ("C", 0.70, c_indicators)

    # Default to NETWORKING/C if none of above
    return ("C", 0.50, ["generic_inbound_message"])


def classify_message(inputs: dict) -> dict:
    """
    Classify a single inbound LinkedIn message.

    Args:
        inputs: Dict with keys:
            - message_id (str): Unique message identifier
            - profile_id (str): LinkedIn profile that received the message
            - sender_name (str): Name of sender
            - sender_title (str): Job title of sender
            - sender_company (str): Company of sender
            - sender_id (str, optional): LinkedIn ID of sender
            - message_text (str): Body of the message
            - timestamp (str): ISO-8601 timestamp when received

    Returns:
        Dict with classification, confidence, routing, and metadata.
    """
    rules = load_rules()

    # Classify
    classification, confidence, reasoning = _classify_message(inputs, rules)

    # Get class definition
    class_def = rules["class_definitions"][classification]

    # Build routing instruction
    routing = {
        "route_to": class_def["route_to"],
        "priority": class_def["priority"],
        "sla_minutes": class_def["sla_minutes"],
        "action": class_def.get("action", "evaluate")
    }

    # Build opportunity summary if applicable
    opportunity_summary = None
    if classification in ["A", "B"]:
        # Extract opportunity details
        message_text = inputs.get("message_text", "")
        has_tech, _, matched_tech = _check_specific_tech(message_text, rules)
        location_match = re.search(r"(new york|boston|san francisco|seattle|austin|denver|chicago|atlanta|miami|los angeles)", message_text.lower())

        summary_parts = []
        if matched_tech:
            summary_parts.append(f"{', '.join(matched_tech[:3])} role")
        if location_match:
            summary_parts.append(location_match.group(1))

        if summary_parts:
            opportunity_summary = ", ".join(summary_parts)

    now = datetime.now(timezone.utc)

    result = {
        "message_id": inputs.get("message_id", "UNKNOWN"),
        "profile_id": inputs.get("profile_id", "UNKNOWN"),
        "classification": classification,
        "class_label": class_def["label"],
        "confidence": round(confidence, 2),
        "reasoning": reasoning,
        "routing": routing,
        "sender_context": {
            "name": inputs.get("sender_name", ""),
            "title": inputs.get("sender_title", ""),
            "company": inputs.get("sender_company", ""),
            "sender_id": inputs.get("sender_id", ""),
            "company_tier": "TIER_1" if _check_tier1_firm(inputs.get("sender_company", ""), rules) else
                            "TIER_2" if _check_tier2_firm(inputs.get("sender_company", ""), rules) else
                            "OTHER"
        },
        "opportunity_summary": opportunity_summary,
        "timestamp": inputs.get("timestamp", now.isoformat()),
        "classified_at": now.isoformat()
    }

    return result


def classify_batch(message_list: list) -> list:
    """
    Classify multiple messages and return sorted by priority/urgency.

    Args:
        message_list: List of message dicts, each matching classify_message input schema.

    Returns:
        List of classified results, sorted by priority (A, B, C, D, E then confidence).
    """
    results = [classify_message(msg) for msg in message_list]

    # Sort by class priority, then by confidence
    class_priority = {"E": 0, "A": 1, "B": 2, "C": 3, "D": 4}
    results.sort(
        key=lambda x: (class_priority.get(x["classification"], 5), -x["confidence"])
    )

    return results


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Read input from file
        with open(sys.argv[1], "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            results = classify_batch(data)
        else:
            results = classify_message(data)
        print(json.dumps(results, indent=2))
    else:
        # Demo with sample messages
        print("=== CLASS A: HOT RECRUITER ===\n")
        class_a = {
            "message_id": "MSG-001",
            "profile_id": "P-001",
            "sender_name": "Sarah Johnson",
            "sender_title": "Senior Technical Recruiter",
            "sender_company": "TechStaff Inc",
            "sender_id": "SEND-001",
            "message_text": "Hi! We have an amazing Python/AWS opportunity for a senior developer in Boston. The client is looking for someone who can start immediately. Are you available for a discussion?",
            "timestamp": "2026-02-15T10:30:00Z"
        }
        result_a = classify_message(class_a)
        print(json.dumps(result_a, indent=2))

        print("\n\n=== CLASS B: WARM HR ===\n")
        class_b = {
            "message_id": "MSG-002",
            "profile_id": "P-001",
            "sender_name": "Mike Chen",
            "sender_title": "HR Manager",
            "sender_company": "TechCorp",
            "sender_id": "SEND-002",
            "message_text": "Hi, I'd like to connect! We have some exciting opportunities in tech that might interest you.",
            "timestamp": "2026-02-15T11:00:00Z"
        }
        result_b = classify_message(class_b)
        print(json.dumps(result_b, indent=2))

        print("\n\n=== CLASS C: NETWORKING ===\n")
        class_c = {
            "message_id": "MSG-003",
            "profile_id": "P-001",
            "sender_name": "Alex Rodriguez",
            "sender_title": "Senior Developer",
            "sender_company": "StartupXYZ",
            "sender_id": "SEND-003",
            "message_text": "Hey! Would love to connect with fellow developers in the tech industry.",
            "timestamp": "2026-02-15T11:30:00Z"
        }
        result_c = classify_message(class_c)
        print(json.dumps(result_c, indent=2))

        print("\n\n=== CLASS D: SPAM ===\n")
        class_d = {
            "message_id": "MSG-004",
            "profile_id": "P-001",
            "sender_name": "Insurance Agent",
            "sender_title": "Life Insurance Specialist",
            "sender_company": "Insurance Corp",
            "sender_id": "SEND-004",
            "message_text": "Limited time offer! Get life insurance coverage today. Don't miss out on this special deal!",
            "timestamp": "2026-02-15T12:00:00Z"
        }
        result_d = classify_message(class_d)
        print(json.dumps(result_d, indent=2))

        print("\n\n=== CLASS E: SUSPICIOUS ===\n")
        class_e = {
            "message_id": "MSG-005",
            "profile_id": "P-001",
            "sender_name": "LinkedIn Security",
            "sender_title": "Trust & Safety",
            "sender_company": "LinkedIn",
            "sender_id": "SEND-005",
            "message_text": "Verify your account identity immediately due to unusual activity detected on your account.",
            "timestamp": "2026-02-15T12:30:00Z"
        }
        result_e = classify_message(class_e)
        print(json.dumps(result_e, indent=2))
