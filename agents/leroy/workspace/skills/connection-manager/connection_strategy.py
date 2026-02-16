"""
Connection Strategy Manager for Agent Leroy
============================================
Manages LinkedIn connection request targeting and execution per tier with
intelligent note selection and daily limit enforcement.

Usage:
    from connection_manager.connection_strategy import get_connection_targets, execute_connection_request

    targets = get_connection_targets({
        "profile_id": "P-001",
        "tier": "A",
        "date": "2026-02-15",
        "daily_limit": 20
    })

    result = execute_connection_request({
        "profile_id": "P-001",
        "target_id": "T-5678",
        "target_name": "Jane Recruiter",
        "target_title": "Technical Recruiter",
        "note": None,
        "proxy_ip": "192.0.2.15"
    })
"""

import json
import random
from datetime import datetime, timezone
from pathlib import Path


def get_tier_daily_limit(tier: str) -> int:
    """Get daily connection request limit for tier."""
    limits = {
        "A": 20,
        "B": 15,
        "C": 8,
        "D": 0
    }
    return limits.get(tier, 0)


def get_tier_targets(tier: str) -> dict:
    """Get connection targeting strategy for tier."""
    strategies = {
        "A": {
            "tier_name": "Thoroughbred",
            "target_distribution": {
                "tier1_recruiters": 0.40,
                "tier2_recruiters": 0.30,
                "hiring_managers": 0.20,
                "industry_peers": 0.10
            },
            "note_strategy": {
                "no_note": 0.70,
                "generic_note": 0.20,
                "personalized_note": 0.10
            }
        },
        "B": {
            "tier_name": "Growth",
            "target_distribution": {
                "tier1_recruiters": 0.35,
                "tier2_recruiters": 0.35,
                "hr_professionals": 0.20,
                "industry_peers": 0.10
            },
            "note_strategy": {
                "no_note": 0.70,
                "generic_note": 0.25,
                "personalized_note": 0.05
            }
        },
        "C": {
            "tier_name": "Warming",
            "target_distribution": {
                "open_networkers": 0.40,
                "alumni": 0.30,
                "group_members": 0.20,
                "industry_peers": 0.10
            },
            "note_strategy": {
                "no_note": 0.80,
                "generic_note": 0.15,
                "personalized_note": 0.05
            }
        },
        "D": {
            "tier_name": "Dormant",
            "target_distribution": {},
            "note_strategy": {}
        }
    }
    return strategies.get(tier, {})


def _generate_targets_list(tier: str, daily_limit: int) -> list:
    """
    Generate list of target profiles for connection (stub - in real usage,
    would query from database of scraped targets).
    """
    # This is a stub - in production, this would query from a target database
    # For demo, generate synthetic targets

    targets = []
    strategy = get_tier_targets(tier)
    distribution = strategy.get("target_distribution", {})

    # Distribute targets across categories
    for category, proportion in distribution.items():
        count = max(1, int(daily_limit * proportion))
        for i in range(count):
            target_id = f"T-{random.randint(100000, 999999)}"
            targets.append({
                "target_id": target_id,
                "category": category,
                "name": f"{category.replace('_', ' ').title()} {i+1}",
                "title": _generate_title_for_category(category),
                "company": _generate_company_for_category(category, tier),
                "connection_count": random.randint(50, 2000)
            })

    return targets[:daily_limit]


def _generate_title_for_category(category: str) -> str:
    """Generate realistic title for target category."""
    titles = {
        "tier1_recruiters": ["Senior Technical Recruiter", "IT Staffing Manager", "Technical Staffing Consultant"],
        "tier2_recruiters": ["Technical Recruiter", "Staffing Specialist", "Recruiting Coordinator"],
        "hiring_managers": ["Engineering Manager", "Team Lead", "Development Manager"],
        "hr_professionals": ["HR Manager", "Talent Acquisition Specialist", "HR Coordinator"],
        "industry_peers": ["Senior Developer", "Software Engineer", "Tech Lead"],
        "open_networkers": ["Freelancer", "Contractor", "Consultant"],
        "alumni": ["Alumni", "Graduate", "Fellow"],
        "group_members": ["Group Member", "Community Member", "Network Member"]
    }
    choices = titles.get(category, ["Professional"])
    return random.choice(choices)


