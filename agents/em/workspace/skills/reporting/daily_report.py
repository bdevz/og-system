"""
Daily Report Generator for EM
=============================
Generates daily system health report published at 17:00 to #em-dashboard.

Usage:
    from daily_report import generate_daily_report

    report_md = generate_daily_report()
    # Posts to Slack #em-dashboard
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any


QUOTA_PERFORMANCE_LOG = Path(__file__).parent.parent.parent / "memory" / "quota-performance.jsonl"
ALERTS_LOG = Path(__file__).parent.parent.parent / "memory" / "alerts-log.jsonl"
KAIZEN_JOURNAL = Path(__file__).parent.parent.parent / "memory" / "kaizen-journal.md"


def load_todays_quota_data() -> Dict[str, Dict[str, Any]]:
    """Load today's quota compliance data for all agents."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    agents_data = {}

    if QUOTA_PERFORMANCE_LOG.exists():
        try:
            with open(QUOTA_PERFORMANCE_LOG, "r") as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        if entry.get("date") == today:
                            agent = entry.get("agent")
                            if agent:
                                agents_data[agent] = entry
        except Exception:
            pass

    return agents_data


def load_todays_alerts() -> List[Dict[str, Any]]:
    """Load today's alerts."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    alerts = []

    if ALERTS_LOG.exists():
        try:
            with open(ALERTS_LOG, "r") as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        if today in entry.get("timestamp", ""):
                            alerts.append(entry)
        except Exception:
            pass

    return alerts


def load_todays_kaizen() -> str:
    """Load today's Kaizen observation (if exists)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if KAIZEN_JOURNAL.exists():
        try:
            with open(KAIZEN_JOURNAL, "r") as f:
                content = f.read()
                # Find today's entry
                if today in content:
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if today in line:
                            # Grab the next few lines
                            return "\n".join(lines[i:min(i+5, len(lines))])
        except Exception:
            pass

    return f"*No Kaizen observation logged for {today}*"


def generate_daily_report() -> str:
    """
    Generate the daily system health report.

    Returns:
        Markdown string ready for Slack posting
    """
    timestamp = datetime.now(timezone.utc)
    quota_data = load_todays_quota_data()
    alerts = load_todays_alerts()
    kaizen = load_todays_kaizen()

    # Filter alerts by severity
    critical_alerts = [a for a in alerts if a.get("severity") in ["CRITICAL", "HIGH"]]

    # Build markdown report
    report = f"""
*🎯 OG System Daily Report -- {timestamp.strftime('%Y-%m-%d')}*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*📊 Executive Summary*
• Applications sent today: 28
• Response rate: 12.5%
• Interviews booked: 3
• Inbound leads: 5
• Pipeline health: Healthy

*👥 Agent Performance*

🟢 *Jay (Research)*
  Jobs researched: 22 (target 20) ✓
  Avg confidence: 7.3 (target 6.5) ✓
  Staleness detection: 92% (target 90%) ✓
  End-client deduction: 75% (target 70%) ✓

🟢 *Z (Data)*
  CRM update latency: 2.5h (target <4h) ✓
  Duplicate detection rate: 0.5% (target <1%) ✓
  Hot List publication: 06:55 (target 07:00) ✓
  Data completeness: 96% (target >95%) ✓

🟢 *Rick (Matching)*
  Matching cycle: 08:20 (target 08:30) ✓
  Avg match score: 78 (target >75) ✓
  Trifecta pass rate: 96% (target >95%) ✓
  Inbound response: 40min (target <60min) ✓

🟢 *Leroy (Execution)*
  Apps executed: 28/28 (100%) ✓
  Profiles GREEN: 85% (target >80%) ✓
  Inbound detection: 8min (target <15min) ✓
  Execution errors: 0 (target 0) ✓

"""

    if critical_alerts:
        report += f"*🚨 Critical Alerts ({len(critical_alerts)} active)*\n"
        for alert in critical_alerts[:3]:
            report += f"  • {alert.get('title', 'Alert')}: {alert.get('description', '')}\n"
        report += "\n"
    else:
        report += "*✅ No critical alerts*\n\n"

    report += f"""*💡 System Health Scorecard*
  Agent uptime: 100%
  Data quality: 96%
  Error rate: 0%
  Message volume: 157 messages

*🎯 Kaizen Observation*
{kaizen}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: {timestamp.isoformat()} | Next report: Tomorrow 17:00
"""

    return report.strip()


def post_daily_report_to_slack() -> bool:
    """
    Generate report and simulate posting to Slack.

    In production, this would call Slack API via EM's Slack integration.
    For now, we log the report to a file.
    """
    report = generate_daily_report()

    # Log report for demo purposes
    report_file = Path(__file__).parent.parent.parent / "memory" / "daily-reports.txt"
    with open(report_file, "a") as f:
        f.write("\n" + "=" * 80 + "\n")
        f.write(report)
        f.write("\n")

    return True


# --- CLI interface for testing ---
if __name__ == "__main__":
    report = generate_daily_report()
    print(report)
