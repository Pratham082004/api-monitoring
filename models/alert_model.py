from __future__ import annotations

from database.db_connection import execute, query_all


def insert_alert(api_id: int, alert_type: str, alert_message: str, alert_time: str | None = None) -> None:
    if alert_time:
        execute(
            """
            INSERT INTO Alerts (ApiID, AlertType, AlertMessage, AlertTime)
            VALUES (?, ?, ?, ?)
            """,
            (api_id, alert_type, alert_message, alert_time),
        )
    else:
        execute(
            """
            INSERT INTO Alerts (ApiID, AlertType, AlertMessage)
            VALUES (?, ?, ?)
            """,
            (api_id, alert_type, alert_message),
        )


def list_alerts(limit: int = 100) -> list[dict]:
    rows = query_all(
        """
        SELECT
            AlertID,
            a.ApiName,
            a.EndpointURL,
            AlertType,
            AlertMessage,
            AlertTime
        FROM Alerts
        JOIN APIs a ON a.ApiID = Alerts.ApiID
        ORDER BY AlertTime DESC
        LIMIT ?
        """,
        (limit,),
    )
    return [dict(r) for r in rows]
