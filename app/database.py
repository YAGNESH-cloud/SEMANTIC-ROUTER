
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent.parent / "app.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH, timeout=30)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS cache_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                embedding TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_at REAL NOT NULL,
                expires_at REAL NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS request_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                cache_hit INTEGER NOT NULL DEFAULT 0,
                model_name TEXT NOT NULL,
                input_tokens INTEGER NOT NULL DEFAULT 0,
                output_tokens INTEGER NOT NULL DEFAULT 0,
                cost_usd REAL NOT NULL DEFAULT 0,
                latency_ms REAL NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'success',
                created_at REAL NOT NULL
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_cache_expires_at
            ON cache_entries(expires_at)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_cache_question_normalized
            ON cache_entries(lower(trim(question)))
        """)

        connection.commit()

def record_request(
    question,
    cache_hit,
    model_name,
    input_tokens,
    output_tokens,
    cost_usd,
    latency_ms,
    status="success"
):
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO request_metrics (
                question,
                cache_hit,
                model_name,
                input_tokens,
                output_tokens,
                cost_usd,
                latency_ms,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, strftime('%s', 'now'))
        """, (
            question,
            int(cache_hit),
            model_name,
            input_tokens,
            output_tokens,
            cost_usd,
            latency_ms,
            status
        ))

        connection.commit()


def get_metrics():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT *
            FROM request_metrics
            ORDER BY id DESC
        """).fetchall()

    return [dict(row) for row in rows]
