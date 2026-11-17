"""SQLite Database storage and queries for Leahe CBT Mood entries."""

import os
import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .models import MoodEntry

DEFAULT_DB_DIR = Path.home() / ".local" / "share" / "leahe"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "leahe.db"
FALLBACK_DB_PATH = Path("./data/leahe.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    entry_type TEXT NOT NULL,
    initial_mood INTEGER NOT NULL,
    primary_emotion TEXT NOT NULL,
    emotion_intensity_initial INTEGER NOT NULL,
    energy_level INTEGER,
    situation TEXT,
    automatic_thought TEXT,
    belief_initial INTEGER,
    distortions TEXT,
    evidence_for TEXT,
    evidence_against TEXT,
    alternative_thought TEXT,
    belief_final INTEGER,
    final_mood INTEGER,
    emotion_intensity_final INTEGER,
    action_plan TEXT,
    technique_used TEXT,
    technique_details TEXT,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_entries_timestamp ON entries(timestamp);
CREATE INDEX IF NOT EXISTS idx_entries_type ON entries(entry_type);
CREATE INDEX IF NOT EXISTS idx_entries_technique ON entries(technique_used);
"""

class Database:
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            env_path = os.getenv("LEAHE_DB") or os.getenv("CBT_MOOD_DB")
            if env_path:
                self.db_path = Path(env_path)
            else:
                self.db_path = DEFAULT_DB_PATH
        else:
            self.db_path = Path(db_path)

        self._ensure_dir()
        self._init_db()

    def _ensure_dir(self):
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Fallback to local ./data or /tmp if user home is read-only
            try:
                self.db_path = FALLBACK_DB_PATH
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
            except OSError:
                self.db_path = Path("/tmp/leahe/leahe.db")
                self.db_path.parent.mkdir(parents=True, exist_ok=True)


    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            # Automatic schema migration for existing databases
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(entries)")
            columns = [row["name"] for row in cursor.fetchall()]
            if "technique_used" not in columns:
                cursor.execute("ALTER TABLE entries ADD COLUMN technique_used TEXT")
            if "technique_details" not in columns:
                cursor.execute("ALTER TABLE entries ADD COLUMN technique_details TEXT")
            conn.commit()

    def save_entry(self, entry: MoodEntry) -> int:
        query = """
        INSERT INTO entries (
            timestamp, entry_type, initial_mood, primary_emotion,
            emotion_intensity_initial, energy_level, situation,
            automatic_thought, belief_initial, distortions,
            evidence_for, evidence_against, alternative_thought,
            belief_final, final_mood, emotion_intensity_final,
            action_plan, technique_used, technique_details, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            entry.timestamp,
            entry.entry_type,
            entry.initial_mood,
            entry.primary_emotion,
            entry.emotion_intensity_initial,
            entry.energy_level,
            entry.situation,
            entry.automatic_thought,
            entry.belief_initial,
            entry.distortions_as_json(),
            entry.evidence_for,
            entry.evidence_against,
            entry.alternative_thought,
            entry.belief_final,
            entry.final_mood,
            entry.emotion_intensity_final,
            entry.action_plan,
            entry.technique_used,
            entry.technique_details,
            entry.notes,
        )
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            entry.id = cursor.lastrowid
            return cursor.lastrowid

    def update_entry(self, entry: MoodEntry) -> None:
        if entry.id is None:
            raise ValueError("Entry has no ID to update")
        query = """
        UPDATE entries SET
            timestamp = ?,
            entry_type = ?,
            initial_mood = ?,
            primary_emotion = ?,
            emotion_intensity_initial = ?,
            energy_level = ?,
            situation = ?,
            automatic_thought = ?,
            belief_initial = ?,
            distortions = ?,
            evidence_for = ?,
            evidence_against = ?,
            alternative_thought = ?,
            belief_final = ?,
            final_mood = ?,
            emotion_intensity_final = ?,
            action_plan = ?,
            technique_used = ?,
            technique_details = ?,
            notes = ?
        WHERE id = ?
        """
        params = (
            entry.timestamp,
            entry.entry_type,
            entry.initial_mood,
            entry.primary_emotion,
            entry.emotion_intensity_initial,
            entry.energy_level,
            entry.situation,
            entry.automatic_thought,
            entry.belief_initial,
            entry.distortions_as_json(),
            entry.evidence_for,
            entry.evidence_against,
            entry.alternative_thought,
            entry.belief_final,
            entry.final_mood,
            entry.emotion_intensity_final,
            entry.action_plan,
            entry.technique_used,
            entry.technique_details,
            entry.notes,
            entry.id,
        )
        with self._get_connection() as conn:
            conn.execute(query, params)
            conn.commit()

    def get_entry(self, entry_id: int) -> Optional[MoodEntry]:
        query = "SELECT * FROM entries WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (entry_id,))
            row = cursor.fetchone()
            if row:
                return MoodEntry.from_row(dict(row))
        return None

    def delete_entry(self, entry_id: int) -> bool:
        query = "DELETE FROM entries WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (entry_id,))
            conn.commit()
            return cursor.rowcount > 0

    def list_entries(
        self,
        limit: int = 50,
        offset: int = 0,
        entry_type: Optional[str] = None,
        distortion: Optional[str] = None,
        technique: Optional[str] = None,
        min_mood: Optional[int] = None,
        max_mood: Optional[int] = None,
        query: Optional[str] = None,
    ) -> List[MoodEntry]:
        conditions = []
        params = []

        if entry_type:
            conditions.append("entry_type = ?")
            params.append(entry_type)
        if distortion:
            conditions.append("distortions LIKE ?")
            params.append(f'%"{distortion}"%')
        if technique:
            conditions.append("technique_used = ?")
            params.append(technique)
        if min_mood is not None:
            conditions.append("initial_mood >= ?")
            params.append(min_mood)
        if max_mood is not None:
            conditions.append("initial_mood <= ?")
            params.append(max_mood)
        if query:
            conditions.append(
                "(situation LIKE ? OR automatic_thought LIKE ? OR alternative_thought LIKE ? OR notes LIKE ?)"
            )
            wildcard = f"%{query}%"
            params.extend([wildcard, wildcard, wildcard, wildcard])

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        sql = f"SELECT * FROM entries{where_clause} ORDER BY timestamp DESC, id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [MoodEntry.from_row(dict(r)) for r in rows]

    def get_all_entries(self) -> List[MoodEntry]:
        sql = "SELECT * FROM entries ORDER BY timestamp ASC, id ASC"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [MoodEntry.from_row(dict(r)) for r in rows]

    def count_entries(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM entries")
            return cursor.fetchone()[0]
