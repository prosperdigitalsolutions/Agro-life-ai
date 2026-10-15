"""
AGRO LIFE-AI
Database Manager

Handles users, produce, predictions, recommendations,
and historical records for the AGRO LIFE-AI system.
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional

from src.database.connection import is_postgres
from src.database.db_compat import get_compatible_connection


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = Path(os.environ.get("AGRO_LIFE_AI_DB_PATH", str(PROJECT_ROOT / "database" / "agro_life_ai.db")))


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    conn = get_compatible_connection()

    if not is_postgres():
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS batch_research_measurements (
                measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id INTEGER NOT NULL,
                day_number INTEGER NOT NULL,
                weight_loss_percent REAL NOT NULL,
                titratable_acidity REAL NOT NULL,
                recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (batch_id)
                    REFERENCES produce_batches(batch_id)
            )
            """
        )
        conn.commit()

    return conn

def add_batch_research_measurement(
    batch_id: int,
    day_number: int,
    weight_loss_percent: float,
    titratable_acidity: float,
):
    if day_number < 0:
        raise ValueError("Day number cannot be negative.")

    if weight_loss_percent < 0:
        raise ValueError("Weight loss cannot be negative.")

    if titratable_acidity < 0:
        raise ValueError("Titratable acidity cannot be negative.")

    conn = get_connection()

    try:
        batch = conn.execute(
            """
            SELECT batch_id
            FROM produce_batches
            WHERE batch_id = ?
            """,
            (batch_id,),
        ).fetchone()

        if batch is None:
            raise ValueError(
                f"Produce batch ID {batch_id} does not exist."
            )

        existing = conn.execute(
            """
            SELECT measurement_id
            FROM batch_research_measurements
            WHERE batch_id = ?
              AND day_number = ?
            """,
            (batch_id, day_number),
        ).fetchone()

        if existing is not None:
            raise ValueError(
                f"A research measurement for Day {day_number} "
                f"already exists for batch #{batch_id}."
            )

        cursor = conn.execute(
            """
            INSERT INTO batch_research_measurements (
                batch_id,
                day_number,
                weight_loss_percent,
                titratable_acidity
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                batch_id,
                day_number,
                weight_loss_percent,
                titratable_acidity,
            ),
        )

        conn.commit()

        return cursor.lastrowid

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def get_batch_research_measurements(batch_id: int):
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                measurement_id,
                batch_id,
                day_number,
                weight_loss_percent,
                titratable_acidity,
                recorded_at
            FROM batch_research_measurements
            WHERE batch_id = ?
            ORDER BY day_number ASC, measurement_id ASC
            """,
            (batch_id,),
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()
if not is_postgres():
    try:
        connection = get_connection()
        try:
            connection.execute(
                """
                ALTER TABLE market_listings
                ADD COLUMN buyer_id INTEGER
                REFERENCES buyers(buyer_id)
                """
            )
            connection.commit()
        finally:
            connection.close()

    except sqlite3.OperationalError as e:
        # Column already exists in the local SQLite database.
        if "duplicate column name" not in str(e).lower():
            raise
# ============================================================
# USER MANAGEMENT
# ============================================================

def add_user(
    full_name: str,
    user_type: str,
    phone: Optional[str] = None,
    email: Optional[str] = None,
):
    """
    Add a farmer or customer to the database.

    Returns:
        int: Newly created user ID.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO users (
            full_name,
            user_type,
            phone,
            email
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            full_name,
            user_type,
            phone,
            email,
        ),
    )

    user_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return user_id


def get_user(user_id: int):
    """
    Retrieve one user by ID.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            user_id,
            full_name,
            user_type,
            phone,
            email,
            created_at
        FROM users
        WHERE user_id = ?
        """,
        (user_id,),
    )

    user = cursor.fetchone()

    connection.close()

    return user


# ============================================================
# FARMER MANAGEMENT
# ============================================================

def add_farmer(
    full_name: str,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    farm_name: Optional[str] = None,
    farm_location: Optional[str] = None,
    district: Optional[str] = None,
    province: Optional[str] = None,
):
    """
    Register a new farmer.

    A farmer is first registered in the users table and then
    linked to the farmers table.

    Returns:
        int: Newly created farmer ID.
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # ----------------------------------------------------
        # CREATE USER RECORD
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO users (
                full_name,
                user_type,
                phone,
                email
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                full_name,
                "FARMER",
                phone,
                email,
            ),
        )

        user_id = cursor.lastrowid

        # ----------------------------------------------------
        # CREATE FARMER RECORD
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO farmers (
                user_id,
                farm_name,
                farm_location,
                district,
                province
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                farm_name,
                farm_location,
                district,
                province,
            ),
        )

        farmer_id = cursor.lastrowid

        connection.commit()

        return farmer_id

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()


def get_farmer(farmer_id: int):
    """
    Retrieve one farmer by farmer ID.

    Returns:
        dict or None
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            f.farmer_id,
            f.user_id,
            u.full_name,
            u.phone,
            u.email,
            f.farm_name,
            f.farm_location,
            f.district,
            f.province,
            f.created_at
        FROM farmers f
        INNER JOIN users u
            ON f.user_id = u.user_id
        WHERE f.farmer_id = ?
        """,
        (farmer_id,),
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "farmer_id": row[0],
        "user_id": row[1],
        "full_name": row[2],
        "phone": row[3],
        "email": row[4],
        "farm_name": row[5],
        "farm_location": row[6],
        "district": row[7],
        "province": row[8],
        "created_at": row[9],
    }


