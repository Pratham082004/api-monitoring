from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from models.monitoring_log import get_logs
from models.alert_model import list_alerts

bp_monitor = Blueprint("monitor", __name__)
bp_alerts = Blueprint("alerts", __name__)


@bp_monitor.route("/logs", methods=["GET"])
def logs_page():
    return render_template("monitoring_logs.html")


@bp_monitor.route("/logs/data", methods=["GET"])
def logs_data():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("pageSize", 10))
    search = request.args.get("search") or None

    status_code = request.args.get("statusCode")
    status_code_int = int(status_code) if status_code not in (None, "", "null") else None

    region = request.args.get("region") or None

    data = get_logs(page=page, page_size=page_size, search=search, status_code=status_code_int, region=region)
    return jsonify(data)


# Alerts data endpoint
@bp_alerts.route("/data", methods=["GET"])
def alerts_data():
    limit = int(request.args.get("limit", 100))
    return jsonify({"rows": list_alerts(limit=limit)})
