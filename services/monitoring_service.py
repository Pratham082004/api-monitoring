from __future__ import annotations

from datetime import datetime
from typing import Any

from models.api_model import get_active_apis, create_api
from models.monitoring_log import insert_log
from services.api_checker import load_dataset, check_from_dataset_row
from services.alert_service import evaluate_and_create_alerts


def ensure_apis_from_dataset(dataset_rows: list[dict[str, Any]]) -> None:
    """
    If APIs table is empty, seed it from dataset rows (best-effort mapping).
    """
    if not dataset_rows:
        return

    active = get_active_apis()
    if active:
        return

    for row in dataset_rows:
        api_name = row.get("ApiName") or row.get("api_name") or "API"
        endpoint = row.get("EndpointURL") or row.get("endpoint_url") or "/"
        status = "active"
        try:
            create_api(str(api_name), str(endpoint), status)
        except Exception:
            # ignore duplicates / insert errors
            pass


def run_monitoring_cycle() -> dict:
    dataset_rows = load_dataset()
    ensure_apis_from_dataset(dataset_rows)

    apis = get_active_apis()
    if not apis:
        return {"ok": True, "message": "No active APIs. Add APIs or add dataset to seed."}

    # If dataset exists, we’ll cycle through dataset rows per API, else use random checker.
    for idx, api in enumerate(apis):
        row = dataset_rows[idx % len(dataset_rows)] if dataset_rows else {"StatusCode": None}
        check = check_from_dataset_row(row)

        timestamp = datetime.utcnow().isoformat()
        insert_log(
            api_id=int(api["ApiID"]),
            timestamp=timestamp,
            status_code=int(check["status_code"]),
            response_time=float(check["response_time_ms"]),
            failure_reason=check.get("failure_reason"),
            region=check.get("region"),
            incident_severity=check.get("incident_severity"),
        )

        evaluate_and_create_alerts(
            dataset_title="api_monitoring_rich_dataset",
            api_id=int(api["ApiID"]),
            api_name=api.get("ApiName"),
            status_code=int(check["status_code"]),
            response_time=float(check["response_time_ms"]),
            failure_reason=check.get("failure_reason"),
            region=check.get("region"),
        )


    return {"ok": True, "message": f"Monitoring cycle completed for {len(apis)} APIs."}