def get_all_farmers():
    """
    Retrieve all registered farmers.

    Returns:
        list: Farmer records as dictionaries.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            f.farmer_id,
            f.user_id,
            u.full_name,
            u.phone,
            u.email,
            f.farm_name,
            f.farm_location,
            f.district,
            f.province,
            f.created_at
        FROM farmers f
        INNER JOIN users u
            ON f.user_id = u.user_id
        ORDER BY f.farmer_id DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    farmers = []

    for row in rows:

        farmers.append(
            {
                "farmer_id": row[0],
                "user_id": row[1],
                "full_name": row[2],
                "phone": row[3],
                "email": row[4],
                "farm_name": row[5],
                "farm_location": row[6],
                "district": row[7],
                "province": row[8],
                "created_at": row[9],
            }
        )

    return farmers


def update_farmer(
    farmer_id: int,
    full_name: str,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    farm_name: Optional[str] = None,
    farm_location: Optional[str] = None,
    district: Optional[str] = None,
    province: Optional[str] = None,
):
    """
    Update farmer information.

    Returns:
        bool: True if update was successful.
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # ----------------------------------------------------
        # FIND USER LINKED TO FARMER
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT user_id
            FROM farmers
            WHERE farmer_id = ?
            """,
            (farmer_id,),
        )

        result = cursor.fetchone()

        if result is None:
            return False

        user_id = result[0]

        # ----------------------------------------------------
        # UPDATE USER INFORMATION
        # ----------------------------------------------------

        cursor.execute(
            """
            UPDATE users
            SET
                full_name = ?,
                phone = ?,
                email = ?
            WHERE user_id = ?
            """,
            (
                full_name,
                phone,
                email,
                user_id,
            ),
        )

        # ----------------------------------------------------
        # UPDATE FARMER INFORMATION
        # ----------------------------------------------------

        cursor.execute(
            """
            UPDATE farmers
            SET
                farm_name = ?,
                farm_location = ?,
                district = ?,
                province = ?
            WHERE farmer_id = ?
            """,
            (
                farm_name,
                farm_location,
                district,
                province,
                farmer_id,
            ),
        )

        connection.commit()

        return True

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()


def deactivate_farmer(farmer_id: int):
    """
    Deactivate a farmer.

    The farmer's records are preserved. The user account is
    changed to INACTIVE rather than physically deleting data.

    Returns:
        bool: True if successful.
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT user_id
            FROM farmers
            WHERE farmer_id = ?
            """,
            (farmer_id,),
        )

        result = cursor.fetchone()

        if result is None:
            return False

        user_id = result[0]

        cursor.execute(
            """
            UPDATE users
            SET user_type = 'INACTIVE_FARMER'
            WHERE user_id = ?
            """,
            (user_id,),
        )

        connection.commit()

        return True

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()
def delete_farmer(farmer_id: int):
    """
    Permanently delete a farmer and all records owned by that farmer.

    Deleted records include:
    - recommendations linked to the farmer's predictions
    - prediction history linked to the farmer's predictions
    - predictions belonging to the farmer
    - marketplace listings created by the farmer
    - quality records for the farmer's batches
    - storage records for the farmer's batches
    - transport records for the farmer's batches
    - research measurements for the farmer's batches
    - produce batches belonging to the farmer
    - farmer record
    - linked user record

    Buyers, produce types, and other farmers are not deleted.

    Returns:
        bool: True if the farmer was successfully deleted.
        False if the farmer does not exist.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ----------------------------------------------------
        # 1. CHECK THAT THE FARMER EXISTS
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT farmer_id, user_id
            FROM farmers
            WHERE farmer_id = ?
            """,
            (farmer_id,),
        )

        farmer = cursor.fetchone()

        if farmer is None:
            return False

        user_id = farmer["user_id"]


        # ----------------------------------------------------
        # 2. PROTECT MARKETPLACE TRANSACTIONS
        # ----------------------------------------------------
        # Do not delete farmers with reserved or sold listings,
        # or listings already linked to a buyer.

        cursor.execute(
            """
            SELECT listing_id
            FROM market_listings
            WHERE (
                seller_id = ?
                OR batch_id IN (
                    SELECT batch_id
                    FROM produce_batches
                    WHERE farmer_id = ?
                )
            )
            AND (
                UPPER(COALESCE(listing_status, '')) IN (
                    'RESERVED',
                    'SOLD'
                )
                OR buyer_id IS NOT NULL
            )
            LIMIT 1
            """,
            (user_id, farmer_id),
        )

        protected_listing = cursor.fetchone()

        if protected_listing is not None:
            raise ValueError(
                "This farmer cannot be deleted because marketplace "
                "listings are reserved, sold, or linked to a buyer. "
                "Resolve the marketplace transactions first."
            )

        # ----------------------------------------------------
        # 3. DELETE RECOMMENDATIONS
        # ----------------------------------------------------
        # Recommendations depend on predictions.

        cursor.execute(
            """
            DELETE FROM recommendations
            WHERE prediction_id IN (
                SELECT prediction_id
                FROM predictions
                WHERE user_id = ?
                   OR batch_id IN (
                       SELECT batch_id
                       FROM produce_batches
                       WHERE farmer_id = ?
                   )
            )
            """,
            (user_id, farmer_id),
        )

        # ----------------------------------------------------
        # 4. DELETE PREDICTION HISTORY
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM history
            WHERE prediction_id IN (
                SELECT prediction_id
                FROM predictions
                WHERE user_id = ?
                   OR batch_id IN (
                       SELECT batch_id
                       FROM produce_batches
                       WHERE farmer_id = ?
                   )
            )
            """,
            (user_id, farmer_id),
        )

        # ----------------------------------------------------
        # 5. DELETE PREDICTIONS
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM predictions
            WHERE user_id = ?
               OR batch_id IN (
                   SELECT batch_id
                   FROM produce_batches
                   WHERE farmer_id = ?
               )
            """,
            (user_id, farmer_id),
        )

        # ----------------------------------------------------
        # 6. DELETE MARKETPLACE LISTINGS
        # ----------------------------------------------------
        # Listings can reference the farmer through:
        # seller_id -> users.user_id
        # and through batch_id.

        cursor.execute(
            """
            DELETE FROM market_listings
            WHERE seller_id = ?
               OR batch_id IN (
                   SELECT batch_id
                   FROM produce_batches
                   WHERE farmer_id = ?
               )
            """,
            (user_id, farmer_id),
        )

        # ----------------------------------------------------
        # 7. DELETE QUALITY RECORDS
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM quality_records
            WHERE batch_id IN (
                SELECT batch_id
                FROM produce_batches
                WHERE farmer_id = ?
            )
            """,
            (farmer_id,),
        )

        # ----------------------------------------------------
        # 8. DELETE STORAGE RECORDS
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM storage_records
            WHERE batch_id IN (
                SELECT batch_id
                FROM produce_batches
                WHERE farmer_id = ?
            )
            """,
            (farmer_id,),
        )

        # ----------------------------------------------------
        # 9. DELETE TRANSPORT RECORDS
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM transport
            WHERE batch_id IN (
                SELECT batch_id
                FROM produce_batches
                WHERE farmer_id = ?
            )
            """,
            (farmer_id,),
        )

        # ----------------------------------------------------
        # 10. DELETE RESEARCH MEASUREMENTS
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM batch_research_measurements
            WHERE batch_id IN (
                SELECT batch_id
                FROM produce_batches
                WHERE farmer_id = ?
            )
            """,
            (farmer_id,),
        )

        # ----------------------------------------------------
        # 11. DELETE PRODUCE BATCHES
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM produce_batches
            WHERE farmer_id = ?
            """,
            (farmer_id,),
        )

        # ----------------------------------------------------
        # 12. DELETE FARMER RECORD
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM farmers
            WHERE farmer_id = ?
            """,
            (farmer_id,),
        )

        # ----------------------------------------------------
        # 13. DELETE LINKED USER CREDENTIALS
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM user_credentials
            WHERE user_id = ?
            """,
            (user_id,),
        )

        # ----------------------------------------------------
        # 14. DELETE LINKED USER RECORD
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM users
            WHERE user_id = ?
            """,
            (user_id,),
        )

        # ----------------------------------------------------
        # 14. SAVE EVERYTHING
        # ----------------------------------------------------

        connection.commit()

        return True

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()

# ============================================================
# PRODUCE BATCH MANAGEMENT
# ============================================================

def add_produce_batch(
    farmer_id: int,
    produce_id: int,
    quantity_kg: float,
    harvest_date: Optional[str] = None,
    initial_quality: Optional[str] = None,
    asking_price_per_kg: Optional[float] = None,
    status: str = "AVAILABLE",
):
    """
    Register a new produce batch for a farmer.

    Returns:
        int: Newly created batch ID.
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # ----------------------------------------------------
        # VERIFY FARMER
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT farmer_id
            FROM farmers
            WHERE farmer_id = ?
            """,
            (farmer_id,),
        )

        farmer = cursor.fetchone()

        if farmer is None:
            raise ValueError(
                f"Farmer with ID {farmer_id} does not exist."
            )

        # ----------------------------------------------------
        # VERIFY PRODUCE
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT produce_id
            FROM produce
            WHERE produce_id = ?
              AND active = 1
            """,
            (produce_id,),
        )

        produce = cursor.fetchone()

        if produce is None:
            raise ValueError(
                f"Produce with ID {produce_id} does not exist."
            )

        # ----------------------------------------------------
        # VALIDATE QUANTITY
        # ----------------------------------------------------

        if quantity_kg <= 0:
            raise ValueError(
                "Quantity must be greater than zero."
            )

        # ----------------------------------------------------
        # INSERT PRODUCE BATCH
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO produce_batches (
                farmer_id,
                produce_id,
                quantity_kg,
                harvest_date,
                initial_quality,
                asking_price_per_kg,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                farmer_id,
                produce_id,
                quantity_kg,
                harvest_date,
                initial_quality,
                asking_price_per_kg,
                status,
            ),
        )

        batch_id = cursor.lastrowid

        connection.commit()

        return batch_id

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()


def get_produce_batch(batch_id: int):
    """
    Retrieve one produce batch with farmer and produce details.

    Returns:
        dict or None
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            pb.batch_id,
            pb.farmer_id,
            u.full_name,
            pb.produce_id,
            p.name,
            pb.quantity_kg,
            pb.harvest_date,
            pb.initial_quality,
            pb.asking_price_per_kg,
            pb.status,
            pb.created_at
        FROM produce_batches pb

        INNER JOIN farmers f
            ON pb.farmer_id = f.farmer_id

        INNER JOIN users u
            ON f.user_id = u.user_id

        INNER JOIN produce p
            ON pb.produce_id = p.produce_id

        WHERE pb.batch_id = ?
        """,
        (batch_id,),
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "batch_id": row[0],
        "farmer_id": row[1],
        "farmer_name": row[2],
        "produce_id": row[3],
        "produce_name": row[4],
        "quantity_kg": row[5],
        "harvest_date": row[6],
        "initial_quality": row[7],
        "asking_price_per_kg": row[8],
        "status": row[9],
        "created_at": row[10],
    }


def get_farmer_batches(farmer_id: int):
    """
    Retrieve all produce batches belonging to a farmer.

    Returns:
        list: Produce batches as dictionaries.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            pb.batch_id,
            pb.farmer_id,
            u.full_name,
            pb.produce_id,
            p.name,
            pb.quantity_kg,
            pb.harvest_date,
            pb.initial_quality,
            pb.asking_price_per_kg,
            pb.status,
            pb.created_at
        FROM produce_batches pb

        INNER JOIN farmers f
            ON pb.farmer_id = f.farmer_id

        INNER JOIN users u
            ON f.user_id = u.user_id

        INNER JOIN produce p
            ON pb.produce_id = p.produce_id

        WHERE pb.farmer_id = ?

        ORDER BY pb.batch_id DESC
        """,
        (farmer_id,),
    )

    rows = cursor.fetchall()

    connection.close()

    batches = []

    for row in rows:

        batches.append(
            {
                "batch_id": row[0],
                "farmer_id": row[1],
                "farmer_name": row[2],
                "produce_id": row[3],
                "produce_name": row[4],
                "quantity_kg": row[5],
                "harvest_date": row[6],
                "initial_quality": row[7],
                "asking_price_per_kg": row[8],
                "status": row[9],
                "created_at": row[10],
            }
        )

    return batches
  

def update_batch_status(
    batch_id: int,
    status: str,
):
    """
    Update the status of a produce batch.

    Examples:
        AVAILABLE
        SOLD
        EXPIRED
        RESERVED
        CANCELLED

    Returns:
        bool: True if successful.
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE produce_batches
            SET status = ?
            WHERE batch_id = ?
            """,
            (
                status,
                batch_id,
            ),
        )

        if cursor.rowcount == 0:
            return False

        connection.commit()

        return True

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()

def delete_produce_batch(batch_id):
    """
    Permanently delete a produce batch and its directly related records.

    Related records deleted:
    - quality_records
    - storage_records
    - transport
    - market_listings
    - batch_research_measurements

    The farmer, produce type, buyers, users, predictions,
    history, and recommendations are not deleted.
    """

    conn = get_connection()

    try:

        cursor = conn.cursor()

        # ----------------------------------------------------
        # CHECK THAT THE BATCH EXISTS
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT batch_id
            FROM produce_batches
            WHERE batch_id = ?
            """,
            (batch_id,)
        )

        batch = cursor.fetchone()

        if batch is None:
            return False

        # ----------------------------------------------------
        # DELETE RELATED RECORDS
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM quality_records
            WHERE batch_id = ?
            """,
            (batch_id,)
        )

        cursor.execute(
            """
            DELETE FROM storage_records
            WHERE batch_id = ?
            """,
            (batch_id,)
        )

        cursor.execute(
            """
            DELETE FROM transport
            WHERE batch_id = ?
            """,
            (batch_id,)
        )

        cursor.execute(
            """
            DELETE FROM market_listings
            WHERE batch_id = ?
            """,
            (batch_id,)
        )

        cursor.execute(
            """
            DELETE FROM batch_research_measurements
            WHERE batch_id = ?
            """,
            (batch_id,)
        )

        # ----------------------------------------------------
        # DELETE THE PRODUCE BATCH
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM produce_batches
            WHERE batch_id = ?
            """,
            (batch_id,)
        )

        # ----------------------------------------------------
        # SAVE CHANGES
        # ----------------------------------------------------

        conn.commit()

        return True

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()
# ============================================================
# PRODUCE MANAGEMENT
# ============================================================

def get_all_produce():
    """
    Retrieve all active produce registered in AGRO LIFE-AI.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            produce_id,
            name,
            category,
            model_name,
            image_supported,
            prediction_available,
            active
        FROM produce
        WHERE active = 1
        ORDER BY produce_id
        """
    )

    produce = cursor.fetchall()

    connection.close()

    return produce


def get_produce_by_name(name: str):
    """
    Retrieve produce information by name.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            produce_id,
            name,
            category,
            model_name,
            image_supported,
            prediction_available,
            active
        FROM produce
        WHERE name = ?
        """,
        (name,),
    )

    produce = cursor.fetchone()

    connection.close()

    return produce

# ============================================================
# QUALITY RECORD MANAGEMENT
# ============================================================

def add_quality_record(
    batch_id: int,
    quality_score: float = None,
    visual_status: str = None,
    cv_confidence: float = None,
    weight_loss_percent: float = None,
):
    """
    Add a quality assessment record for a produce batch.

    Returns:
        quality_id if successful
        None if the batch does not exist
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Verify that the batch exists
        cursor.execute(
            """
            SELECT batch_id
            FROM produce_batches
            WHERE batch_id = ?
            """,
            (batch_id,),
        )

        batch = cursor.fetchone()

        if batch is None:
            return None

        # Validate quality score
        if quality_score is not None:
            if quality_score < 0 or quality_score > 10:
                raise ValueError(
                    "Quality score must be between 0 and 10."
                )

        # Validate CV confidence
        if cv_confidence is not None:
            if cv_confidence < 0 or cv_confidence > 1:
                raise ValueError(
                    "CV confidence must be between 0 and 1."
                )

        # Validate weight loss
        if weight_loss_percent is not None:
            if weight_loss_percent < 0:
                raise ValueError(
                    "Weight loss percentage cannot be negative."
                )

        cursor.execute(
            """
            INSERT INTO quality_records (
                batch_id,
                quality_score,
                visual_status,
                cv_confidence,
                weight_loss_percent
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                batch_id,
                quality_score,
                visual_status,
                cv_confidence,
                weight_loss_percent,
            ),
        )

        quality_id = cursor.lastrowid

        conn.commit()

        return quality_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_quality_record(quality_id: int):
    """
    Retrieve a quality record together with its
    associated batch, farmer and produce information.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                qr.quality_id,
                qr.batch_id,
                pb.farmer_id,
                u.full_name AS farmer_name,
                pb.produce_id,
                p.name AS produce_name,
                qr.quality_score,
                qr.visual_status,
                qr.cv_confidence,
                qr.weight_loss_percent,
                qr.recorded_at

            FROM quality_records qr

            INNER JOIN produce_batches pb
                ON qr.batch_id = pb.batch_id

            INNER JOIN farmers f
                ON pb.farmer_id = f.farmer_id

            INNER JOIN users u
                ON f.user_id = u.user_id

            INNER JOIN produce p
                ON pb.produce_id = p.produce_id

            WHERE qr.quality_id = ?
            """,
            (quality_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        conn.close()


def get_batch_quality_records(batch_id: int):
    """
    Retrieve all quality records belonging to a produce batch.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                qr.quality_id,
                qr.batch_id,
                qr.quality_score,
                qr.visual_status,
                qr.cv_confidence,
                qr.weight_loss_percent,
                qr.recorded_at

            FROM quality_records qr

            WHERE qr.batch_id = ?

            ORDER BY qr.quality_id DESC
            """,
            (batch_id,),
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()

# ============================================================
# STORAGE RECORD MANAGEMENT
# ============================================================

def add_storage_record(
    batch_id: int,
    temperature_c: float = None,
    humidity_percent: float = None,
    storage_days: float = None,
):
    """
    Add a storage/environmental record for a produce batch.

    Returns:
        storage_id if successful
        None if the batch does not exist
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Verify that the batch exists
        cursor.execute(
            """
            SELECT batch_id
            FROM produce_batches
            WHERE batch_id = ?
            """,
            (batch_id,),
        )

        batch = cursor.fetchone()

        if batch is None:
            return None

        # Validate temperature
        if temperature_c is not None:
            if temperature_c < -50 or temperature_c > 100:
                raise ValueError(
                    "Temperature must be between -50 and 100 degrees Celsius."
                )

        # Validate humidity
        if humidity_percent is not None:
            if humidity_percent < 0 or humidity_percent > 100:
                raise ValueError(
                    "Humidity percentage must be between 0 and 100."
                )

        # Validate storage duration
        if storage_days is not None:
            if storage_days < 0:
                raise ValueError(
                    "Storage days cannot be negative."
                )

        cursor.execute(
            """
            INSERT INTO storage_records (
                batch_id,
                temperature_c,
                humidity_percent,
                storage_days
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                batch_id,
                temperature_c,
                humidity_percent,
                storage_days,
            ),
        )

        storage_id = cursor.lastrowid

        conn.commit()

        return storage_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_storage_record(storage_id: int):
    """
    Retrieve a storage record together with
    its associated batch, farmer and produce.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                sr.storage_id,
                sr.batch_id,
                pb.farmer_id,
                u.full_name AS farmer_name,
                pb.produce_id,
                p.name AS produce_name,
                sr.temperature_c,
                sr.humidity_percent,
                sr.storage_days,
                sr.recorded_at

            FROM storage_records sr

            INNER JOIN produce_batches pb
                ON sr.batch_id = pb.batch_id

            INNER JOIN farmers f
                ON pb.farmer_id = f.farmer_id

            INNER JOIN users u
                ON f.user_id = u.user_id

            INNER JOIN produce p
                ON pb.produce_id = p.produce_id

            WHERE sr.storage_id = ?
            """,
            (storage_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        conn.close()


def get_batch_storage_records(batch_id: int):
    """
    Retrieve all storage records belonging to a produce batch.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                sr.storage_id,
                sr.batch_id,
                sr.temperature_c,
                sr.humidity_percent,
                sr.storage_days,
                sr.recorded_at

            FROM storage_records sr

            WHERE sr.batch_id = ?

            ORDER BY sr.storage_id DESC
            """,
            (batch_id,),
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()

# ============================================================
# TRANSPORT MANAGEMENT
# ============================================================

def add_transport(
    batch_id: int,
    source_location: str,
    destination: str,
    vehicle_number: str = None,
    transport_cost: float = None,
    estimated_duration_hours: float = None,
    transport_date: str = None,
    status: str = "PLANNED",
):
    """
    Register a transport record for a produce batch.

    Returns:
        transport_id if successful
        None if the batch does not exist
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Verify that the batch exists
        cursor.execute(
            """
            SELECT batch_id
            FROM produce_batches
            WHERE batch_id = ?
            """,
            (batch_id,),
        )

        batch = cursor.fetchone()

        if batch is None:
            return None

        # Validate required locations
        if not source_location or not source_location.strip():
            raise ValueError(
                "Source location is required."
            )

        if not destination or not destination.strip():
            raise ValueError(
                "Destination is required."
            )

        # Validate transport cost
        if transport_cost is not None:
            if transport_cost < 0:
                raise ValueError(
                    "Transport cost cannot be negative."
                )

        # Validate duration
        if estimated_duration_hours is not None:
            if estimated_duration_hours < 0:
                raise ValueError(
                    "Estimated duration cannot be negative."
                )

        cursor.execute(
            """
            INSERT INTO transport (
                batch_id,
                source_location,
                destination,
                vehicle_number,
                transport_cost,
                estimated_duration_hours,
                transport_date,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                batch_id,
                source_location,
                destination,
                vehicle_number,
                transport_cost,
                estimated_duration_hours,
                transport_date,
                status,
            ),
        )

        transport_id = cursor.lastrowid

        conn.commit()

        return transport_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_transport(transport_id: int):
    """
    Retrieve a transport record together with
    its associated batch, farmer and produce.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                t.transport_id,
                t.batch_id,
                pb.farmer_id,
                u.full_name AS farmer_name,
                pb.produce_id,
                p.name AS produce_name,
                t.source_location,
                t.destination,
                t.vehicle_number,
                t.transport_cost,
                t.estimated_duration_hours,
                t.transport_date,
                t.status,
                t.created_at

            FROM transport t

            INNER JOIN produce_batches pb
                ON t.batch_id = pb.batch_id

            INNER JOIN farmers f
                ON pb.farmer_id = f.farmer_id

            INNER JOIN users u
                ON f.user_id = u.user_id

            INNER JOIN produce p
                ON pb.produce_id = p.produce_id

            WHERE t.transport_id = ?
            """,
            (transport_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        conn.close()


def get_batch_transport_records(batch_id: int):
    """
    Retrieve all transport records belonging
    to a produce batch.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                t.transport_id,
                t.batch_id,
                t.source_location,
                t.destination,
                t.vehicle_number,
                t.transport_cost,
                t.estimated_duration_hours,
                t.transport_date,
                t.status,
                t.created_at

            FROM transport t

            WHERE t.batch_id = ?

            ORDER BY t.transport_id DESC
            """,
            (batch_id,),
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


def update_transport_status(
    transport_id: int,
    status: str,
):
    """
    Update the status of a transport record.

    Example statuses:
        PLANNED
        IN_TRANSIT
        COMPLETED
        CANCELLED
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE transport
            SET status = ?
            WHERE transport_id = ?
            """,
            (status, transport_id),
        )

        updated = cursor.rowcount > 0

        conn.commit()

        return updated

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

# ============================================================
# MARKET LISTING MANAGEMENT
# ============================================================

def add_market_listing(
    batch_id: int,
    seller_id: int,
    quantity_available_kg: float,
    price_per_kg: float,
    quality_status: str = None,
    listing_status: str = "AVAILABLE",
):
    """
    Create a market listing for a produce batch.

    Returns:
        listing_id if successful
        None if the batch or seller does not exist
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Verify batch exists
        cursor.execute(
            """
            SELECT batch_id
            FROM produce_batches
            WHERE batch_id = ?
            """,
            (batch_id,),
        )

        batch = cursor.fetchone()

        if batch is None:
            return None

        # Verify seller/user exists
        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE user_id = ?
            """,
            (seller_id,),
        )

        seller = cursor.fetchone()

        if seller is None:
            return None

        # Validate quantity
        if quantity_available_kg <= 0:
            raise ValueError(
                "Available quantity must be greater than zero."
            )

        # Validate price
        if price_per_kg < 0:
            raise ValueError(
                "Price per kilogram cannot be negative."
            )

        # Check available batch quantity
        cursor.execute(
            """
            SELECT quantity_kg
            FROM produce_batches
            WHERE batch_id = ?
            """,
            (batch_id,),
        )

        batch_data = cursor.fetchone()

        if quantity_available_kg > batch_data[0]:
            raise ValueError(
                "Listed quantity cannot exceed batch quantity."
            )

        cursor.execute(
            """
            INSERT INTO market_listings (
                batch_id,
                seller_id,
                quantity_available_kg,
                price_per_kg,
                quality_status,
                listing_status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                batch_id,
                seller_id,
                quantity_available_kg,
                price_per_kg,
                quality_status,
                listing_status,
            ),
        )

        listing_id = cursor.lastrowid

        conn.commit()

        return listing_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_all_market_listings():
    """
    Retrieve all marketplace listings,
    including seller and assigned buyer information.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                ml.listing_id,
                ml.batch_id,
                ml.seller_id,
                u.full_name AS seller_name,

                p.name AS produce_name,

                ml.quantity_available_kg,
                ml.price_per_kg,
                ml.quality_status,
                ml.listing_status,
                ml.created_at,

                ml.buyer_id,

                buyer_user.full_name AS buyer_name,
                b.buyer_type,
                b.buyer_location

            FROM market_listings ml

            INNER JOIN users u
                ON ml.seller_id = u.user_id

            INNER JOIN produce_batches pb
                ON ml.batch_id = pb.batch_id

            INNER JOIN farmers f
                ON pb.farmer_id = f.farmer_id

            INNER JOIN produce p
                ON pb.produce_id = p.produce_id

            LEFT JOIN buyers b
                ON ml.buyer_id = b.buyer_id

            LEFT JOIN users buyer_user
                ON b.user_id = buyer_user.user_id

            ORDER BY ml.listing_id DESC
            """
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()

def get_farmer_market_listings(farmer_id: int):
    """
    Retrieve all market listings belonging
    to a farmer, including assigned buyer information.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                ml.listing_id,
                ml.batch_id,
                ml.seller_id,
                u.full_name AS seller_name,

                p.name AS produce_name,

                ml.quantity_available_kg,
                ml.price_per_kg,
                ml.quality_status,
                ml.listing_status,
                ml.created_at,

                ml.buyer_id,

                buyer_user.full_name AS buyer_name,
                b.buyer_type,
                b.buyer_location

            FROM market_listings ml

            INNER JOIN users u
                ON ml.seller_id = u.user_id

            INNER JOIN produce_batches pb
                ON ml.batch_id = pb.batch_id

            INNER JOIN farmers f
                ON pb.farmer_id = f.farmer_id

            INNER JOIN produce p
                ON pb.produce_id = p.produce_id

            LEFT JOIN buyers b
                ON ml.buyer_id = b.buyer_id

            LEFT JOIN users buyer_user
                ON b.user_id = buyer_user.user_id

            WHERE f.farmer_id = ?

            ORDER BY ml.listing_id DESC
            """,
            (farmer_id,),
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


def update_market_listing_status(
    listing_id: int,
    listing_status: str,
):
    """
    Update the status of a market listing.

    Example statuses:
        AVAILABLE
        RESERVED
        SOLD
        EXPIRED
        CANCELLED
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE market_listings
            SET listing_status = ?
            WHERE listing_id = ?
            """,
            (
                listing_status,
                listing_id,
            ),
        )

        updated = cursor.rowcount > 0

        conn.commit()

        return updated

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

        # ============================================================
# BUYER MANAGEMENT
# ============================================================

def add_buyer(
    full_name: str,
    buyer_type: str,
    buyer_location: str = None,
    phone: str = None,
    email: str = None,
):
    """
    Register a buyer.

    Creates a common user record first and then
    creates the buyer-specific profile.

    Returns:
        buyer_id if successful
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Create common user record
        cursor.execute(
            """
            INSERT INTO users (
                full_name,
                user_type,
                phone,
                email
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                full_name,
                "BUYER",
                phone,
                email,
            ),
        )

        user_id = cursor.lastrowid

        # Create buyer profile
        cursor.execute(
            """
            INSERT INTO buyers (
                user_id,
                buyer_type,
                buyer_location
            )
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                buyer_type,
                buyer_location,
            ),
        )

        buyer_id = cursor.lastrowid

        conn.commit()

        return buyer_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_buyer(buyer_id: int):
    """
    Retrieve a buyer together with common user information.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                b.buyer_id,
                b.user_id,
                u.full_name,
                u.phone,
                u.email,
                b.buyer_type,
                b.buyer_location,
                b.created_at

            FROM buyers b

            INNER JOIN users u
                ON b.user_id = u.user_id

            WHERE b.buyer_id = ?
            """,
            (buyer_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        conn.close()


def get_all_buyers():
    """
    Retrieve all registered buyers.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                b.buyer_id,
                b.user_id,
                u.full_name,
                u.phone,
                u.email,
                b.buyer_type,
                b.buyer_location,
                b.created_at

            FROM buyers b

            INNER JOIN users u
                ON b.user_id = u.user_id

            ORDER BY b.buyer_id DESC
            """
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


def update_buyer(
    buyer_id: int,
    full_name: str = None,
    buyer_type: str = None,
    buyer_location: str = None,
    phone: str = None,
    email: str = None,
):
    """
    Update buyer information.
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Find linked user
        cursor.execute(
            """
            SELECT user_id
            FROM buyers
            WHERE buyer_id = ?
            """,
            (buyer_id,),
        )

        buyer = cursor.fetchone()

        if buyer is None:
            return False

        user_id = buyer[0]

        cursor.execute(
            """
            UPDATE users
            SET
                full_name = COALESCE(?, full_name),
                phone = COALESCE(?, phone),
                email = COALESCE(?, email)
            WHERE user_id = ?
            """,
            (
                full_name,
                phone,
                email,
                user_id,
            ),
        )

        cursor.execute(
            """
            UPDATE buyers
            SET
                buyer_type = COALESCE(?, buyer_type),
                buyer_location = COALESCE(?, buyer_location)
            WHERE buyer_id = ?
            """,
            (
                buyer_type,
                buyer_location,
                buyer_id,
            ),
        )

        conn.commit()

        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
def assign_buyer_to_market_listing(listing_id, buyer_id):
    """
    Assigns a buyer to a market listing.

    The listing is automatically changed to RESERVED.
    """

    conn = get_connection()

    try:

        # Verify buyer exists
        buyer = conn.execute(
            """
            SELECT buyer_id
            FROM buyers
            WHERE buyer_id = ?
            """,
            (buyer_id,)
        ).fetchone()

        if buyer is None:
            raise ValueError("Buyer does not exist.")

        # Verify listing exists
        listing = conn.execute(
            """
            SELECT listing_id
            FROM market_listings
            WHERE listing_id = ?
            """,
            (listing_id,)
        ).fetchone()

        if listing is None:
            raise ValueError("Market listing does not exist.")

        conn.execute(
            """
            UPDATE market_listings
            SET buyer_id = ?,
                listing_status = 'RESERVED'
            WHERE listing_id = ?
            """,
            (buyer_id, listing_id)
        )

        conn.commit()

        return listing_id

    finally:
        conn.close()
def get_marketplace_statistics():
    """
    Returns overall marketplace statistics.
    """

    conn = get_connection()

    try:

        total = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM market_listings
            """
        ).fetchone()["count"]

        available = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM market_listings
            WHERE listing_status = 'AVAILABLE'
            """
        ).fetchone()["count"]

        reserved = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM market_listings
            WHERE listing_status = 'RESERVED'
            """
        ).fetchone()["count"]

        sold = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM market_listings
            WHERE listing_status = 'SOLD'
            """
        ).fetchone()["count"]

        closed = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM market_listings
            WHERE listing_status = 'CLOSED'
            """
        ).fetchone()["count"]

        total_quantity = conn.execute(
            """
            SELECT COALESCE(SUM(quantity_available_kg), 0)
            FROM market_listings
            WHERE listing_status = 'AVAILABLE'
            """
        ).fetchone()[0]

        return {
            "total_listings": total,
            "available": available,
            "reserved": reserved,
            "sold": sold,
            "closed": closed,
            "available_quantity_kg": total_quantity,
        }

    finally:
        conn.close()
# ============================================================
# PREDICTION MANAGEMENT
# ============================================================

def add_prediction(
    produce_id: int,
    input_method: str,
    total_shelf_life_days: float,
    current_storage_days: float,
    user_id: int,
    confidence_note: str = None,
):
    """
    Save a shelf-life prediction for a produce item.

    Returns:
        prediction_id if successful
        None if the produce or user does not exist
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT produce_id
            FROM produce
            WHERE produce_id = ?
              AND active = 1
            """,
            (produce_id,),
        )

        if cursor.fetchone() is None:
            return None

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE user_id = ?
            """,
            (user_id,),
        )

        if cursor.fetchone() is None:
            return None

        if total_shelf_life_days is None or total_shelf_life_days < 0:
            raise ValueError("Total shelf life must be non-negative.")

        if current_storage_days is None or current_storage_days < 0:
            raise ValueError("Current storage days must be non-negative.")

        remaining_shelf_life_days = max(
            total_shelf_life_days - current_storage_days,
            0,
        )

        cursor.execute(
            """
            INSERT INTO predictions (
                produce_id,
                input_method,
                total_shelf_life_days,
                current_storage_days,
                remaining_shelf_life_days,
                user_id,
                confidence_note
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                produce_id,
                input_method,
                total_shelf_life_days,
                current_storage_days,
                remaining_shelf_life_days,
                user_id,
                confidence_note,
            ),
        )

        prediction_id = cursor.lastrowid
        conn.commit()

        return prediction_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_prediction(prediction_id: int):
    """
    Retrieve a prediction together with the user and produce details.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                p.prediction_id,
                p.produce_id,
                pr.name AS produce_name,
                p.input_method,
                p.total_shelf_life_days,
                p.current_storage_days,
                p.remaining_shelf_life_days,
                p.user_id,
                u.full_name,
                p.confidence_note,
                p.created_at

            FROM predictions p

            INNER JOIN produce pr
                ON p.produce_id = pr.produce_id

            INNER JOIN users u
                ON p.user_id = u.user_id

            WHERE p.prediction_id = ?
            """,
            (prediction_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        conn.close()

    if current_storage_days < 0:
        raise ValueError(
            "Current storage days cannot be negative."
        )

    if input_method is None or not input_method.strip():
        raise ValueError(
            "Input method is required."
        )

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Verify produce exists
        cursor.execute(
            """
            SELECT produce_id
            FROM produce
            WHERE produce_id = ?
            AND active = 1
            """,
            (produce_id,),
        )

        produce = cursor.fetchone()

        if produce is None:
            raise ValueError(
                "Selected produce does not exist."
            )

        # Verify user if supplied
        if user_id is not None:

            cursor.execute(
                """
                SELECT user_id
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            )

            user = cursor.fetchone()

            if user is None:
                raise ValueError(
                    "Selected user does not exist."
                )

        # Calculate remaining shelf life
        remaining_shelf_life_days = max(
            total_shelf_life_days - current_storage_days,
            0
        )

        cursor.execute(
            """
            INSERT INTO predictions (
                user_id,
                produce_id,
                input_method,
                total_shelf_life_days,
                current_storage_days,
                remaining_shelf_life_days,
                confidence_note
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                produce_id,
                input_method,
                total_shelf_life_days,
                current_storage_days,
                remaining_shelf_life_days,
                confidence_note,
            ),
        )

        prediction_id = cursor.lastrowid

        conn.commit()

        return prediction_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_prediction(prediction_id: int):
    """
    Retrieve one prediction together with
    produce and user information.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                p.prediction_id,
                p.user_id,
                u.full_name,
                p.produce_id,
                pr.name AS produce_name,
                pr.category,
                p.prediction_date,
                p.input_method,
                p.total_shelf_life_days,
                p.current_storage_days,
                p.remaining_shelf_life_days,
                p.confidence_note

            FROM predictions p

            INNER JOIN produce pr
                ON p.produce_id = pr.produce_id

            LEFT JOIN users u
                ON p.user_id = u.user_id

            WHERE p.prediction_id = ?
            """,
            (prediction_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        conn.close()


def get_all_predictions():
    """
    Retrieve all shelf-life predictions.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                p.prediction_id,
                p.user_id,
                u.full_name,
                p.batch_id,
                p.produce_id,
                pr.name AS produce_name,
                p.prediction_date,
                p.input_method,
                p.total_shelf_life_days,
                p.current_storage_days,
                p.remaining_shelf_life_days,
                p.confidence_note

            FROM predictions p

            INNER JOIN produce pr
                ON p.produce_id = pr.produce_id

            LEFT JOIN users u
                ON p.user_id = u.user_id

            ORDER BY p.prediction_id DESC
            """
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()

def get_batch_predictions(batch_id: int, farmer_id: int = None):
    """
    Retrieve predictions for a batch.

    When farmer_id is provided, return records only if the batch
    belongs to that farmer and each prediction belongs to the
    batch owner's user account.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        query = """
            SELECT
                p.prediction_id,
                p.user_id,
                u.full_name,
                p.batch_id,
                p.produce_id,
                pr.name AS produce_name,
                p.prediction_date,
                p.input_method,
                p.total_shelf_life_days,
                p.current_storage_days,
                p.remaining_shelf_life_days,
                p.confidence_note
            FROM predictions p
            INNER JOIN produce_batches pb
                ON p.batch_id = pb.batch_id
            INNER JOIN farmers f
                ON pb.farmer_id = f.farmer_id
            INNER JOIN produce pr
                ON p.produce_id = pr.produce_id
            LEFT JOIN users u
                ON p.user_id = u.user_id
            WHERE p.batch_id = ?
        """

        params = [batch_id]

        if farmer_id is not None:
            query += """
                AND pb.farmer_id = ?
                AND p.user_id = f.user_id
            """
            params.append(farmer_id)

        query += " ORDER BY p.prediction_id DESC"

        cursor.execute(query, tuple(params))
        return [dict(row) for row in cursor.fetchall()]

    finally:
        conn.close()


def get_user_predictions(user_id: int):
    """
    Retrieve all predictions belonging to a user.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                p.prediction_id,
                p.user_id,
                u.full_name,
                p.produce_id,
                pr.name AS produce_name,
                p.prediction_date,
                p.input_method,
                p.total_shelf_life_days,
                p.current_storage_days,
                p.remaining_shelf_life_days,
                p.confidence_note

            FROM predictions p

            INNER JOIN produce pr
                ON p.produce_id = pr.produce_id

            LEFT JOIN users u
                ON p.user_id = u.user_id

            WHERE p.user_id = ?

            ORDER BY p.prediction_id DESC
            """,
            (user_id,),
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()
# ============================================================
# PREDICTION MANAGEMENT
# ============================================================

def save_prediction(
    produce_id: int,
    input_method: str,
    total_shelf_life_days: float,
    current_storage_days: float,
    remaining_shelf_life_days: float,
    user_id: Optional[int] = None,
    confidence_note: Optional[str] = None,
    batch_id: Optional[int] = None,
):
    """
    Save a shelf-life prediction.

    The prediction can be linked directly to a
    farmer's produce batch using batch_id.

    Returns:
        int: Newly created prediction ID.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO predictions (
                user_id,
                batch_id,
                produce_id,
                input_method,
                total_shelf_life_days,
                current_storage_days,
                remaining_shelf_life_days,
                confidence_note
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                batch_id,
                produce_id,
                input_method,
                total_shelf_life_days,
                current_storage_days,
                remaining_shelf_life_days,
                confidence_note,
            ),
        )

        prediction_id = cursor.lastrowid

        connection.commit()

        return prediction_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

# ============================================================
# RECOMMENDATION MANAGEMENT
# ============================================================

def add_recommendation(
    prediction_id: int,
    user_type: str,
    status: str,
    recommendation_text: str,
):
    """
    Save a recommendation associated with a prediction.

    Returns:
        recommendation_id if successful
    """

    if not user_type or not user_type.strip():
        raise ValueError(
            "User type is required."
        )

    if not status or not status.strip():
        raise ValueError(
            "Recommendation status is required."
        )

    if not recommendation_text or not recommendation_text.strip():
        raise ValueError(
            "Recommendation text is required."
        )

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Verify prediction exists
        cursor.execute(
            """
            SELECT prediction_id
            FROM predictions
            WHERE prediction_id = ?
            """,
            (prediction_id,),
        )

        prediction = cursor.fetchone()

        if prediction is None:
            raise ValueError(
                "Selected prediction does not exist."
            )

        cursor.execute(
            """
            INSERT INTO recommendations (
                prediction_id,
                user_type,
                status,
                recommendation_text
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                prediction_id,
                user_type,
                status,
                recommendation_text,
            ),
        )

        recommendation_id = cursor.lastrowid

        conn.commit()

        return recommendation_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_recommendation(recommendation_id: int):
    """
    Retrieve one recommendation together with
    prediction and produce information.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                r.recommendation_id,
                r.prediction_id,
                r.user_type,
                r.status,
                r.recommendation_text,
                r.created_at,
                p.produce_id,
                pr.name AS produce_name,
                p.total_shelf_life_days,
                p.remaining_shelf_life_days

            FROM recommendations r

            INNER JOIN predictions p
                ON r.prediction_id = p.prediction_id

            INNER JOIN produce pr
                ON p.produce_id = pr.produce_id

            WHERE r.recommendation_id = ?
            """,
            (recommendation_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        conn.close()


def get_prediction_recommendations(prediction_id: int):
    """
    Retrieve all recommendations associated
    with a specific prediction.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                recommendation_id,
                prediction_id,
                user_type,
                status,
                recommendation_text,
                created_at

            FROM recommendations

            WHERE prediction_id = ?

            ORDER BY recommendation_id DESC
            """,
            (prediction_id,),
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


def get_all_recommendations():
    """
    Retrieve all recommendations.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                r.recommendation_id,
                r.prediction_id,
                r.user_type,
                r.status,
                r.recommendation_text,
                r.created_at,
                pr.name AS produce_name

            FROM recommendations r

            INNER JOIN predictions p
                ON r.prediction_id = p.prediction_id

            INNER JOIN produce pr
                ON p.produce_id = pr.produce_id

            ORDER BY r.recommendation_id DESC
            """
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()

# ============================================================
# RECOMMENDATION MANAGEMENT
# ============================================================

def save_recommendation(
    prediction_id: int,
    user_type: str,
    status: str,
    recommendation_text: str,
):
    """
    Save a recommendation associated with a prediction.

    Returns:
        int: Newly created recommendation ID.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO recommendations (
            prediction_id,
            user_type,
            status,
            recommendation_text
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            prediction_id,
            user_type,
            status,
            recommendation_text,
        ),
    )

    recommendation_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return recommendation_id


# ============================================================
# HISTORY MANAGEMENT
# ============================================================

def add_prediction_history(
    prediction_id: int,
    produce_name: str,
    total_shelf_life_days: float,
    remaining_shelf_life_days: float,
    status: Optional[str] = None,
    user_id: Optional[int] = None,
):
    """Save a prediction history record."""

    return save_history(
        prediction_id=prediction_id,
        produce_name=produce_name,
        total_shelf_life_days=total_shelf_life_days,
        remaining_shelf_life_days=remaining_shelf_life_days,
        status=status,
        user_id=user_id,
    )


def get_prediction_history(history_id: int):
    """Retrieve one prediction history record with user information."""

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                h.history_id,
                h.user_id,
                u.full_name,
                h.prediction_id,
                h.produce_name,
                h.total_shelf_life_days,
                h.remaining_shelf_life_days,
                h.status,
                h.recorded_at
            FROM history h
            LEFT JOIN users u ON h.user_id = u.user_id
            WHERE h.history_id = ?
            """,
            (history_id,),
        )

        row = cursor.fetchone()
        return dict(row) if row is not None else None
    finally:
        connection.close()


def get_all_prediction_history():
    """Retrieve all prediction history records."""

    return get_history()

def save_history(
    prediction_id: int,
    produce_name: str,
    total_shelf_life_days: float,
    remaining_shelf_life_days: float,
    status: Optional[str] = None,
    user_id: Optional[int] = None,
):
    """
    Save a prediction into the user's historical records.

    Returns:
        int: Newly created history ID.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO history (
            user_id,
            prediction_id,
            produce_name,
            total_shelf_life_days,
            remaining_shelf_life_days,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            prediction_id,
            produce_name,
            total_shelf_life_days,
            remaining_shelf_life_days,
            status,
        ),
    )

    history_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return history_id


def get_history(user_id: Optional[int] = None):
    """
    Retrieve historical prediction records.

    The result is returned as a list of dictionaries so that
    the application does not depend on fragile tuple positions.

    If user_id is provided, only that user's records are returned.
    Otherwise, all records are returned.
    """

    connection = get_connection()
    cursor = connection.cursor()

    if user_id is None:

        cursor.execute(
            """
            SELECT
                h.history_id,
                h.user_id,
                h.prediction_id,
                h.produce_name,
                h.total_shelf_life_days,
                h.remaining_shelf_life_days,
                h.status,
                h.recorded_at,
                p.input_method,
                p.current_storage_days,
                p.confidence_note
            FROM history h
            LEFT JOIN predictions p
                ON h.prediction_id = p.prediction_id
            ORDER BY h.recorded_at DESC
            """
        )

    else:

        cursor.execute(
            """
            SELECT
                h.history_id,
                h.user_id,
                h.prediction_id,
                h.produce_name,
                h.total_shelf_life_days,
                h.remaining_shelf_life_days,
                h.status,
                h.recorded_at,
                p.input_method,
                p.current_storage_days,
                p.confidence_note
            FROM history h
            LEFT JOIN predictions p
                ON h.prediction_id = p.prediction_id
            WHERE h.user_id = ?
            ORDER BY h.recorded_at DESC
            """,
            (user_id,),
        )

    rows = cursor.fetchall()

    connection.close()

    history = []

    for row in rows:

        history.append(
            {
                "history_id": row[0],
                "user_id": row[1],
                "prediction_id": row[2],
                "produce_name": row[3],
                "total_shelf_life_days": row[4],
                "remaining_shelf_life_days": row[5],
                "status": row[6],
                "recorded_at": row[7],
                "input_method": row[8],
                "current_storage_days": row[9],
                "confidence_note": row[10],
            }
        )

    return history

    print()
    print("Produce Batch Management Test:")
    print("-" * 60)

    # --------------------------------------------------------
    # TEST PRODUCE BATCH REGISTRATION
    # --------------------------------------------------------

    test_batch_id = add_produce_batch(
        farmer_id=test_farmer_id,
        produce_id=1,
        quantity_kg=250.0,
        harvest_date="2026-09-30",
        initial_quality="GOOD",
        asking_price_per_kg=8.50,
        status="AVAILABLE",
    )

    print()
    print("Produce batch registered successfully!")
    print(f"Batch ID: {test_batch_id}")

    # --------------------------------------------------------
    # TEST BATCH RETRIEVAL
    # --------------------------------------------------------

    batch = get_produce_batch(test_batch_id)

    print()
    print("Registered Produce Batch:")
    print(f"Farmer: {batch['farmer_name']}")
    print(f"Produce: {batch['produce_name']}")
    print(f"Quantity: {batch['quantity_kg']} kg")
    print(f"Harvest Date: {batch['harvest_date']}")
    print(f"Initial Quality: {batch['initial_quality']}")
    print(f"Price: K{batch['asking_price_per_kg']:.2f}/kg")
    print(f"Status: {batch['status']}")

    # --------------------------------------------------------
    # TEST FARMER BATCHES
    # --------------------------------------------------------

    farmer_batches = get_farmer_batches(test_farmer_id)

    print()
    print(
        f"Total Batches for Farmer: "
        f"{len(farmer_batches)}"
    )

    print()
    print("Produce Batch Management is working correctly.")
# ============================================================
# DATABASE TEST
# ============================================================
# ============================================================
# FARMER DASHBOARD SUMMARY
# ============================================================

