"""
Dashboard Formatter for EM
==========================
Formats system data into Slack-friendly markdown with visual indicators.

Usage:
    from dashboard_formatter import format_agent_status_bar, format_metric_scorecard

    status_bar = format_agent_status_bar("Z", "ACTIVE", 10)  # Last activity 10 min ago
    print(status_bar)  # "🟢 Z: ACTIVE (10 min)"
"""


def format_agent_status(agent_id: str, state: str, time_since_activity_minutes: int) -> str:
    """
    Format agent status with emoji and color.

    Args:
        agent_id: "Z", "Jay", "Rick", "Leroy"
        state: "ACTIVE", "IDLE", "BUSY", "SLOW", "ERROR", "DEAD"
        time_since_activity_minutes: Minutes since last activity

    Returns:
        Formatted status string for Slack
    """
    state_emoji = {
        "ACTIVE": "🟢",
        "IDLE": "🟡",
        "BUSY": "🟠",
        "SLOW": "🟠",
        "ERROR": "🔴",
        "DEAD": "⚫",
    }

    emoji = state_emoji.get(state, "❓")
    status = f"{emoji} {agent_id}: {state} ({time_since_activity_minutes} min)"

    return status


def format_metric_status(metric_name: str, actual: float, target: float, unit: str = "") -> str:
    """
    Format a single metric with status indicator.

    Args:
        metric_name: Name of the metric
        actual: Actual value
        target: Target value
        unit: Unit of measurement

    Returns:
        Formatted metric string for Slack
    """
    if actual is None:
        return f"⚪ {metric_name}: NO DATA"

    # Determine status (higher is better by default)
    if "latency" in metric_name or "error" in metric_name:
        # For latency/errors, lower is better
        if actual <= target:
            status = "✓"
            emoji = "🟢"
        else:
            status = "⚠️"
            emoji = "🟡"
    else:
        # For most metrics, higher is better
        if actual >= target:
            status = "✓"
            emoji = "🟢"
        else:
            status = "⚠️"
            emoji = "🟡" if actual >= target * 0.95 else "🔴"

    return f"{emoji} {metric_name}: {actual} {unit} (target: {target}) {status}"


def format_alert_summary(alert_dict: dict) -> str:
    """
    Format a single alert for Slack.

    Args:
        alert_dict: Alert with severity, title, description

    Returns:
        Formatted alert string for Slack
    """
    severity = alert_dict.get("severity", "MEDIUM")
    severity_emoji = {
        "CRITICAL": "🚨",
        "HIGH": "⚠️",
        "MEDIUM": "⚡",
        "LOW": "ℹ️",
    }

    emoji = severity_emoji.get(severity, "📢")
    title = alert_dict.get("title", "Alert")
    description = alert_dict.get("description", "")
    action = alert_dict.get("recommended_action", "")

    formatted = f"{emoji} *{title}*\n  {description}"
    if action:
        formatted += f"\n  _Action: {action}_"

    return formatted


def format_agent_dashboard(agents_status: dict) -> str:
    """
    Format system dashboard with all agent statuses.

    Args:
        agents_status: Dict like {"Z": {"state": "ACTIVE", "time_since": 10}, ...}

    Returns:
        Formatted dashboard string for Slack
    """
    dashboard = "*👥 Agent Status Dashboard*\n"

    for agent_id in ["Z", "Jay", "Rick", "Leroy"]:
        if agent_id in agents_status:
            status = agents_status[agent_id]
            state = status.get("state", "UNKNOWN")
            time_since = status.get("time_since_activity_minutes", 0)
            dashboard += f"  {format_agent_status(agent_id, state, time_since)}\n"

    return dashboard


def format_pipeline_snapshot(stats: dict) -> str:
    """
    Format pipeline numbers snapshot.

    Args:
        stats: Dict with counts like {"researched": 154, "submitted": 135, ...}

    Returns:
        Formatted pipeline string for Slack
    """
    pipeline = "*📊 Pipeline Snapshot*\n"
    pipeline += f"  📋 Researched: {stats.get('researched', 0)}\n"
    pipeline += f"  ✅ Submitted: {stats.get('submitted', 0)}\n"
    pipeline += f"  💬 Responded: {stats.get('responded', 0)}\n"
    pipeline += f"  🎯 Interviewing: {stats.get('interviewing', 0)}\n"
    pipeline += f"  🎉 Offers: {stats.get('offers', 0)}\n"

    return pipeline


def format_health_scorecard(metrics: dict) -> str:
    """
    Format system health scorecard.

    Args:
        metrics: Dict with metrics like {"uptime": 99.5, "data_quality": 96, ...}

    Returns:
        Formatted scorecard string for Slack
    """
    scorecard = "*💡 System Health*\n"
    scorecard += f"  ✅ Uptime: {metrics.get('uptime', 0)}% (target >95%)\n"
    scorecard += f"  ✅ Data Quality: {metrics.get('data_quality', 0)}% (target >95%)\n"
    scorecard += f"  ✅ Error Rate: {metrics.get('error_rate', 0)}% (target <1%)\n"
    scorecard += f"  ✅ Avg Processing Time: {metrics.get('avg_processing_time', 0)}min\n"

    return scorecard


# --- CLI interface for testing ---
if __name__ == "__main__":
    # Demo formatting
    print(format_agent_status("Z", "ACTIVE", 5))
    print(format_agent_status("Jay", "BUSY", 45))
    print(format_agent_status("Rick", "SLOW", 95))
    print(format_agent_status("Leroy", "ERROR", 120))

    print("\n" + "=" * 40 + "\n")

    print(format_metric_status("jobs_researched", 22, 20, "jobs/day"))
    print(format_metric_status("crm_latency", 2.5, 4, "hours"))
    print(format_metric_status("match_score", 72, 75, ""))

    print("\n" + "=" * 40 + "\n")

    agents = {
        "Z": {"state": "ACTIVE", "time_since_activity_minutes": 5},
        "Jay": {"state": "BUSY", "time_since_activity_minutes": 35},
        "Rick": {"state": "ACTIVE", "time_since_activity_minutes": 8},
        "Leroy": {"state": "IDLE", "time_since_activity_minutes": 42},
    }

    print(format_agent_dashboard(agents))

    print("\n" + "=" * 40 + "\n")

    stats = {
        "researched": 154,
        "submitted": 135,
        "responded": 18,
        "interviewing": 6,
        "offers": 1,
    }

    print(format_pipeline_snapshot(stats))

    print("\n" + "=" * 40 + "\n")

    metrics = {
        "uptime": 100,
        "data_quality": 96,
        "error_rate": 0,
        "avg_processing_time": 120,
    }

    print(format_health_scorecard(metrics))
