from __future__ import annotations

from typing import Optional

from database.db_connection import execute, query_all, query_one


def insert_log(
    api_id: int,
    timestamp: str,
    status_code: int,
    response_time: float,
    failure_reason: Optional[str],
    region: Optional[str],
    incident_severity: Optional[str],
) -> None:
    execute(
        """
        INSERT INTO MonitoringLogs
        (ApiID, Timestamp, StatusCode, ResponseTime, FailureReason, Region, IncidentSeverity)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (api_id, timestamp, status_code, response_time, failure_reason, region, incident_severity),
    )


def get_logs(
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
    status_code: Optional[int] = None,
    region: Optional[str] = None,
) -> dict:
    offset = (page - 1) * page_size

    where = []
    params: list = []

    if search:
        where.append("(a.ApiName LIKE ? OR m.FailureReason LIKE ? OR m.Region LIKE ?)")
        like = f"%{search}%"
        params.extend([like, like, like])

    if status_code is not None:
        where.append("m.StatusCode = ?")
        params.append(int(status_code))

    if region:
        where.append("m.Region = ?")
        params.append(region)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    # Total
    total_row = query_one(
        f"""
        SELECT COUNT(1) AS total
        FROM MonitoringLogs m
        JOIN APIs a ON a.ApiID = m.ApiID
        {where_sql}
        """,
        tuple(params),
    )
    total = int(total_row["total"]) if total_row else 0

    rows = query_all(
        f"""
        SELECT
            m.LogID,
            m.Timestamp,
            a.ApiName,
            a.EndpointURL,
            m.StatusCode,
            m.ResponseTime,
            m.FailureReason,
            m.Region,
            m.IncidentSeverity
        FROM MonitoringLogs m
        JOIN APIs a ON a.ApiID = m.ApiID
        {where_sql}
        ORDER BY m.Timestamp DESC
        LIMIT ? OFFSET ?
        """,
        tuple(params) + (page_size, offset),
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "rows": [dict(r) for r in rows],
    }


def get_latest_logs_per_api(limit_per_api: int = 50) -> list[dict]:
    # Used for uptime/downtime computation
    rows = query_all(
        f"""
        SELECT
            m.LogID,
            m.ApiID,
            m.Timestamp,
            m.StatusCode,
            m.ResponseTime,
            m.FailureReason,
            m.Region,
            m.IncidentSeverity
        FROM MonitoringLogs m
        ORDER BY m.Timestamp DESC
        LIMIT ?
        """,
        (limit_per_api,),
    )
    return [dict(r) for r in rows]
