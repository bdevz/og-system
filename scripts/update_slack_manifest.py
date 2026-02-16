"""
Update the Popping Slack app manifest with all scopes and events
needed for OG System's multi-agent operation.
"""

import json
import os
import sys
import urllib.request
import urllib.parse

CONFIG_TOKEN = os.environ.get("SLACK_CONFIG_TOKEN")
if not CONFIG_TOKEN:
    print("ERROR: Set SLACK_CONFIG_TOKEN environment variable")
    print("  Generate one at: https://api.slack.com/apps → Your App Configuration Tokens")
    sys.exit(1)

APP_ID = os.environ.get("SLACK_APP_ID", "A0ABC0ZPQEM")

MANIFEST = {
    "display_information": {
        "name": "Popping",
        "description": "pop agent is always popping",
        "background_color": "#294eb3"
    },
    "features": {
        "app_home": {
            "home_tab_enabled": False,
            "messages_tab_enabled": True,
            "messages_tab_read_only_enabled": False
        },
        "bot_user": {
            "display_name": "popping",
            "always_online": True
        },
        "slash_commands": [
            {
                "command": "/clawd",
                "description": "Send a message to Clawdbot",
                "should_escape": False
            }
        ]
    },
    "oauth_config": {
        "scopes": {
            "bot": [
                "app_mentions:read",
                "channels:history",
                "channels:read",
                "chat:write",
                "chat:write.customize",
                "commands",
                "files:read",
                "files:write",
                "groups:history",
                "groups:read",
                "groups:write",
                "im:history",
                "im:read",
                "im:write",
                "mpim:history",
                "mpim:read",
                "mpim:write",
                "pins:read",
                "pins:write",
                "reactions:read",
                "reactions:write",
                "users:read"
            ]
        }
    },
    "settings": {
        "event_subscriptions": {
            "bot_events": [
                "app_mention",
                "channel_rename",
                "member_joined_channel",
                "member_left_channel",
                "message.channels",
                "message.groups",
                "message.im",
                "message.mpim",
                "pin_added",
                "pin_removed",
                "reaction_added",
                "reaction_removed"
            ]
        },
        "interactivity": {
            "is_enabled": True
        },
        "org_deploy_enabled": False,
        "socket_mode_enabled": True,
        "token_rotation_enabled": False
    }
}

payload = json.dumps({"app_id": APP_ID, "manifest": MANIFEST}).encode("utf-8")

req = urllib.request.Request(
    "https://slack.com/api/apps.manifest.update",
    data=payload,
    headers={
        "Authorization": f"Bearer {CONFIG_TOKEN}",
        "Content-Type": "application/json; charset=utf-8",
    },
    method="POST",
)

with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read().decode())

if result.get("ok"):
    print("Manifest updated successfully!")
    print(f"App ID: {APP_ID}")
    print(f"\nScopes added:")
    added = ["chat:write.customize", "files:read", "files:write", "pins:write", "reactions:write"]
    for s in added:
        print(f"  + {s}")
    print(f"\nEvents (already configured, preserved):")
    for e in MANIFEST["settings"]["event_subscriptions"]["bot_events"]:
        print(f"  - {e}")
    print(f"\nApp Home messages tab: enabled")
    print(f"\nIMPORTANT: Reinstall the app in your workspace to activate new scopes.")
    print(f"  Go to: https://api.slack.com/apps/{APP_ID}/install-on-team")
else:
    print(f"ERROR: {result.get('error')}")
    if result.get("errors"):
        for err in result["errors"]:
            print(f"  - {err.get('message')} (at {err.get('pointer')})")
    print(json.dumps(result, indent=2))
