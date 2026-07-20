from __future__ import annotations

from typing import Any

from database.db_connection import execute, query_all, query_one


def create_api(api_name: str, endpoint_url: str, status: str = "active") -> int:
    row = query_one(
        "INSERT INTO APIs (ApiName, EndpointURL, Status) VALUES (?, ?, ?) RETURNING ApiID",
        (api_name, endpoint_url, status),
    )
    # SQLite RETURNING supported in modern versions; fallback:
    if row and "ApiID" in row.keys():
        return int(row["ApiID"])

    # Fallback for older SQLite:
    execute("INSERT INTO APIs (ApiName, EndpointURL, Status) VALUES (?, ?, ?)", (api_name, endpoint_url, status))
    # Re-fetch last insert id
    last = query_one("SELECT last_insert_rowid() AS id")
    return int(last["id"])


def update_api(api_id: int, api_name: str, endpoint_url: str, status: str) -> None:
    execute(
        "UPDATE APIs SET ApiName = ?, EndpointURL = ?, Status = ? WHERE ApiID = ?",
        (api_name, endpoint_url, status, api_id),
    )


def delete_api(api_id: int) -> None:
    execute("DELETE FROM APIs WHERE ApiID = ?", (api_id,))


def list_apis() -> list[dict[str, Any]]:
    rows = query_all("SELECT ApiID, ApiName, EndpointURL, Status, CreatedAt FROM APIs ORDER BY ApiID DESC")
    return [dict(r) for r in rows]


def get_api(api_id: int) -> dict[str, Any] | None:
    row = query_one(
        "SELECT ApiID, ApiName, EndpointURL, Status, CreatedAt FROM APIs WHERE ApiID = ?",
        (api_id,),
    )
    return dict(row) if row else None


def get_active_apis() -> list[dict[str, Any]]:
    rows = query_all(
        "SELECT ApiID, ApiName, EndpointURL, Status, CreatedAt FROM APIs WHERE Status = 'active' ORDER BY ApiID ASC"
    )
    return [dict(r) for r in rows]
