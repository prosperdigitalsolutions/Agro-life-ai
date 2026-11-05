"""SQLite/PostgreSQL compatibility helpers for AGRO LIFE-AI."""

import sqlite3
import re
from collections.abc import Mapping

from src.database.connection import get_connection, is_postgres


class HybridRow(Mapping):
    """Support both row['column'] and row[0] access."""

    def __init__(self, row):
        self._row = row
        self._keys = list(row.keys()) if hasattr(row, "keys") else []

    def __getitem__(self, key):
        if isinstance(key, int):
            if isinstance(self._row, sqlite3.Row):
                return self._row[key]
            return self._row[self._keys[key]]
        return self._row[key]

    def __iter__(self):
        return iter(self._keys)

    def __len__(self):
        return len(self._keys)

    def keys(self):
        return self._keys


class CompatibleCursor:
    """Translate SQL placeholders and expose generated IDs."""

    PRIMARY_KEYS = {
        "batch_research_measurements": "measurement_id",
        "users": "user_id",
        "farmers": "farmer_id",
        "produce_batches": "batch_id",
        "quality_records": "quality_id",
        "storage_records": "storage_id",
        "transport": "transport_id",
        "market_listings": "listing_id",
        "buyers": "buyer_id",
        "predictions": "prediction_id",
        "recommendations": "recommendation_id",
        "history": "history_id",
        "customer_camera_assessments": "assessment_id",
    }

    def __init__(self, cursor, postgres=False):
        self._cursor = cursor
        self._postgres = postgres
        self._lastrowid = None
        self._expects_generated_id = False

    def execute(self, sql, parameters=None):
        self._lastrowid = None

        if self._postgres:
            sql = sql.replace("?", "%s")

            match = re.match(
                r"\s*INSERT\s+INTO\s+"
                r"(?:(?:public)\s*\.\s*)?"
                r'["`]?([a-zA-Z_][a-zA-Z0-9_]*)["`]?',
                sql,
                re.IGNORECASE,
            )
            if match and not re.search(r"\bRETURNING\b", sql, re.IGNORECASE):
                table = match.group(1).lower()
                primary_key = self.PRIMARY_KEYS.get(table)

                if primary_key:
                    sql = sql.rstrip().rstrip(";") + f" RETURNING {primary_key}"
                    self._expects_generated_id = True
                else:
                    self._expects_generated_id = False
            else:
                self._expects_generated_id = False
        else:
            self._expects_generated_id = False
        if parameters is None:
            self._cursor.execute(sql)
        else:
            self._cursor.execute(sql, parameters)
        return self

    @property
    def lastrowid(self):
        if not self._postgres:
            return self._cursor.lastrowid

        if self._lastrowid is None and self._expects_generated_id:
            row = self._cursor.fetchone()
            if row is not None:
                self._lastrowid = next(iter(row.values()))

        if self._expects_generated_id and self._lastrowid is None:
            raise RuntimeError("PostgreSQL did not return the generated ID.")

        return self._lastrowid

    def fetchone(self):
        row = self._cursor.fetchone()
        return HybridRow(row) if row is not None else None

    def fetchall(self):
        return [HybridRow(row) for row in self._cursor.fetchall()]

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class CompatibleConnection:
    """Expose a small SQLite-like interface for database operations."""

    def __init__(self, connection, postgres=False):
        self._connection = connection
        self._postgres = postgres
        self.row_factory = None

    def cursor(self):
        return CompatibleCursor(self._connection.cursor(), self._postgres)

    def execute(self, sql, parameters=None):
        cursor = self.cursor()
        cursor.execute(sql, parameters)
        return cursor

    def commit(self):
        return self._connection.commit()

    def rollback(self):
        return self._connection.rollback()

    def close(self):
        return self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()
        return False

    def __getattr__(self, name):
        return getattr(self._connection, name)


def get_compatible_connection():
    """Return a compatible connection to Neon or local SQLite."""
    return CompatibleConnection(get_connection(), is_postgres())
