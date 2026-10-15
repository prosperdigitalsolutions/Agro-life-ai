"""
AGRO LIFE-AI
Cloud Database Initializer

Creates the application database and applies repeatable,
non-destructive schema migrations.

IMPORTANT:
Configure AGRO_LIFE_AI_DB_PATH to the intended cloud database
location before executing this script in a hosted environment.
"""

import os
import sqlite3
from pathlib import Path


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = Path(
    os.environ.get(
        "AGRO_LIFE_AI_DB_PATH",
        str(PROJECT_ROOT / "database" / "agro_life_ai.db"),
    )
).expanduser()


# ============================================================
# INITIAL PRODUCE DATA
# ============================================================

PRODUCE = [
    ("Tomato", "Fruit", "shelf_life_random_forest.joblib", 1, 1),
    ("Mango", "Fruit", "shelf_life_random_forest.joblib", 0, 1),
    ("Banana", "Fruit", "shelf_life_random_forest.joblib", 0, 1),
    ("Avocado", "Fruit", "shelf_life_random_forest.joblib", 0, 1),
    ("Orange", "Fruit", "shelf_life_random_forest.joblib", 0, 1),
    ("Leafy Vegetables", "Vegetable", None, 0, 0),
    ("Other", "Other", None, 0, 0),
]


# ============================================================
# DATABASE TABLES
# ============================================================

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        user_type TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS user_credentials (
        credential_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        password_salt TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS produce (
        produce_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL,
        model_name TEXT,
        image_supported INTEGER DEFAULT 0,
        prediction_available INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS predictions (
        prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        produce_id INTEGER NOT NULL,
        prediction_date TEXT DEFAULT CURRENT_TIMESTAMP,
        input_method TEXT NOT NULL,
        total_shelf_life_days REAL,
        current_storage_days REAL,
        remaining_shelf_life_days REAL,
        confidence_note TEXT,
        batch_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (produce_id) REFERENCES produce(produce_id)
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS recommendations (
        recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        prediction_id INTEGER NOT NULL,
        user_type TEXT NOT NULL,
        status TEXT NOT NULL,
        recommendation_text TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (prediction_id)
            REFERENCES predictions(prediction_id)
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS history (
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        prediction_id INTEGER NOT NULL,
        produce_name TEXT NOT NULL,
        total_shelf_life_days REAL,
        remaining_shelf_life_days REAL,
        status TEXT,
        recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (prediction_id)
            REFERENCES predictions(prediction_id)
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS farmers (
        farmer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        farm_name TEXT,
        farm_location TEXT,
        district TEXT,
        province TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS buyers (
        buyer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        buyer_type TEXT,
        buyer_location TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS produce_batches (
        batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER NOT NULL,
        produce_id INTEGER NOT NULL,
        quantity_kg REAL NOT NULL,
        harvest_date TEXT,
        initial_quality TEXT,
        asking_price_per_kg REAL,
        status TEXT DEFAULT 'AVAILABLE',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id),
        FOREIGN KEY (produce_id) REFERENCES produce(produce_id)
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS quality_records (
        quality_id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id INTEGER NOT NULL,
        quality_score REAL,
        visual_status TEXT,
        cv_confidence REAL,
        weight_loss_percent REAL,
        recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (batch_id) REFERENCES produce_batches(batch_id)
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS storage_records (
        storage_id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id INTEGER NOT NULL,
        temperature_c REAL,
        humidity_percent REAL,
        storage_days REAL,
        recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (batch_id) REFERENCES produce_batches(batch_id)
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS transport (
        transport_id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id INTEGER NOT NULL,
        source_location TEXT NOT NULL,
        destination TEXT NOT NULL,
        vehicle_number TEXT,
        transport_cost REAL,
        estimated_duration_hours REAL,
        transport_date TEXT,
        status TEXT DEFAULT 'PLANNED',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (batch_id) REFERENCES produce_batches(batch_id)
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS market_listings (
        listing_id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id INTEGER NOT NULL,
        seller_id INTEGER NOT NULL,
        quantity_available_kg REAL NOT NULL,
        price_per_kg REAL NOT NULL,
        quality_status TEXT,
        listing_status TEXT DEFAULT 'AVAILABLE',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        buyer_id INTEGER,
        FOREIGN KEY (batch_id) REFERENCES produce_batches(batch_id),
        FOREIGN KEY (seller_id) REFERENCES users(user_id),
        FOREIGN KEY (buyer_id) REFERENCES buyers(buyer_id)
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS batch_research_measurements (
        measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id INTEGER NOT NULL,
        day_number INTEGER NOT NULL,
        weight_loss_percent REAL,
        titratable_acidity REAL,
        recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (batch_id) REFERENCES produce_batches(batch_id)
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS customer_camera_assessments (
        assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        produce_id INTEGER NOT NULL,
        predicted_class TEXT NOT NULL,
        model_probability REAL,
        image_path TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (produce_id) REFERENCES produce(produce_id)
    )
    """,
]


# ============================================================
# SAFE SCHEMA MIGRATIONS
# ============================================================

def ensure_columns(connection, table_name, required_columns):
    """Add missing columns without removing existing data."""

    existing_columns = {
        row["name"]
        for row in connection.execute(
            f'PRAGMA table_info("{table_name}")'
        ).fetchall()
    }

    for column_name, definition in required_columns.items():
        if column_name not in existing_columns:
            connection.execute(
                f'ALTER TABLE "{table_name}" '
                f'ADD COLUMN "{column_name}" {definition}'
            )


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():
    """Create required tables and apply safe schema migrations."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH, timeout=30)
    connection.row_factory = sqlite3.Row

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        for statement in SCHEMA:
            connection.execute(statement)

        # Support databases created by earlier app versions.
        ensure_columns(
            connection,
            "predictions",
            {"batch_id": "INTEGER"},
        )

        ensure_columns(
            connection,
            "market_listings",
            {"buyer_id": "INTEGER"},
        )

        # Seed produce without duplicating existing produce names.
        connection.executemany(
            """
            INSERT OR IGNORE INTO produce (
                name,
                category,
                model_name,
                image_supported,
                prediction_available
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            PRODUCE,
        )

        connection.commit()

        print("AGRO LIFE-AI database initialized successfully.")
        print(f"Database location: {DATABASE_PATH}")
        print(f"Tables defined: {len(SCHEMA)}")
        print("Schema migrations completed successfully.")

        user_count = connection.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        credential_count = connection.execute(
            "SELECT COUNT(*) FROM user_credentials"
        ).fetchone()[0]

        active_credential_count = connection.execute(
            "SELECT COUNT(*) FROM user_credentials WHERE is_active = 1"
        ).fetchone()[0]

        print(f"Login diagnostic - users: {user_count}")
        print(f"Login diagnostic - credentials: {credential_count}")
        print(f"Login diagnostic - active credentials: {active_credential_count}")


    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    initialize_database()
