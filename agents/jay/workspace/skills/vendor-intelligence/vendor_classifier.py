"""
Vendor Classifier for Agent Jay
================================
Classifies vendors into tiers and looks up known information.
Input: vendor name. Output: tier, known info, confidence.

Usage:
    from vendor_classifier import classify_vendor, get_vendor_database

    result = classify_vendor("Robert Half")
    # Returns tier 1 with known info
"""

import json
from typing import Dict, Tuple, Optional
from pathlib import Path


# Known vendor database - updated from vendor-database.md memory file
KNOWN_VENDORS = {
    "Tier 1": {
        "Insight Global": {
            "response_rate": "95%",
            "ghost_rate": "2%",
            "known_clients": ["Tech companies", "Financial services", "Fortune 500"],
            "placements_count": 500,
            "confidence": "high"
        },
        "Robert Half": {
            "response_rate": "92%",
            "ghost_rate": "3%",
            "known_clients": ["Tech companies", "Fortune 500", "Mid-market"],
            "placements_count": 450,
            "confidence": "high"
        },
        "TEKsystems": {
            "response_rate": "88%",
            "ghost_rate": "5%",
            "known_clients": ["Large enterprises", "Tech companies"],
            "placements_count": 400,
            "confidence": "high"
        },
        "Infosys": {
            "response_rate": "85%",
            "ghost_rate": "8%",
            "known_clients": ["Enterprise", "Fortune 500"],
            "placements_count": 350,
            "confidence": "high"
        },
        "Cognizant": {
            "response_rate": "84%",
            "ghost_rate": "9%",
            "known_clients": ["Enterprise", "Financial services"],
            "placements_count": 330,
            "confidence": "high"
        },
        "TCS": {
            "response_rate": "80%",
            "ghost_rate": "12%",
            "known_clients": ["Enterprise", "Large corporations"],
            "placements_count": 300,
            "confidence": "high"
        },
        "Wipro": {
            "response_rate": "79%",
            "ghost_rate": "13%",
            "known_clients": ["Enterprise", "Tech"],
            "placements_count": 280,
            "confidence": "high"
        },
        "Accenture": {
            "response_rate": "75%",
            "ghost_rate": "15%",
            "known_clients": ["Enterprise", "Fortune 500"],
            "placements_count": 250,
            "confidence": "high"
        },
    },
    "Tier 2": {
        "Heidrick & Struggles": {
            "response_rate": "70%",
            "ghost_rate": "20%",
            "known_clients": ["Mid-market", "Tech startups"],
            "placements_count": 100,
            "confidence": "high"
        },
        "Kforce": {
            "response_rate": "68%",
            "ghost_rate": "22%",
            "known_clients": ["Tech companies", "Mid-market"],
            "placements_count": 80,
            "confidence": "medium"
        },
        "On Assignment": {
            "response_rate": "65%",
            "ghost_rate": "25%",
            "known_clients": ["Tech", "Fortune 500"],
            "placements_count": 60,
            "confidence": "medium"
        },
    },
    "Tier 3": {
        "Unknown Recruiter": {
            "response_rate": "40%",
            "ghost_rate": "60%",
            "known_clients": ["Unknown"],
            "placements_count": 0,
            "confidence": "low"
        },
        "Local Body Shop": {
            "response_rate": "35%",
            "ghost_rate": "65%",
            "known_clients": ["Mid-market"],
            "placements_count": 5,
            "confidence": "low"
        },
    }
}


def normalize_vendor_name(name: str) -> str:
    """Normalize vendor name for matching (lowercase, trim)."""
    return name.lower().strip()


def find_vendor_tier(vendor_name: str) -> Tuple[str, Optional[Dict]]:
    """
    Find vendor in known database and return tier + info.
    Returns: (tier_number, vendor_info_dict or None)
    If not found, returns ("unknown", None)
    """
    normalized = normalize_vendor_name(vendor_name)

    for tier, vendors in KNOWN_VENDORS.items():
        for known_name, info in vendors.items():
            if normalize_vendor_name(known_name) == normalized:
                tier_num = tier.replace("Tier ", "")
                return tier_num, info

    return "unknown", None


def classify_vendor(vendor_name: str) -> dict:
    """
    Classify a vendor into tier and return known information.

    Args:
        vendor_name: Vendor name to classify

    Returns:
        Dict with tier, known info, confidence, and notes.
    """
    tier, vendor_info = find_vendor_tier(vendor_name)

    result = {
        "vendor_name": vendor_name,
        "tier": tier,
        "confidence_of_classification": "high" if tier != "unknown" else "low"
    }

    if vendor_info:
        result.update({
            "response_rate": vendor_info.get("response_rate", "unknown"),
            "ghost_rate": vendor_info.get("ghost_rate", "unknown"),
            "known_clients": vendor_info.get("known_clients", []),
            "placement_count": vendor_info.get("placements_count", 0),
            "data_confidence": vendor_info.get("confidence", "unknown"),
            "notes": f"Known Tier {tier} vendor with established track record"
        })
    else:
        result.update({
            "response_rate": "unknown",
            "ghost_rate": "unknown",
            "known_clients": [],
            "placement_count": 0,
            "data_confidence": "none",
            "notes": f"Unknown vendor. Recommend manual research before submission."
        })

    return result


def get_vendor_database() -> Dict:
    """Return the full vendor database."""
    return KNOWN_VENDORS


def get_tier_characteristics(tier: str) -> dict:
    """Get general characteristics of a vendor tier."""
    characteristics = {
        "1": {
            "label": "Top-tier established vendors",
            "description": "Large, well-established vendors with track records and multiple clients",
            "typical_response_rate": "80-95%",
            "typical_ghost_rate": "2-15%",
            "reliability": "high",
            "confidence_boost": 1.5
        },
        "2": {
            "label": "Regional specialists and growing vendors",
            "description": "Solid mid-market vendors with good track records",
            "typical_response_rate": "60-75%",
            "typical_ghost_rate": "20-30%",
            "reliability": "medium",
            "confidence_boost": 0.0
        },
        "3": {
            "label": "Small vendors and body shops",
            "description": "Body shops and small niche vendors with higher risk",
            "typical_response_rate": "30-50%",
            "typical_ghost_rate": "50-70%",
            "reliability": "low",
            "confidence_boost": -1.0
        },
        "unknown": {
            "label": "Unvetted vendor",
            "description": "Vendor not in knowledge base. Requires manual research.",
            "typical_response_rate": "unknown",
            "typical_ghost_rate": "unknown",
            "reliability": "unknown",
            "confidence_boost": 0.0
        }
    }

    return characteristics.get(tier, characteristics["unknown"])


# --- CLI interface for testing ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        vendor_name = sys.argv[1]
        result = classify_vendor(vendor_name)
        print(json.dumps(result, indent=2))
    else:
        # Demo with sample vendors
        test_vendors = [
            "Robert Half",
            "Insight Global",
            "Unknown Recruiter Inc",
            "Accenture",
            "Local Body Shop",
            "TCS"
        ]

        print("=== VENDOR CLASSIFICATION DEMO ===\n")
        for vendor in test_vendors:
            result = classify_vendor(vendor)
            print(json.dumps(result, indent=2))
            print()
