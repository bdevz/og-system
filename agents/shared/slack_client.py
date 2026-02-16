"""
OG System Shared Slack Client
==============================
Lightweight Slack client used by all OG agents to post messages,
alerts, files, and reactions to the og-* channels.

Usage:
    from slack_client import post_message, post_alert, post_to_channel

    post_to_channel("og-alerts", "Profile P-042-A banned by LinkedIn", agent="Leroy")
    post_message(channel_id, "Hello", agent="EM")

Environment:
    SLACK_BOT_TOKEN  - Bot token (xoxb-...), required
"""

import json
import os
import urllib.request
from pathlib import Path
from typing import Optional, Dict, Any


SLACK_API = "https://slack.com/api"

# Agent identity map for chat:write.customize
AGENT_IDENTITIES = {
    "Z":     {"username": "Agent Z",     "icon_emoji": ":bar_chart:"},
    "Jay":   {"username": "Agent Jay",   "icon_emoji": ":mag:"},
    "Rick":  {"username": "Agent Rick",  "icon_emoji": ":dart:"},
    "Leroy": {"username": "Agent Leroy", "icon_emoji": ":link:"},
    "EM":    {"username": "Agent EM",    "icon_emoji": ":robot_face:"},
    "OG":    {"username": "OG System",   "icon_emoji": ":fire:"},
}

# Channel map: logical name -> Slack channel ID
# Loaded lazily from slack-channel-map.json
_channel_map: Optional[Dict[str, str]] = None
_channel_map_path = Path(__file__).parent.parent / "em" / "workspace" / "memory" / "slack-channel-map.json"


def _get_token() -> str:
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        raise RuntimeError("SLACK_BOT_TOKEN environment variable not set")
    return token


def _load_channel_map() -> Dict[str, str]:
    global _channel_map
    if _channel_map is not None:
        return _channel_map

    if _channel_map_path.exists():
        with open(_channel_map_path) as f:
            _channel_map = json.load(f)
    else:
        _channel_map = {}

    return _channel_map


def _slack_api_call(method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Make a Slack API call and return the response."""
    token = _get_token()
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        f"{SLACK_API}/{method}",
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def resolve_channel(name: str) -> str:
    """
    Resolve a channel name to a Slack channel ID.

    Accepts:
        - Channel ID directly (starts with C/D/G)
        - Logical name like "og-alerts" (looked up in channel map)
        - Name with # prefix like "#og-alerts"
    """
    if name and name[0] in ("C", "D", "G") and len(name) > 8:
        return name

    clean = name.lstrip("#")
    channel_map = _load_channel_map()

    if clean in channel_map:
        return channel_map[clean]

    raise ValueError(
        f"Channel '{name}' not found in channel map. "
        f"Available: {list(channel_map.keys())}"
    )


def post_message(
    channel: str,
    text: str,
    agent: str = "OG",
    thread_ts: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Post a message to a Slack channel with agent identity.

    Args:
        channel: Channel ID or logical name (e.g. "og-alerts")
        text: Message text (supports Slack markdown)
        agent: Agent name for identity (Z, Jay, Rick, Leroy, EM, OG)
        thread_ts: Optional thread timestamp to reply in thread
    """
    channel_id = resolve_channel(channel)
    identity = AGENT_IDENTITIES.get(agent, AGENT_IDENTITIES["OG"])

    payload = {
        "channel": channel_id,
        "text": text,
        "username": identity["username"],
        "icon_emoji": identity["icon_emoji"],
    }

    if thread_ts:
        payload["thread_ts"] = thread_ts

    result = _slack_api_call("chat.postMessage", payload)

    if not result.get("ok"):
        raise RuntimeError(f"Slack API error: {result.get('error')}")

    return result


def post_to_channel(
    channel_name: str,
    text: str,
    agent: str = "OG",
    thread_ts: Optional[str] = None,
) -> Dict[str, Any]:
    """Convenience alias for post_message using logical channel names."""
    return post_message(channel_name, text, agent=agent, thread_ts=thread_ts)


def post_alert(alert_obj: Any, agent: str = "EM") -> Dict[str, Any]:
    """
    Post an Alert object to its designated Slack channel.

    Args:
        alert_obj: An Alert instance with .channel, .to_slack_message(), .severity
        agent: Agent posting the alert (default EM)
    """
    # Map old channel names to og-* names
    channel_remap = {
        "#alerts": "og-alerts",
        "#em-dashboard": "og-em-dashboard",
        "#daily-hotlist": "og-daily-hotlist",
        "#inbound-leads": "og-inbound-leads",
        "#kaizen": "og-kaizen",
        "#agent-feed": "og-agent-feed",
        "#human-commands": "og-human-commands",
    }

    raw_channel = getattr(alert_obj, "channel", "#alerts")
    channel = channel_remap.get(raw_channel, raw_channel)
    text = alert_obj.to_slack_message()

    return post_message(channel, text, agent=agent)


def add_reaction(
    channel: str,
    timestamp: str,
    emoji: str,
) -> Dict[str, Any]:
    """
    Add a reaction emoji to a message.

    Args:
        channel: Channel ID or logical name
        timestamp: Message timestamp (ts)
        emoji: Emoji name without colons (e.g. "white_check_mark")
    """
    channel_id = resolve_channel(channel)
    return _slack_api_call("reactions.add", {
        "channel": channel_id,
        "timestamp": timestamp,
        "name": emoji,
    })


def upload_text_snippet(
    channel: str,
    content: str,
    filename: str,
    title: Optional[str] = None,
    agent: str = "OG",
) -> Dict[str, Any]:
    """
    Upload a text snippet to a Slack channel.

    Args:
        channel: Channel ID or logical name
        content: File content as string
        filename: Filename (e.g. "hotlist-2026-02-16.txt")
        title: Optional title for the file
        agent: Agent identity for the accompanying message
    """
    channel_id = resolve_channel(channel)
    token = _get_token()

    # Step 1: Get upload URL
    params = urllib.parse.urlencode({
        "filename": filename,
        "length": len(content.encode("utf-8")),
    })
    req = urllib.request.Request(
        f"{SLACK_API}/files.getUploadURLExternal?{params}",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    with urllib.request.urlopen(req) as resp:
        url_result = json.loads(resp.read().decode())

    if not url_result.get("ok"):
        raise RuntimeError(f"Failed to get upload URL: {url_result.get('error')}")

    # Step 2: Upload file content
    upload_url = url_result["upload_url"]
    upload_req = urllib.request.Request(
        upload_url,
        data=content.encode("utf-8"),
        headers={"Content-Type": "text/plain; charset=utf-8"},
        method="POST",
    )
    urllib.request.urlopen(upload_req)

    # Step 3: Complete upload
    complete_payload = {
        "files": [{"id": url_result["file_id"], "title": title or filename}],
        "channel_id": channel_id,
    }
    return _slack_api_call("files.completeUploadExternal", complete_payload)


def reload_channel_map():
    """Force reload the channel map from disk."""
    global _channel_map
    _channel_map = None
    _load_channel_map()


# --- CLI test ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python slack_client.py <channel> <message> [agent]")
        print("  e.g.: python slack_client.py og-alerts 'Test alert' EM")
        sys.exit(1)

    channel = sys.argv[1]
    text = sys.argv[2]
    agent = sys.argv[3] if len(sys.argv) > 3 else "OG"

    result = post_message(channel, text, agent=agent)
    print(f"Posted to {channel} as {agent}: ts={result['ts']}")
