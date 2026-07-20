from __future__ import annotations

from datetime import datetime, timedelta

import config
from models.alert_model import insert_alert
from models.monitoring_log import get_latest_logs_per_api
from services.email_service import send_email


def compute_downtime_critical_minutes(latest_logs: list[dict]) -> bool:
    """
    Downtime computation heuristic:
    - Consider "downtime" when latest status codes are >= 500 or when FailureReason exists.
    - If downtime episodes reach threshold -> critical.
    """
    if not latest_logs:
        return False

    # Group by ApiID and estimate last failures duration based on timestamps order.
    latest_logs_sorted = sorted(latest_logs, key=lambda x: x["Timestamp"], reverse=True)

    api_last_failure_time: dict[int, datetime] = {}
    now = datetime.utcnow()

    for row in latest_logs_sorted:
        api_id = int(row["ApiID"])
        ts_raw = row["Timestamp"]
        # SQLite datetime('now') stored as ISO-ish; use fallback parsing
        try:
            ts = datetime.fromisoformat(ts_raw)
        except ValueError:
            ts = now

        status_code = int(row["StatusCode"])
        failure = bool(row.get("FailureReason"))
        if status_code >= 500 or failure:
            if api_id not in api_last_failure_time:
                api_last_failure_time[api_id] = ts

    # Compute "how long since first failure in the recent window"
    for api_id, first_failure_ts in api_last_failure_time.items():
        minutes = (now - first_failure_ts).total_seconds() / 60.0
        if minutes > config.DOWNTIME_CRITICAL_MINUTES:
            return True

    return False


def evaluate_and_create_alerts(dataset_title: str, api_id: int, api_name: str | None, status_code: int, response_time: float,
                                 failure_reason: str | None, region: str | None) -> list[dict]:
    """
    Creates alerts based on rules:
    - StatusCode >= 500 => critical/high (use 'critical' if >= 600 else 'high')
    - ResponseTime > 3000ms => high
    - Downtime > 30 minutes => critical (computed from latest logs window)
    """
    alerts: list[dict] = []

    # Rule 1: server errors
    if status_code >= config.STATUS_CODE_CRITICAL:
        severity = "critical" if status_code >= 600 else "high"
        alert_type = "SERVER_ERROR"
        message = f"{alert_type}: {status_code} on {api_name or 'API'} ({region or 'unknown'}) - {failure_reason or 'no reason'}"
        insert_alert(api_id, alert_type, f"{severity.upper()} - {message}")
        alerts.append({"type": alert_type, "severity": severity, "message": message})

    # Rule 2: slow responses
    if response_time > config.RESPONSE_TIME_HIGH_MS:
        alert_type = "HIGH_RESPONSE_TIME"
        severity = "high"
        message = f"{alert_type}: {response_time:.0f}ms on {api_name or 'API'} ({region or 'unknown'})"
        insert_alert(api_id, alert_type, f"{severity.upper()} - {message}")
        alerts.append({"type": alert_type, "severity": severity, "message": message})

    # Rule 3: downtime (global critical check)
    latest = get_latest_logs_per_api(limit_per_api := 200)
    if compute_downtime_critical_minutes(latest):
        alert_type = "DOWNTIME"
        severity = "critical"
        message = f"{alert_type}: downtime over {config.DOWNTIME_CRITICAL_MINUTES} minutes detected."
        # Create a single downtime alert per evaluation using the api_id passed
        insert_alert(api_id, alert_type, f"{severity.upper()} - {message}")
        alerts.append({"type": alert_type, "severity": severity, "message": message})

    # Optional SMTP dispatch for critical/high
    for a in alerts:
        if a["severity"] in ("critical", "high") and config.SMTP_ENABLED:
            subject = f"[API Monitoring] {a['severity'].upper()} alert - {a['type']}"
            body = a["message"]
            try:
                send_email(subject, body, config.ALERT_EMAIL_TO)
            except Exception:
                # Don't break monitoring cycle if email fails
                pass

    return alerts
