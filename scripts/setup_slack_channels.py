"""
OG System Slack Channel Setup
===============================
Creates all 7 og-* channels, sets topics/purposes, and saves
the channel map to agents/em/workspace/memory/slack-channel-map.json.

Usage:
    SLACK_BOT_TOKEN=xoxb-... python3 scripts/setup_slack_channels.py
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
if not BOT_TOKEN:
    print("ERROR: Set SLACK_BOT_TOKEN environment variable")
    sys.exit(1)

SLACK_API = "https://slack.com/api"

CHANNEL_MAP_PATH = Path(__file__).parent.parent / "agents" / "em" / "workspace" / "memory" / "slack-channel-map.json"

# Channel definitions: name, topic, purpose
CHANNELS = [
    {
        "name": "og-em-dashboard",
        "topic": "EM daily reports & system health | Posted by Agent EM at 17:00 ET",
        "purpose": "Daily system health reports, weekly retrospectives, agent performance metrics, and quota compliance from the OG System orchestrator.",
    },
    {
        "name": "og-alerts",
        "topic": "CRITICAL & HIGH severity alerts only | Real-time",
        "purpose": "Real-time alerts for profile bans, visa expiry (<30d), duplicate submissions, agent failures (DEAD/ERROR), data quality drops, and quota misses.",
    },
    {
        "name": "og-agent-feed",
        "topic": "Inter-agent message audit trail | All agent communication logged here",
        "purpose": "Transparent log of all messages routed between agents (Z, Jay, Rick, Leroy) through EM. For audit and debugging.",
    },
    {
        "name": "og-daily-hotlist",
        "topic": "Z's prioritized candidate queue | Published daily by 07:00 ET",
        "purpose": "Daily prioritized consultant list (P1-P4 tiers) with visa urgency flags, days on bench, active submission counts, and stale submission follow-ups.",
    },
    {
        "name": "og-kaizen",
        "topic": "Daily improvement observations | One post per day at 17:45 ET",
        "purpose": "Continuous improvement journal. EM posts one PROCESS/QUALITY/SPEED/COST/RISK improvement observation daily. Weekly digest on Fridays.",
    },
    {
        "name": "og-inbound-leads",
        "topic": "Recruiter inbound leads | <15 min detection, <60 min response SLA",
        "purpose": "Real-time tracking of inbound recruiter messages detected by Leroy, positioning responses by Rick, and response time SLA monitoring.",
    },
    {
        "name": "og-human-commands",
        "topic": "Human instructions to OG System | EM reads and routes",
        "purpose": "Direct human instructions: pause submissions, override priorities, approve weight changes, trigger backups. EM interprets and routes to the right agent.",
    },
]


def slack_api(method, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{SLACK_API}/{method}",
        data=data,
        headers={
            "Authorization": f"Bearer {BOT_TOKEN}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def create_channel(name):
    """Create a channel. Returns channel ID or None if already exists."""
    result = slack_api("conversations.create", {"name": name, "is_private": False})

    if result.get("ok"):
        return result["channel"]["id"]

    if result.get("error") == "name_taken":
        # Channel exists, find its ID
        cursor = ""
        while True:
            params = {"types": "public_channel", "limit": 200}
            if cursor:
                params["cursor"] = cursor
            result = slack_api("conversations.list", params)
            if not result.get("ok"):
                return None
            for ch in result.get("channels", []):
                if ch["name"] == name:
                    return ch["id"]
            cursor = result.get("response_metadata", {}).get("next_cursor", "")
            if not cursor:
                break
    return None


def set_topic(channel_id, topic):
    return slack_api("conversations.setTopic", {"channel": channel_id, "topic": topic})


def set_purpose(channel_id, purpose):
    return slack_api("conversations.setPurpose", {"channel": channel_id, "purpose": purpose})


def main():
    print("=" * 60)
    print("  OG System — Slack Channel Setup")
    print("=" * 60)
    print()

    channel_map = {}
    created = 0
    existing = 0

    for ch in CHANNELS:
        name = ch["name"]
        channel_id = create_channel(name)

        if channel_id:
            channel_map[name] = channel_id

            # Set topic and purpose
            set_topic(channel_id, ch["topic"])
            set_purpose(channel_id, ch["purpose"])

            # Join the channel (bot needs to be a member)
            slack_api("conversations.join", {"channel": channel_id})

            print(f"  #{name:25s}  {channel_id}  OK")
            created += 1
        else:
            print(f"  #{name:25s}  FAILED")

    # Save channel map
    CHANNEL_MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CHANNEL_MAP_PATH, "w") as f:
        json.dump(channel_map, f, indent=2)

    print()
    print(f"  Channels ready: {created}/{len(CHANNELS)}")
    print(f"  Channel map saved to: {CHANNEL_MAP_PATH}")
    print()

    # Post welcome message to each channel
    print("  Sending welcome messages...")
    for ch in CHANNELS:
        name = ch["name"]
        if name not in channel_map:
            continue

        welcome = f":white_check_mark: *#{name} is online*\n_{ch['purpose']}_"
        slack_api("chat.postMessage", {
            "channel": channel_map[name],
            "text": welcome,
            "username": "OG System",
            "icon_emoji": ":fire:",
        })
        print(f"    #{name} — welcome posted")

    print()
    print("=" * 60)
    print("  Setup complete. All OG channels are live.")
    print("=" * 60)


if __name__ == "__main__":
    main()
