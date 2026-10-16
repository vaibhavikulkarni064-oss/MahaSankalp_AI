from pathlib import Path
import sqlite3
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "database" / "krushirakshak.db"

@contextmanager
def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            district TEXT NOT NULL,
            preferred_language TEXT NOT NULL DEFAULT 'en' CHECK(preferred_language IN ('en','mr')),
            guest_id TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
        );
        CREATE INDEX IF NOT EXISTS idx_farmers_guest ON farmers(guest_id);
        CREATE TABLE IF NOT EXISTS crop_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER REFERENCES farmers(id) ON DELETE SET NULL,
            guest_id TEXT NOT NULL,
            district TEXT NOT NULL,
            soil_type TEXT NOT NULL,
            season TEXT NOT NULL,
            irrigation_type TEXT NOT NULL,
            water_availability TEXT NOT NULL,
            land_area REAL NOT NULL CHECK(land_area > 0),
            land_unit TEXT NOT NULL,
            crop_preference TEXT,
            constraints TEXT,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
        );
        CREATE INDEX IF NOT EXISTS idx_assessments_guest ON crop_assessments(guest_id, created_at);
        CREATE TABLE IF NOT EXISTS crop_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL REFERENCES crop_assessments(id) ON DELETE CASCADE,
            recommended_crops TEXT NOT NULL,
            explanation TEXT NOT NULL,
            limitations TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
        );
        CREATE TABLE IF NOT EXISTS crop_problem_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER REFERENCES farmers(id) ON DELETE SET NULL,
            guest_id TEXT NOT NULL,
            crop_name TEXT NOT NULL,
            growth_stage TEXT NOT NULL,
            symptoms TEXT NOT NULL,
            duration TEXT NOT NULL,
            possible_causes TEXT NOT NULL,
            guidance TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
        );
        CREATE INDEX IF NOT EXISTS idx_problems_guest ON crop_problem_reports(guest_id, created_at);
        CREATE TABLE IF NOT EXISTS irrigation_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER REFERENCES farmers(id) ON DELETE SET NULL,
            guest_id TEXT NOT NULL,
            crop_name TEXT NOT NULL,
            soil_type TEXT NOT NULL,
            growth_stage TEXT NOT NULL,
            irrigation_method TEXT NOT NULL,
            rainfall_input TEXT NOT NULL,
            water_availability TEXT NOT NULL,
            guidance TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
        );
        CREATE INDEX IF NOT EXISTS idx_irrigation_guest ON irrigation_reports(guest_id, created_at);
        """)
