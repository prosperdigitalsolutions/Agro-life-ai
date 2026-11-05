import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
DATABASE_FILE = PROJECT_ROOT / "database" / "agro_life_ai.db"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from database import database_manager as dm


class TestPredictionWorkflow(unittest.TestCase):
    """Safely test research-measurement validation using a database copy."""

    def setUp(self):
        if not DATABASE_FILE.exists():
            self.fail(
                f"Local SQLite database not found: {DATABASE_FILE}"
            )

        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_database = Path(self.temp_dir.name) / "test_agro_life_ai.db"
        shutil.copy2(DATABASE_FILE, self.test_database)

        self.original_database_path = dm.DATABASE_PATH
        self.original_get_connection = dm.get_connection
        dm.DATABASE_PATH = self.test_database

        def get_test_connection():
            conn = sqlite3.connect(str(self.test_database))
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

        dm.get_connection = get_test_connection

        conn = dm.get_connection()
        try:
            row = conn.execute(
                "SELECT MAX(batch_id) FROM produce_batches"
            ).fetchone()
            self.existing_batch_id = row[0] if row and row[0] is not None else None
            self.missing_batch_id = (
                (self.existing_batch_id or 0) + 100000
            )
        finally:
            conn.close()

    def tearDown(self):
        dm.get_connection = self.original_get_connection
        dm.DATABASE_PATH = self.original_database_path
        self.temp_dir.cleanup()

    def test_negative_day_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Day number cannot be negative"):
            dm.add_batch_research_measurement(
                1, -1, 1.0, 0.8
            )

    def test_negative_weight_loss_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Weight loss cannot be negative"):
            dm.add_batch_research_measurement(
                1, 4, -1.0, 0.8
            )

    def test_negative_acidity_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Titratable acidity cannot be negative"):
            dm.add_batch_research_measurement(
                1, 4, 1.0, -0.8
            )

    def test_nonexistent_batch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            dm.add_batch_research_measurement(
                self.missing_batch_id, 4, 1.0, 0.8
            )

    def test_valid_measurement_can_be_saved(self):
        if self.existing_batch_id is None:
            self.skipTest("No produce batch exists in the copied database.")

        measurement_id = dm.add_batch_research_measurement(
            self.existing_batch_id, 99999, 1.25, 0.85
        )

        self.assertIsNotNone(measurement_id)

        conn = dm.get_connection()
        try:
            row = conn.execute(
                """
                SELECT batch_id, day_number, weight_loss_percent,
                       titratable_acidity
                FROM batch_research_measurements
                WHERE measurement_id = ?
                """,
                (measurement_id,),
            ).fetchone()

            self.assertIsNotNone(row)
            self.assertEqual(row["batch_id"], self.existing_batch_id)
            self.assertEqual(row["day_number"], 99999)
            self.assertAlmostEqual(row["weight_loss_percent"], 1.25)
            self.assertAlmostEqual(row["titratable_acidity"], 0.85)
        finally:
            conn.close()

    def test_duplicate_batch_day_is_rejected(self):
        if self.existing_batch_id is None:
            self.skipTest("No produce batch exists in the copied database.")

        day_number = 99998

        dm.add_batch_research_measurement(
            self.existing_batch_id, day_number, 1.25, 0.85
        )

        with self.assertRaisesRegex(ValueError, "already exists"):
            dm.add_batch_research_measurement(
                self.existing_batch_id, day_number, 1.50, 0.80
            )


if __name__ == "__main__":
    unittest.main()
