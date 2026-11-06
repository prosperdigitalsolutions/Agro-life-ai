"""
AGRO LIFE-AI
Shared Database Connection

Uses Neon PostgreSQL when DATABASE_URL is configured.
Falls back to local SQLite for development.
"""

import atexit
import os
import sqlite3
import threading
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load local development settings without overriding existing environment variables.
load_dotenv(PROJECT_ROOT / ".env.local")

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
# Read Streamlit Cloud Secrets if DATABASE_URL is not in environment variables.
if not DATABASE_URL:
    try:
        import streamlit as st
        DATABASE_URL = str(
            st.secrets.get("DATABASE_URL", "")
        ).strip()
    except Exception:
        DATABASE_URL = ""

DATABASE_PATH = Path(
    os.environ.get(
        "AGRO_LIFE_AI_DB_PATH",
        str(PROJECT_ROOT / "database" / "agro_life_ai.db"),
    )
)


def is_postgres():
    """Return True when PostgreSQL is configured."""
    return DATABASE_URL.startswith(("postgresql://", "postgres://"))


_POSTGRES_POOL = None
_POSTGRES_POOL_LOCK = threading.Lock()


class _PooledConnectionLease:
    """Return a PostgreSQL connection to its pool when closed."""

    def __init__(self, pool, connection):
        self._pool = pool
        self._connection = connection
        self._returned = False
        self._lock = threading.Lock()

    def close(self):
        with self._lock:
            if self._returned:
                return

            try:
                if not self._connection.closed and self._connection.info.transaction_status != 0:
                    self._connection.rollback()
            finally:
                self._returned = True
                self._pool.putconn(self._connection)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is None:
                self._connection.commit()
            else:
                self._connection.rollback()
        finally:
            self.close()
        return False

    def __getattr__(self, name):
        return getattr(self._connection, name)


def _get_postgres_pool():
    """Create the shared PostgreSQL connection pool once per process."""
    global _POSTGRES_POOL

    if _POSTGRES_POOL is None:
        with _POSTGRES_POOL_LOCK:
            if _POSTGRES_POOL is None:
                from psycopg.rows import dict_row
                from psycopg_pool import ConnectionPool

                _POSTGRES_POOL = ConnectionPool(
                    conninfo=DATABASE_URL,
                    kwargs={
                        "row_factory": dict_row,
                        "connect_timeout": 10,
                    },
                    min_size=1,
                    max_size=5,
                    timeout=10,
                    open=True,
                )

    return _POSTGRES_POOL


def close_postgres_pool():
    """Close the shared PostgreSQL pool during application shutdown."""
    global _POSTGRES_POOL

    with _POSTGRES_POOL_LOCK:
        if _POSTGRES_POOL is not None:
            _POSTGRES_POOL.close()
            _POSTGRES_POOL = None


atexit.register(close_postgres_pool)


def get_connection():
    """
    Open a connection to the configured database.

    PostgreSQL connections are borrowed from a shared pool and returned
    when closed. SQLite remains the local development fallback.
    """
    if is_postgres():
        pool = _get_postgres_pool()
        return _PooledConnectionLease(pool, pool.getconn())

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection
