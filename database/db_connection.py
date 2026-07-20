import os
import sqlite3

import config


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    if not os.path.exists(config.SCHEMA_PATH):
        raise FileNotFoundError(f"Missing schema file: {config.SCHEMA_PATH}")

    with get_connection() as conn:
        with open(config.SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()


def execute(query: str, params: tuple = ()) -> None:
    with get_connection() as conn:
        conn.execute(query, params)
        conn.commit()


def query_all(query: str, params: tuple = ()) -> list[sqlite3.Row]:
    with get_connection() as conn:
        cur = conn.execute(query, params)
        return cur.fetchall()


def query_one(query: str, params: tuple = ()) -> sqlite3.Row | None:
    with get_connection() as conn:
        cur = conn.execute(query, params)
        return cur.fetchone()