def _generate_company_for_category(category: str, tier: str) -> str:
    """Generate realistic company for target category."""
    tier1_firms = ["Cognizant", "Infosys", "Accenture", "Deloitte", "IBM", "Microsoft", "Google"]
    tier2_firms = ["Stripe", "Figma", "Okta", "Twilio", "Databricks"]
    startups = ["StartupXYZ", "TechStudio", "Innovation Labs", "Digital Ventures"]

    if "tier1" in category or tier == "A":
        return random.choice(tier1_firms)
    elif "tier2" in category or tier == "B":
        return random.choice(tier2_firms)
    else:
        return random.choice(startups)


def get_connection_targets(inputs: dict) -> dict:
    """
    Get recommended connection targets for a profile on a given date.

    Args:
        inputs: Dict with keys:
            - profile_id (str): Profile identifier
            - tier (str): A, B, C, or D
            - date (str): YYYY-MM-DD
            - daily_limit (int, optional): Override daily limit

    Returns:
        Dict with target list, distribution breakdown, note strategy.
    """
    tier = inputs["tier"]
    daily_limit = inputs.get("daily_limit", get_tier_daily_limit(tier))
    strategy = get_tier_targets(tier)

    if not strategy:
        return {
            "profile_id": inputs["profile_id"],
            "date": inputs["date"],
            "tier": tier,
            "daily_limit": 0,
            "targets": [],
            "reason": "Tier D: no activity"
        }

    # Generate targets for today
    targets = _generate_targets_list(tier, daily_limit)

    result = {
        "profile_id": inputs["profile_id"],
        "date": inputs["date"],
        "tier": tier,
        "tier_name": strategy.get("tier_name", ""),
        "daily_limit": daily_limit,
        "targets_available": len(targets),
        "targets": targets,
        "target_distribution": strategy.get("target_distribution", {}),
        "note_strategy": strategy.get("note_strategy", {}),
        "guidance": {
            "priority_categories": list(strategy.get("target_distribution", {}).keys())[:3],
            "note_guidance": "70% no note, 20% generic, 10% personalized"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return result


def select_note_type(tier: str) -> str:
    """
    Randomly select note type based on tier strategy.
    Returns: 'none', 'generic', or 'personalized'
    """
    strategy = get_tier_targets(tier)
    note_strategy = strategy.get("note_strategy", {})

    rand = random.random()
    cumulative = 0

    for note_type in ["no_note", "generic_note", "personalized_note"]:
        cumulative += note_strategy.get(note_type, 0)
        if rand < cumulative:
            return note_type.replace("_note", "").replace("no", "none")

    return "none"


def generate_generic_note() -> str:
    """Generate generic connection note."""
    notes = [
        "Hi! I'd like to connect and expand my professional network.",
        "Hi! Let's connect and share industry insights.",
        "Hi! I'm interested in connecting with professionals in your field.",
        "Hi! Would love to grow my network. Let's connect!"
    ]
    return random.choice(notes)


def generate_personalized_note(target: dict) -> str:
    """Generate personalized connection note based on target info."""
    target_title = target.get("title", "professional")
    target_company = target.get("company", "their company")

    templates = [
        f"Hi! I noticed your work in {target_company} and would love to connect.",
        f"Hi! As a {target_title}, I think we'd have great insights to share.",
        f"Hi! I'm impressed with your background at {target_company}. Let's connect!"
    ]
    return random.choice(templates)


def execute_connection_request(inputs: dict) -> dict:
    """
    Execute a single connection request.

    Args:
        inputs: Dict with keys:
            - profile_id (str): Profile making the request
            - target_id (str): Target profile ID
            - target_name (str): Target's name
            - target_title (str): Target's title
            - note (str or None): Connection note (None = no note)
            - proxy_ip (str): Proxy IP to use

    Returns:
        Dict with connection request result.
    """
    profile_id = inputs["profile_id"]
    target_id = inputs["target_id"]
    note = inputs.get("note")

    now = datetime.now(timezone.utc)

    request_id = f"CONN-REQ-{now.strftime('%Y%m%d%H%M%S')}-{random.randint(10000, 99999)}"

    result = {
        "request_id": request_id,
        "profile_id": profile_id,
        "target_id": target_id,
        "target_name": inputs.get("target_name", ""),
        "target_title": inputs.get("target_title", ""),
        "status": "SENT",
        "note_sent": note is not None,
        "note_type": "none" if note is None else ("personalized" if "impressed" in note.lower() else "generic"),
        "proxy_ip": inputs.get("proxy_ip", ""),
        "timestamp": now.isoformat(),
        "details": {
            "note_content": note if note else None,
            "timing": f"Connection sent at {now.isoformat()}",
            "target_context": {
                "name": inputs.get("target_name"),
                "title": inputs.get("target_title"),
                "company": inputs.get("target_company", "")
            }
        }
    }

    return result


def execute_batch_connections(inputs: dict) -> dict:
    """
    Execute multiple connection requests for a profile on a date.

    Args:
        inputs: Dict with keys:
            - profile_id (str)
            - tier (str)
            - date (str)
            - targets (list): List of target dicts
            - proxy_ip (str)

    Returns:
        Dict with batch results.
    """
    profile_id = inputs["profile_id"]
    tier = inputs["tier"]
    targets = inputs.get("targets", [])
    proxy_ip = inputs.get("proxy_ip", "")

    now = datetime.now(timezone.utc)

    # Get note strategy for tier
    strategy = get_tier_targets(tier)
    note_strategy = strategy.get("note_strategy", {})

    requests_sent = []
    note_stats = {"none": 0, "generic": 0, "personalized": 0}

    for target in targets:
        # Determine note for this request
        rand = random.random()
        cumulative = 0
        selected_note = None
        note_type = "none"

        for note_key, prob in note_strategy.items():
            cumulative += prob
            if rand < cumulative:
                if note_key == "no_note":
                    selected_note = None
                    note_type = "none"
                elif note_key == "generic_note":
                    selected_note = generate_generic_note()
                    note_type = "generic"
                elif note_key == "personalized_note":
                    selected_note = generate_personalized_note(target)
                    note_type = "personalized"
                break

        # Execute connection
        result = execute_connection_request({
            "profile_id": profile_id,
            "target_id": target.get("target_id"),
            "target_name": target.get("name"),
            "target_title": target.get("title"),
            "target_company": target.get("company"),
            "note": selected_note,
            "proxy_ip": proxy_ip
        })

        requests_sent.append(result)
        note_stats[note_type] += 1

    batch_result = {
        "profile_id": profile_id,
        "date": inputs["date"],
        "tier": tier,
        "total_requests": len(requests_sent),
        "requests": requests_sent,
        "statistics": {
            "note_distribution": note_stats,
            "no_note_percentage": round(note_stats["none"] / max(1, len(requests_sent)) * 100, 1),
            "with_note_percentage": round((note_stats["generic"] + note_stats["personalized"]) / max(1, len(requests_sent)) * 100, 1)
        },
        "timestamp": now.isoformat()
    }

    return batch_result


# --- CLI interface for testing ---
if __name__ == "__main__":
    print("=== TIER A: CONNECTION TARGETS ===\n")
    targets_a = get_connection_targets({
        "profile_id": "P-001",
        "tier": "A",
        "date": "2026-02-15"
    })
    print(json.dumps(targets_a, indent=2))

    print("\n\n=== SINGLE CONNECTION REQUEST ===\n")
    conn = execute_connection_request({
        "profile_id": "P-001",
        "target_id": "T-5678",
        "target_name": "Jane Recruiter",
        "target_title": "Senior Technical Recruiter",
        "target_company": "TechStaff Inc",
        "note": "Hi! I noticed your work at TechStaff and would love to connect.",
        "proxy_ip": "192.0.2.15"
    })
    print(json.dumps(conn, indent=2))

    print("\n\n=== BATCH CONNECTIONS FOR TIER C ===\n")
    targets_c = get_connection_targets({
        "profile_id": "P-002",
        "tier": "C",
        "date": "2026-02-15"
    })
    batch = execute_batch_connections({
        "profile_id": "P-002",
        "tier": "C",
        "date": "2026-02-15",
        "targets": targets_c["targets"][:5],
        "proxy_ip": "192.0.2.16"
    })
    print(json.dumps(batch, indent=2))
