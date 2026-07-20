from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime

import numpy as np

import config


@dataclass
class ApiCheckResult:
    status_code: int
    response_time_ms: float
    failure_reason: str | None
    region: str | None
    incident_severity: str | None


def _pick_region(row: dict) -> str | None:
    # Dataset uses server_region
    for key in ("server_region", "ServerRegion", "Region", "region", "Location", "location"):
        if key in row and row[key] and str(row[key]).strip():
            return str(row[key]).strip()
    return None



def _pick_api_name(row: dict) -> str | None:
    for key in ("api_name", "ApiName", "APIName", "Api", "Service"):
        if key in row and row[key] and str(row[key]).strip():
            return str(row[key]).strip()
    return None



def _pick_endpoint(row: dict) -> str | None:
    for key in ("endpoint", "EndpointURL", "Endpoint", "endpoint_url"):
        if key in row and row[key] and str(row[key]).strip():
            return str(row[key]).strip()
    return None



def check_from_dataset_row(row: dict) -> dict:
    """
    Simulate an API check using dataset row hints.
    Dataset columns vary; we use best-effort picks.
    """
    base_rt = None
    # Dataset uses snake_case (response_time_ms)
    for key in ("response_time_ms", "ResponseTime", "Response Time", "LatencyMs", "ResponseTimeMs"):
        if key in row and row[key] is not None:
            try:
                base_rt = float(row[key])
                break
            except Exception:
                pass


    # Determine status code from dataset-provided status if available; else random distribution
    # Dataset uses status_code
    dataset_status = None
    for key in ("status_code", "StatusCode", "Status", "http_status"):
        if key in row and row[key] is not None:
            try:
                dataset_status = int(float(row[key]))
                break
            except Exception:
                pass

    # If dataset provides status_code, never randomize
    status_code = int(dataset_status) if dataset_status is not None else 200

    region = _pick_region(row)

    # If dataset provides response time, never randomize
    response_time_ms = float(base_rt) if base_rt is not None else 0.0
    response_time_ms = max(0.0, response_time_ms)


    failure_reason = None
    for key in ("failure_reason", "FailureReason"):
        if key in row and row[key]:
            failure_reason = str(row[key])
            break

    # If dataset doesn't provide failure_reason, derive minimal fallback
    if not failure_reason:
        if status_code >= 500:
            failure_reason = "Server error"
        elif status_code == 404:
            failure_reason = "Endpoint not found"

    # Dataset provides incident_severity (e.g., High/Critical)
    incident_severity = None
    for key in ("incident_severity", "IncidentSeverity"):
        if key in row and row[key]:
            incident_severity = str(row[key]).lower()
            break

    # Normalize dataset severities into critical/high for alerts/UX
    if incident_severity:
        if incident_severity in ("critical", "high"):
            pass
        else:
            # map medium/low/other
            if incident_severity in ("medium", "med"):
                incident_severity = "high"
            else:
                incident_severity = "low"
    else:
        # Derive only if dataset missing
        if status_code >= config.STATUS_CODE_CRITICAL:
            incident_severity = "critical"
        elif response_time_ms > config.RESPONSE_TIME_HIGH_MS:
            incident_severity = "high"


    return {
        "status_code": status_code,
        "response_time_ms": response_time_ms,
        "failure_reason": failure_reason,
        "region": region,
        "incident_severity": incident_severity,
    }


def load_dataset() -> list[dict]:
    """
    Loads dataset CSV into list[dict]. If dataset missing, returns [].
    """
    import os
    import pandas as pd

    if not os.path.exists(config.DATASET_PATH):
        return []

    df = pd.read_csv(config.DATASET_PATH)
    # Replace NaNs with None for easier logic
    df = df.where(df.notnull(), None)
    return df.to_dict(orient="records")
