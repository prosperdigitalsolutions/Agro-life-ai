"""
AGRO LIFE-AI
Shared Database Connection

Uses Neon PostgreSQL when DATABASE_URL is configured.
Falls back to local SQLite for development.
"""

import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load local development settings without overriding existing environment variables.
load_dotenv(PROJECT_ROOT / ".env.local")

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

DATABASE_PATH = Path(
    os.environ.get(
        "AGRO_LIFE_AI_DB_PATH",
        str(PROJECT_ROOT / "database" / "agro_life_ai.db"),
    )
)


def is_postgres():
    """Return True when PostgreSQL is configured."""
    return DATABASE_URL.startswith(("postgresql://", "postgres://"))


def get_connection():
    """
    Open a connection to the configured database.

    PostgreSQL connections use dictionary-style rows.
    SQLite remains the local fallback.
    """
    if is_postgres():
        import psycopg
        from psycopg.rows import dict_row

        return psycopg.connect(
            DATABASE_URL,
            row_factory=dict_row,
            connect_timeout=10,
        )

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection
