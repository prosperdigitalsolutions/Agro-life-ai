"""
AGRO LIFE-AI
Database Setup

Creates the SQLite database and initial database tables
for the AGRO LIFE-AI multi-produce shelf-life system.
"""

import sqlite3
from pathlib import Path


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "agro_life_ai.db"


# ============================================================
# CREATE DATABASE DIRECTORY
# ============================================================

DATABASE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONNECT TO DATABASE
# ============================================================

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()


# ============================================================
# USERS TABLE
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    user_type TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")


# ============================================================
# PRODUCE TABLE
# ============================================================

cursor.execute("""
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
""")


# ============================================================
# PREDICTIONS TABLE
# ============================================================

cursor.execute("""
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
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (produce_id) REFERENCES produce(produce_id)
)
""")


# ============================================================
# RECOMMENDATIONS TABLE
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_id INTEGER NOT NULL,
    user_type TEXT NOT NULL,
    status TEXT NOT NULL,
    recommendation_text TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prediction_id) REFERENCES predictions(prediction_id)
)
""")


# ============================================================
# HISTORY TABLE
# ============================================================

cursor.execute("""
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
    FOREIGN KEY (prediction_id) REFERENCES predictions(prediction_id)
)
""")

# ============================================================
# FARMERS TABLE
# ============================================================

cursor.execute("""
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
""")


# ============================================================
# PRODUCE BATCHES TABLE
# ============================================================

cursor.execute("""
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
""")

# ============================================================
# QUALITY RECORDS TABLE
# ============================================================

cursor.execute("""
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
""")


# ============================================================
# STORAGE RECORDS TABLE
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS storage_records (
    storage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,
    temperature_c REAL,
    humidity_percent REAL,
    storage_days REAL,
    recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES produce_batches(batch_id)
)
""")

# ============================================================
# TRANSPORT TABLE
# ============================================================

cursor.execute("""
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
""")


# ============================================================
# MARKET LISTINGS TABLE
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS market_listings (
    listing_id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,
    seller_id INTEGER NOT NULL,
    quantity_available_kg REAL NOT NULL,
    price_per_kg REAL NOT NULL,
    quality_status TEXT,
    listing_status TEXT DEFAULT 'AVAILABLE',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES produce_batches(batch_id),
    FOREIGN KEY (seller_id) REFERENCES users(user_id)
)
""")


# ============================================================
# BUYERS TABLE
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS buyers (
    buyer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    buyer_type TEXT,
    buyer_location TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
""")

# ============================================================
# INITIAL PRODUCE REGISTRY
# ============================================================

produce_records = [
    (
        "Tomato",
        "Fruit/Vegetable",
        "final_research_shelf_life_model.joblib",
        0,
        1,
        1,
    ),
    (
        "Mango",
        "Fruit",
        None,
        0,
        0,
        1,
    ),
    (
        "Banana",
        "Fruit",
        None,
        0,
        0,
        1,
    ),
    (
        "Avocado",
        "Fruit",
        None,
        0,
        0,
        1,
    ),
    (
        "Orange",
        "Fruit",
        None,
        0,
        0,
        1,
    ),
    (
        "Leafy Vegetables",
        "Vegetable",
        None,
        0,
        0,
        1,
    ),
    (
        "Other",
        "Other Produce",
        None,
        0,
        0,
        1,
    ),
]


cursor.executemany("""
INSERT OR IGNORE INTO produce (
    name,
    category,
    model_name,
    image_supported,
    prediction_available,
    active
)
VALUES (?, ?, ?, ?, ?, ?)
""", produce_records)


# ============================================================
# SAVE CHANGES
# ============================================================

connection.commit()


# ============================================================
# DISPLAY DATABASE INFORMATION
# ============================================================

print()
print("=" * 60)
print("AGRO LIFE-AI DATABASE SETUP")
print("=" * 60)

print()
print("Database created at:")
print(DATABASE_PATH)

print()
print("Registered produce:")
print("-" * 60)

cursor.execute("""
SELECT produce_id, name, category, prediction_available
FROM produce
ORDER BY produce_id
""")

for record in cursor.fetchall():
    print(
        f"ID: {record[0]} | "
        f"{record[1]} | "
        f"{record[2]} | "
        f"Prediction Available: {bool(record[3])}"
    )


print()
print("Database tables:")
print("-" * 60)

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name
""")

for table in cursor.fetchall():
    print(f"- {table[0]}")


print()
print("Database setup completed successfully!")
print("=" * 60)


# ============================================================
# CLOSE DATABASE
# ============================================================

connection.close()