def get_farmer_dashboard(farmer_id: int):
    """
    Retrieve a complete dashboard summary for a farmer.

    Includes:
        - Farmer information
        - Latest produce batch
        - Latest quality record
        - Latest storage record
        - Latest prediction
        - Latest recommendation
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        # ----------------------------------------------------
        # 1. Farmer Information
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                f.farmer_id,
                f.user_id,
                u.full_name,
                u.phone,
                u.email,
                f.farm_name,
                f.farm_location,
                f.district,
                f.province

            FROM farmers f

            INNER JOIN users u
                ON f.user_id = u.user_id

            WHERE f.farmer_id = ?
            """,
            (farmer_id,),
        )

        farmer_row = cursor.fetchone()

        if farmer_row is None:
            return None

        farmer_info = dict(farmer_row)

        # ----------------------------------------------------
        # 2. Latest Produce Batch
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                pb.batch_id,
                pb.produce_id,
                p.name AS produce_name,
                p.category,
                pb.quantity_kg,
                pb.harvest_date,
                pb.initial_quality,
                pb.asking_price_per_kg,
                pb.status

            FROM produce_batches pb

            INNER JOIN produce p
                ON pb.produce_id = p.produce_id

            WHERE pb.farmer_id = ?

            ORDER BY pb.batch_id DESC

            LIMIT 1
            """,
            (farmer_id,),
        )

        batch_row = cursor.fetchone()

        batch_info = (
            dict(batch_row)
            if batch_row is not None
            else None
        )

        # ----------------------------------------------------
        # 3. Latest Quality Record
        # ----------------------------------------------------

        quality_info = None

        if batch_info is not None:

            cursor.execute(
                """
                SELECT
                    quality_id,
                    batch_id,
                    quality_score,
                    visual_status,
                    cv_confidence,
                    weight_loss_percent,
                    recorded_at

                FROM quality_records

                WHERE batch_id = ?

                ORDER BY quality_id DESC

                LIMIT 1
                """,
                (batch_info["batch_id"],),
            )

            quality_row = cursor.fetchone()

            if quality_row is not None:
                quality_info = dict(quality_row)

        # ----------------------------------------------------
        # 4. Latest Storage Record
        # ----------------------------------------------------

        storage_info = None

        if batch_info is not None:

            cursor.execute(
                """
                SELECT
                    storage_id,
                    batch_id,
                    temperature_c,
                    humidity_percent,
                    storage_days,
                    recorded_at

                FROM storage_records

                WHERE batch_id = ?

                ORDER BY storage_id DESC

                LIMIT 1
                """,
                (batch_info["batch_id"],),
            )

            storage_row = cursor.fetchone()

            if storage_row is not None:
                storage_info = dict(storage_row)

        # ----------------------------------------------------
        # 5. Latest Prediction
        # ----------------------------------------------------

        prediction_info = None

        if batch_info is not None:

            cursor.execute(
                """
                SELECT
                    p.prediction_id,
                    p.batch_id,
                    p.produce_id,
                    pr.name AS produce_name,
                    p.prediction_date,
                    p.input_method,
                    p.total_shelf_life_days,
                    p.current_storage_days,
                    p.remaining_shelf_life_days,
                    p.confidence_note

                FROM predictions p

                INNER JOIN produce pr
                    ON p.produce_id = pr.produce_id

                WHERE p.batch_id = ?

                ORDER BY p.prediction_id DESC

                LIMIT 1
                """,
                (batch_info["batch_id"],),
            )

            prediction_row = cursor.fetchone()

            if prediction_row is not None:
                prediction_info = dict(prediction_row)

        # ----------------------------------------------------
        # 6. Latest Recommendation
        # ----------------------------------------------------

        recommendation_info = None

        if prediction_info is not None:

            cursor.execute(
                """
                SELECT
                    recommendation_id,
                    prediction_id,
                    user_type,
                    status,
                    recommendation_text,
                    created_at

                FROM recommendations

                WHERE prediction_id = ?

                ORDER BY recommendation_id DESC

                LIMIT 1
                """,
                (prediction_info["prediction_id"],),
            )

            recommendation_row = cursor.fetchone()

            if recommendation_row is not None:
                recommendation_info = dict(
                    recommendation_row
                )

        # ----------------------------------------------------
        # 7. Dashboard Summary
        # ----------------------------------------------------

        return {
            "farmer": farmer_info,
            "batch": batch_info,
            "quality": quality_info,
            "storage": storage_info,
            "prediction": prediction_info,
            "recommendation": recommendation_info,
        }

    finally:
        conn.close()
# ============================================================
# CUSTOMER CAMERA ASSESSMENT MANAGEMENT
# ============================================================

def add_customer_camera_assessment(
    user_id: int,
    produce_id: int,
    predicted_class: str,
    model_probability: float = None,
    image_path: str = None,
):
    """
    Save an automatic customer camera assessment.

    The computer-vision model determines whether the
    produce is Fresh or Rotten.
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Verify customer/user exists
        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE user_id = ?
            """,
            (user_id,),
        )

        if cursor.fetchone() is None:
            raise ValueError("Customer does not exist.")

        # Verify produce exists
        cursor.execute(
            """
            SELECT produce_id
            FROM produce
            WHERE produce_id = ?
              AND active = 1
            """,
            (produce_id,),
        )

        if cursor.fetchone() is None:
            raise ValueError("Selected produce does not exist.")

        # Validate automatic model result
        if predicted_class not in ("Fresh", "Rotten"):
            raise ValueError(
                "Predicted class must be Fresh or Rotten."
            )

        # Validate confidence
        if model_probability is not None:
            if model_probability < 0 or model_probability > 1:
                raise ValueError(
                    "Model probability must be between 0 and 1."
                )

        cursor.execute(
            """
            INSERT INTO customer_camera_assessments (
                user_id,
                produce_id,
                predicted_class,
                model_probability,
                image_path
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                produce_id,
                predicted_class,
                model_probability,
                image_path,
            ),
        )

        assessment_id = cursor.lastrowid

        conn.commit()

        return assessment_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_all_customer_camera_assessments():
    """
    Retrieve all customer camera assessments for
    the Admin Dashboard.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                cca.assessment_id,
                cca.user_id,
                u.full_name AS customer_name,
                u.phone AS customer_phone,
                u.email AS customer_email,
                cca.produce_id,
                p.name AS produce_name,
                cca.predicted_class,
                cca.model_probability,
                cca.image_path,
                cca.created_at

            FROM customer_camera_assessments cca

            LEFT JOIN users u
                ON cca.user_id = u.user_id

            INNER JOIN produce p
                ON cca.produce_id = p.produce_id

            ORDER BY cca.assessment_id DESC
            """
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


# ============================================================
# ADMIN RECORD MANAGEMENT
# ============================================================

def delete_buyer(buyer_id: int):
    """
    Delete a buyer and linked login records safely.

    Buyers with marketplace listings or other dependent records
    are protected from deletion.

    Returns True when deleted, False when the buyer is not found.
    Raises ValueError when linked records prevent safe deletion.
    """

    conn = get_connection()

    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT user_id FROM buyers WHERE buyer_id = ?",
            (buyer_id,),
        )
        buyer = cursor.fetchone()

        if buyer is None:
            return False

        user_id = buyer["user_id"]

        cursor.execute(
            """
            SELECT listing_id
            FROM market_listings
            WHERE buyer_id = ?
            LIMIT 1
            """,
            (buyer_id,),
        )
        if cursor.fetchone() is not None:
            raise ValueError(
                "This buyer cannot be deleted because marketplace "
                "listings are linked to the buyer. Resolve those "
                "transactions first."
            )

        cursor.execute(
            """
            SELECT farmer_id FROM farmers WHERE user_id = ?
            UNION ALL
            SELECT listing_id FROM market_listings WHERE seller_id = ?
            UNION ALL
            SELECT prediction_id FROM predictions WHERE user_id = ?
            UNION ALL
            SELECT assessment_id
            FROM customer_camera_assessments
            WHERE user_id = ?
            LIMIT 1
            """,
            (user_id, user_id, user_id, user_id),
        )
        if cursor.fetchone() is not None:
            raise ValueError(
                "This buyer account has other linked records. "
                "The account was not deleted."
            )

        cursor.execute(
            "DELETE FROM user_credentials WHERE user_id = ?",
            (user_id,),
        )
        cursor.execute(
            "DELETE FROM buyers WHERE buyer_id = ?",
            (buyer_id,),
        )
        cursor.execute(
            "DELETE FROM users WHERE user_id = ?",
            (user_id,),
        )

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def delete_prediction(prediction_id: int):
    """
    Delete a prediction and its dependent history and recommendations.

    Returns True when deleted, False when the prediction is not found.
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT prediction_id FROM predictions WHERE prediction_id = ?",
            (prediction_id,),
        )
        if cursor.fetchone() is None:
            return False

        cursor.execute(
            "DELETE FROM recommendations WHERE prediction_id = ?",
            (prediction_id,),
        )
        cursor.execute(
            "DELETE FROM history WHERE prediction_id = ?",
            (prediction_id,),
        )
        cursor.execute(
            "DELETE FROM predictions WHERE prediction_id = ?",
            (prediction_id,),
        )

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def delete_customer_camera_assessment(assessment_id: int):
    """
    Delete one customer camera assessment without deleting the
    customer, produce type, or captured image file.

    Returns True when deleted, False when the assessment is not found.
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM customer_camera_assessments
            WHERE assessment_id = ?
            """,
            (assessment_id,),
        )

        deleted = cursor.rowcount > 0
        conn.commit()
        return deleted

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

