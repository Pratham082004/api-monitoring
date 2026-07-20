from __future__ import annotations

from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, jsonify

from database.db_connection import query_all, query_one
from models.api_model import get_active_apis
from models.monitoring_log import get_latest_logs_per_api
from models.alert_model import list_alerts
import config

bp_dashboard = Blueprint("dashboard", __name__)
bp_api = Blueprint("api", __name__)
bp_monitor = Blueprint("monitor", __name__)
bp_alerts = Blueprint("alerts", __name__)
bp_reports = Blueprint("reports", __name__)


def _calc_uptime_percentage(latest_logs: list[dict]) -> float:
    # uptime heuristic: % of status_code < 500 over recent window
    if not latest_logs:
        return 100.0
    ok = 0
    for r in latest_logs:
        if int(r.get("StatusCode", r.get("status_code", 0))) < 500:
            ok += 1
    return (ok / len(latest_logs)) * 100.0


@bp_dashboard.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html")


@bp_dashboard.route("/api/metrics", methods=["GET"])
def dashboard_metrics():
    latest = get_latest_logs_per_api(limit_per_api=50)

    apis = get_active_apis()
    total_apis = len(apis)

    failed_apis = 0
    critical_incidents = 0

    # Determine per-api last incident severity
    by_api: dict[int, dict] = {}
    for r in latest:
        api_id = int(r["ApiID"])
        cur = by_api.get(api_id)
        # keep newest by Timestamp (string ISO-ish)
        if not cur or str(r["Timestamp"]) > str(cur["Timestamp"]):
            by_api[api_id] = r

    for api_id, r in by_api.items():
        status_code = int(r["StatusCode"])
        rt = float(r["ResponseTime"])
        severity = r.get("IncidentSeverity")
        if status_code >= 500 or r.get("FailureReason"):
            failed_apis += 1
        if severity == "critical" or status_code >= 600:
            critical_incidents += 1

    healthy_apis = max(0, total_apis - failed_apis)

    avg_response = sum(float(r["ResponseTime"]) for r in latest) / len(latest) if latest else 0.0
    uptime = _calc_uptime_percentage(latest)

    # Status code distribution
    status_dist: dict[str, int] = {}
    for r in latest:
        sc = int(r["StatusCode"])
        cls = f"{sc // 100}xx" if sc >= 100 else str(sc)
        status_dist[cls] = status_dist.get(cls, 0) + 1

    resp_trend_rows = query_all(
        """
        SELECT Timestamp, ResponseTime
        FROM MonitoringLogs
        ORDER BY Timestamp DESC
        LIMIT 30
        """,
    )
    resp_trend = [{"x": r["Timestamp"], "y": float(r["ResponseTime"])} for r in reversed(resp_trend_rows)]

    # Failure distribution by reason
    failure_dist: dict[str, int] = {}
    for r in latest:
        reason = r.get("FailureReason")
        if reason:
            failure_dist[reason] = failure_dist.get(reason, 0) + 1

    # Regional performance table (used by dashboard.js)
    region_rows = query_all(
        """
        SELECT
            Region,
            COUNT(1) AS total,
            AVG(ResponseTime) AS avgResponseTime,
            SUM(CASE WHEN StatusCode >= 500 THEN 1 ELSE 0 END) AS failures
        FROM MonitoringLogs
        GROUP BY Region
        ORDER BY total DESC
        LIMIT 10
        """
    )
    region_performance = [
        {"region": r["Region"] or "unknown", "total": r["total"], "avg": r["avgResponseTime"] or 0, "failures": r["failures"]}
        for r in region_rows
    ]

    return jsonify(
        {
            "kpis": {
                "totalApis": total_apis,
                "healthyApis": healthy_apis,
                "failedApis": failed_apis,
                "criticalIncidents": critical_incidents,
                "avgResponseTimeMs": avg_response,
                "uptimePct": uptime,
            },
            "regionPerformance": region_performance,
            "statusDistribution": status_dist,
            "responseTimeTrend": resp_trend,
            "failureDistribution": failure_dist,
        }
    )


@bp_dashboard.route("/api/region-performance", methods=["GET"])
def region_performance():
    rows = query_all(
        """
        SELECT
            Region,
            COUNT(1) AS total,
            AVG(ResponseTime) AS avgResponseTime,
            SUM(CASE WHEN StatusCode >= 500 THEN 1 ELSE 0 END) AS failures
        FROM MonitoringLogs
        GROUP BY Region
        ORDER BY total DESC
        LIMIT 10
        """
    )
    return jsonify([{"region": r["Region"] or "unknown", "total": r["total"], "avg": r["avgResponseTime"] or 0, "failures": r["failures"]} for r in rows])


@bp_dashboard.route("/api/downtime", methods=["GET"])
def downtime_analysis():
    # Simple downtime analysis: count of logs with status_code >= 500 per day (last 7 days)
    rows = query_all(
        """
        SELECT
            date(Timestamp) AS day,
            SUM(CASE WHEN StatusCode >= 500 THEN 1 ELSE 0 END) AS downtimeEvents
        FROM MonitoringLogs
        WHERE Timestamp >= datetime('now', '-7 days')
        GROUP BY day
        ORDER BY day ASC
        """
    )
    return jsonify([{"day": r["day"], "downtimeEvents": r["downtimeEvents"]} for r in rows])


# Alerts page
@bp_alerts.route("/", methods=["GET"])
def alerts_page():
    return render_template("alerts.html")


# Reports
@bp_reports.route("/", methods=["GET"])
def reports_page():
    daily = config.DAILY_REPORT_PATH
    monthly = config.MONTHLY_REPORT_PATH
    return render_template("reports.html", daily_exists=bool(daily), monthly_exists=bool(monthly))
