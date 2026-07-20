from __future__ import annotations

import csv
import os
from datetime import datetime, timezone
from typing import Any

import pandas as pd

import config
from database.db_connection import query_all


def _ensure_reports_dir() -> None:
    os.makedirs(config.REPORTS_DIR, exist_ok=True)


def _top_failure_reasons(limit: int = 5) -> list[dict[str, Any]]:
    rows = query_all(
        """
        SELECT FailureReason, COUNT(1) AS c
        FROM MonitoringLogs
        WHERE FailureReason IS NOT NULL AND FailureReason != ''
        GROUP BY FailureReason
        ORDER BY c DESC
        LIMIT ?
        """,
        (limit,),
    )
    return [{"reason": r["FailureReason"], "count": r["c"]} for r in rows]


def _overall_stats(start_ts: str, end_ts: str) -> dict[str, Any]:
    rows = query_all(
        """
        SELECT
            COUNT(1) AS totalRequests,
            SUM(CASE WHEN StatusCode >= 500 THEN 1 ELSE 0 END) AS totalFailures,
            AVG(ResponseTime) AS avgResponseTimeMs,
            AVG(CASE WHEN StatusCode < 500 THEN 1.0 ELSE 0.0 END) * 100.0 AS uptimePct
        FROM MonitoringLogs
        WHERE Timestamp >= ? AND Timestamp < ? 
        """,
        (start_ts, end_ts),
    )
    r = rows[0] if rows else None
    if not r:
        return {
            "totalRequests": 0,
            "totalFailures": 0,
            "avgResponseTimeMs": 0,
            "uptimePct": 100,
        }
    return {
        "totalRequests": int(r["totalRequests"]),
        "totalFailures": int(r["totalFailures"]),
        "avgResponseTimeMs": float(r["avgResponseTimeMs"] or 0),
        "uptimePct": float(r["uptimePct"] or 0),
    }


def generate_daily_report(now: datetime | None = None) -> None:
    _ensure_reports_dir()
    now = now or datetime.now(timezone.utc)

    start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    end = start + pd.Timedelta(days=1)
    start_ts = start.isoformat()
    end_ts = end.isoformat()

    stats = _overall_stats(start_ts, end_ts)
    top_reasons = _top_failure_reasons(limit=5)

    out_rows = [
        {
            "date": start.date().isoformat(),
            **stats,
            "topFailureReason1": top_reasons[0]["reason"] if len(top_reasons) > 0 else "",
            "topFailureCount1": top_reasons[0]["count"] if len(top_reasons) > 0 else 0,
            "topFailureReason2": top_reasons[1]["reason"] if len(top_reasons) > 1 else "",
            "topFailureCount2": top_reasons[1]["count"] if len(top_reasons) > 1 else 0,
            "topFailureReason3": top_reasons[2]["reason"] if len(top_reasons) > 2 else "",
            "topFailureCount3": top_reasons[2]["count"] if len(top_reasons) > 2 else 0,
            "topFailureReason4": top_reasons[3]["reason"] if len(top_reasons) > 3 else "",
            "topFailureCount4": top_reasons[3]["count"] if len(top_reasons) > 3 else 0,
            "topFailureReason5": top_reasons[4]["reason"] if len(top_reasons) > 4 else "",
            "topFailureCount5": top_reasons[4]["count"] if len(top_reasons) > 4 else 0,
        }
    ]

    # Overwrite latest file each run
    pd.DataFrame(out_rows).to_csv(config.DAILY_REPORT_PATH, index=False)


def generate_monthly_report(now: datetime | None = None) -> None:
    _ensure_reports_dir()
    now = now or datetime.now(timezone.utc)

    start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    # first day of next month
    if now.month == 12:
        end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)

    start_ts = start.isoformat()
    end_ts = end.isoformat()

    stats = _overall_stats(start_ts, end_ts)
    top_reasons = _top_failure_reasons(limit=5)

    out_rows = [
        {
            "month": start.strftime("%Y-%m"),
            **stats,
            "topFailureReason1": top_reasons[0]["reason"] if len(top_reasons) > 0 else "",
            "topFailureCount1": top_reasons[0]["count"] if len(top_reasons) > 0 else 0,
            "topFailureReason2": top_reasons[1]["reason"] if len(top_reasons) > 1 else "",
            "topFailureCount2": top_reasons[1]["count"] if len(top_reasons) > 1 else 0,
            "topFailureReason3": top_reasons[2]["reason"] if len(top_reasons) > 2 else "",
            "topFailureCount3": top_reasons[2]["count"] if len(top_reasons) > 2 else 0,
            "topFailureReason4": top_reasons[3]["reason"] if len(top_reasons) > 3 else "",
            "topFailureCount4": top_reasons[3]["count"] if len(top_reasons) > 3 else 0,
            "topFailureReason5": top_reasons[4]["reason"] if len(top_reasons) > 4 else "",
            "topFailureCount5": top_reasons[4]["count"] if len(top_reasons) > 4 else 0,
        }
    ]

    pd.DataFrame(out_rows).to_csv(config.MONTHLY_REPORT_PATH, index=False)
