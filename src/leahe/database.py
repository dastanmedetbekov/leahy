"""SQLite Database storage and queries for Leahe CBT Mood entries."""

import os
import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime

from .models import (
    MoodEntry,
    ActionItem,
    AntiProcrastinationTask,
    DASAssessment,
    BehavioralExperiment,
    ExposureStep,
    ExposureLadder,
)

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
    tags TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER,
    created_at TEXT NOT NULL,
    action_text TEXT NOT NULL,
    is_done INTEGER DEFAULT 0,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS anti_procrastination_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    task_name TEXT NOT NULL,
    predicted_difficulty INTEGER NOT NULL,
    predicted_pleasure INTEGER NOT NULL,
    actual_difficulty INTEGER,
    actual_pleasure INTEGER,
    status TEXT NOT NULL DEFAULT 'pending',
    completed_at TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS das_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    scores_json TEXT NOT NULL,
    total_score INTEGER NOT NULL,
    top_vulnerabilities TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS behavioral_experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    title TEXT NOT NULL,
    fear_prediction TEXT NOT NULL,
    predicted_belief INTEGER NOT NULL,
    experiment_plan TEXT NOT NULL,
    actual_outcome TEXT,
    actual_severity INTEGER,
    fear_realized INTEGER,
    conclusion TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    completed_at TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS exposure_ladders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    fear_theme TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS exposure_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ladder_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL,
    description TEXT NOT NULL,
    target_suds INTEGER NOT NULL,
    repetitions_done INTEGER DEFAULT 0,
    last_pre_suds INTEGER,
    last_post_suds INTEGER,
    status TEXT NOT NULL DEFAULT 'pending',
    completed_at TEXT,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_entries_timestamp ON entries(timestamp);
CREATE INDEX IF NOT EXISTS idx_entries_type ON entries(entry_type);
CREATE INDEX IF NOT EXISTS idx_entries_technique ON entries(technique_used);
CREATE INDEX IF NOT EXISTS idx_actions_status ON actions(is_done);
CREATE INDEX IF NOT EXISTS idx_procrastination_status ON anti_procrastination_tasks(status);
CREATE INDEX IF NOT EXISTS idx_exp_status ON behavioral_experiments(status);
CREATE INDEX IF NOT EXISTS idx_ladder_steps ON exposure_steps(ladder_id);
"""

class Database:
    def __init__(
        self,
        db_path: Optional[Path] = None,
        notes_dir: Optional[Path] = None,
        auto_sync_notes: bool = True,
    ):
        if db_path is None:
            env_path = os.getenv("LEAHE_DB") or os.getenv("CBT_MOOD_DB")
            if env_path:
                self.db_path = Path(env_path)
            else:
                self.db_path = DEFAULT_DB_PATH
        else:
            self.db_path = Path(db_path)

        self.notes_dir = notes_dir
        self.auto_sync_notes = auto_sync_notes

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
            if "tags" not in columns:
                cursor.execute("ALTER TABLE entries ADD COLUMN tags TEXT")
            conn.commit()

    def save_entry(self, entry: MoodEntry) -> int:
        query = """
        INSERT INTO entries (
            timestamp, entry_type, initial_mood, primary_emotion,
            emotion_intensity_initial, energy_level, situation,
            automatic_thought, belief_initial, distortions,
            evidence_for, evidence_against, alternative_thought,
            belief_final, final_mood, emotion_intensity_final,
            action_plan, technique_used, technique_details, tags, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        tags_json = json.dumps(entry.tags)
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
            tags_json,
            entry.notes,
        )
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            entry.id = cursor.lastrowid

            # Auto-create action item if action plan is specified
            if entry.action_plan and entry.action_plan.strip():
                try:
                    conn.execute(
                        "INSERT INTO actions (entry_id, created_at, action_text, is_done) VALUES (?, ?, ?, 0)",
                        (entry.id, entry.timestamp, entry.action_plan.strip()),
                    )
                    conn.commit()
                except Exception:
                    pass

            if self.auto_sync_notes:
                try:
                    from .notes import save_note_file
                    save_note_file(entry, self.notes_dir)
                except Exception:
                    pass

            return entry.id

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
            tags = ?,
            notes = ?
        WHERE id = ?
        """
        tags_json = json.dumps(entry.tags)
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
            tags_json,
            entry.notes,
            entry.id,
        )
        with self._get_connection() as conn:
            conn.execute(query, params)
            conn.commit()

        if self.auto_sync_notes:
            try:
                from .notes import save_note_file
                save_note_file(entry, self.notes_dir)
            except Exception:
                pass

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
            success = cursor.rowcount > 0

        if success and self.auto_sync_notes:
            try:
                from .notes import delete_note_file
                delete_note_file(entry_id, self.notes_dir)
            except Exception:
                pass

        return success

    def list_entries(
        self,
        limit: int = 50,
        offset: int = 0,
        entry_type: Optional[str] = None,
        distortion: Optional[str] = None,
        technique: Optional[str] = None,
        tag: Optional[str] = None,
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
        if tag:
            clean_tag = tag.lstrip("#").lower()
            conditions.append("lower(tags) LIKE ?")
            params.append(f'%"{clean_tag}"%')
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

    # --- Actions Management ---
    def save_action(self, action: ActionItem) -> int:
        query = "INSERT INTO actions (entry_id, created_at, action_text, is_done, completed_at) VALUES (?, ?, ?, ?, ?)"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                query,
                (action.entry_id, action.created_at, action.action_text, 1 if action.is_done else 0, action.completed_at),
            )
            conn.commit()
            action.id = cursor.lastrowid
            return cursor.lastrowid

    def list_actions(self, is_done: Optional[bool] = None) -> List[ActionItem]:
        query = "SELECT * FROM actions"
        params = []
        if is_done is not None:
            query += " WHERE is_done = ?"
            params.append(1 if is_done else 0)
        query += " ORDER BY is_done ASC, id DESC"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [ActionItem.from_row(dict(r)) for r in rows]

    def mark_action_done(self, action_id: int, done: bool = True) -> bool:
        completed_at = datetime.now().isoformat() if done else None
        query = "UPDATE actions SET is_done = ?, completed_at = ? WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (1 if done else 0, completed_at, action_id))
            conn.commit()
            return cursor.rowcount > 0

    # --- Anti-Procrastination Tasks Management ---
    def save_task(self, task: AntiProcrastinationTask) -> int:
        query = """
        INSERT INTO anti_procrastination_tasks (
            created_at, task_name, predicted_difficulty, predicted_pleasure,
            actual_difficulty, actual_pleasure, status, completed_at, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            task.created_at,
            task.task_name,
            task.predicted_difficulty,
            task.predicted_pleasure,
            task.actual_difficulty,
            task.actual_pleasure,
            task.status,
            task.completed_at,
            task.notes,
        )
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            task.id = cursor.lastrowid

            if self.auto_sync_notes:
                try:
                    from .notes import save_task_note_file
                    save_task_note_file(task, self.notes_dir)
                except Exception:
                    pass

            return cursor.lastrowid

    def update_task(self, task: AntiProcrastinationTask) -> None:
        if task.id is None:
            raise ValueError("Task has no ID to update")
        query = """
        UPDATE anti_procrastination_tasks SET
            task_name = ?,
            predicted_difficulty = ?,
            predicted_pleasure = ?,
            actual_difficulty = ?,
            actual_pleasure = ?,
            status = ?,
            completed_at = ?,
            notes = ?
        WHERE id = ?
        """
        params = (
            task.task_name,
            task.predicted_difficulty,
            task.predicted_pleasure,
            task.actual_difficulty,
            task.actual_pleasure,
            task.status,
            task.completed_at,
            task.notes,
            task.id,
        )
        with self._get_connection() as conn:
            conn.execute(query, params)
            conn.commit()

        if self.auto_sync_notes:
            try:
                from .notes import save_task_note_file
                save_task_note_file(task, self.notes_dir)
            except Exception:
                pass

    def get_task(self, task_id: int) -> Optional[AntiProcrastinationTask]:
        query = "SELECT * FROM anti_procrastination_tasks WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (task_id,))
            row = cursor.fetchone()
            if row:
                return AntiProcrastinationTask.from_row(dict(row))
        return None

    def list_tasks(self, status: Optional[str] = None) -> List[AntiProcrastinationTask]:
        query = "SELECT * FROM anti_procrastination_tasks"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY status ASC, id DESC"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [AntiProcrastinationTask.from_row(dict(r)) for r in rows]

    def complete_task(
        self,
        task_id: int,
        actual_difficulty: int = 50,
        actual_pleasure: int = 50,
        notes: Optional[str] = None,
    ) -> Optional[AntiProcrastinationTask]:
        task = self.get_task(task_id)
        if not task:
            return None
        task.actual_difficulty = actual_difficulty
        task.actual_pleasure = actual_pleasure
        task.status = "completed"
        task.completed_at = datetime.now().isoformat()
        if notes:
            task.notes = f"{task.notes or ''} | {notes}".strip(" | ")
        self.update_task(task)
        return task

    # Aliases for task management
    list_procrastination_tasks = list_tasks
    save_procrastination_task = save_task
    complete_procrastination_task = complete_task

    # --- DAS (Dysfunctional Attitude Scale) Assessments ---
    def save_das(self, assessment: DASAssessment) -> int:
        query = "INSERT INTO das_assessments (timestamp, scores_json, total_score, top_vulnerabilities, notes) VALUES (?, ?, ?, ?, ?)"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                query,
                (assessment.timestamp, assessment.scores_json, assessment.total_score, assessment.top_vulnerabilities, assessment.notes),
            )
            conn.commit()
            assessment.id = cursor.lastrowid
            return cursor.lastrowid

    def list_das(self) -> List[DASAssessment]:
        query = "SELECT * FROM das_assessments ORDER BY id DESC"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [DASAssessment.from_row(dict(r)) for r in rows]

    # --- Behavioral Experiments (Fear Testing) ---
    def save_experiment(self, exp: BehavioralExperiment) -> int:
        query = """
        INSERT INTO behavioral_experiments (
            created_at, title, fear_prediction, predicted_belief,
            experiment_plan, actual_outcome, actual_severity,
            fear_realized, conclusion, status, completed_at, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            exp.created_at,
            exp.title,
            exp.fear_prediction,
            exp.predicted_belief,
            exp.experiment_plan,
            exp.actual_outcome,
            exp.actual_severity,
            1 if exp.fear_realized else (0 if exp.fear_realized is not None else None),
            exp.conclusion,
            exp.status,
            exp.completed_at,
            exp.notes,
        )
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            exp.id = cursor.lastrowid

            if self.auto_sync_notes:
                try:
                    from .notes import save_experiment_note_file
                    save_experiment_note_file(exp, self.notes_dir)
                except Exception:
                    pass

            return exp.id

    def update_experiment(self, exp: BehavioralExperiment) -> None:
        if exp.id is None:
            raise ValueError("Experiment has no ID to update")
        query = """
        UPDATE behavioral_experiments SET
            title = ?,
            fear_prediction = ?,
            predicted_belief = ?,
            experiment_plan = ?,
            actual_outcome = ?,
            actual_severity = ?,
            fear_realized = ?,
            conclusion = ?,
            status = ?,
            completed_at = ?,
            notes = ?
        WHERE id = ?
        """
        params = (
            exp.title,
            exp.fear_prediction,
            exp.predicted_belief,
            exp.experiment_plan,
            exp.actual_outcome,
            exp.actual_severity,
            1 if exp.fear_realized else (0 if exp.fear_realized is not None else None),
            exp.conclusion,
            exp.status,
            exp.completed_at,
            exp.notes,
            exp.id,
        )
        with self._get_connection() as conn:
            conn.execute(query, params)
            conn.commit()

        if self.auto_sync_notes:
            try:
                from .notes import save_experiment_note_file
                save_experiment_note_file(exp, self.notes_dir)
            except Exception:
                pass

    def get_experiment(self, exp_id: int) -> Optional[BehavioralExperiment]:
        query = "SELECT * FROM behavioral_experiments WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (exp_id,))
            row = cursor.fetchone()
            if row:
                return BehavioralExperiment.from_row(dict(row))
        return None

    def list_experiments(self, status: Optional[str] = None) -> List[BehavioralExperiment]:
        query = "SELECT * FROM behavioral_experiments"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY id DESC"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [BehavioralExperiment.from_row(dict(r)) for r in rows]

    def delete_experiment(self, exp_id: int) -> bool:
        query = "DELETE FROM behavioral_experiments WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (exp_id,))
            conn.commit()
            return cursor.rowcount > 0

    def complete_experiment(
        self,
        experiment_id: int,
        actual_outcome: str,
        actual_severity: int = 0,
        fear_realized: bool = False,
        conclusion: str = "",
    ) -> Optional[BehavioralExperiment]:
        exp = self.get_experiment(experiment_id)
        if not exp:
            return None
        exp.actual_outcome = actual_outcome
        exp.actual_severity = actual_severity
        exp.fear_realized = 1 if fear_realized else 0
        exp.conclusion = conclusion
        exp.status = "completed"
        exp.completed_at = datetime.now().isoformat()
        self.update_experiment(exp)
        return exp

    # --- Exposure Ladders & Steps ---
    def save_ladder(self, ladder: ExposureLadder) -> int:
        query = "INSERT INTO exposure_ladders (created_at, fear_theme, notes) VALUES (?, ?, ?)"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (ladder.created_at, ladder.fear_theme, ladder.notes))
            conn.commit()
            ladder.id = cursor.lastrowid
            return ladder.id

    def get_ladder(self, ladder_id: int) -> Optional[ExposureLadder]:
        query = "SELECT * FROM exposure_ladders WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (ladder_id,))
            row = cursor.fetchone()
            if row:
                steps = self.list_exposure_steps(ladder_id=ladder_id)
                return ExposureLadder.from_row(dict(row), steps=steps)
        return None

    def list_ladders(self) -> List[ExposureLadder]:
        query = "SELECT * FROM exposure_ladders ORDER BY id DESC"
        ladders = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            for r in rows:
                ladder_id = r["id"]
                steps = self.list_exposure_steps(ladder_id=ladder_id)
                ladders.append(ExposureLadder.from_row(dict(r), steps=steps))
        return ladders

    def delete_ladder(self, ladder_id: int) -> bool:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM exposure_steps WHERE ladder_id = ?", (ladder_id,))
            cursor = conn.cursor()
            cursor.execute("DELETE FROM exposure_ladders WHERE id = ?", (ladder_id,))
            conn.commit()
            return cursor.rowcount > 0

    def save_exposure_step(self, step: ExposureStep) -> int:
        query = """
        INSERT INTO exposure_steps (
            ladder_id, step_order, description, target_suds,
            repetitions_done, last_pre_suds, last_post_suds,
            status, completed_at, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            step.ladder_id,
            step.step_order,
            step.description,
            step.target_suds,
            step.repetitions_done,
            step.last_pre_suds,
            step.last_post_suds,
            step.status,
            step.completed_at,
            step.notes,
        )
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            step.id = cursor.lastrowid
            return step.id

    def update_exposure_step(self, step: ExposureStep) -> None:
        if step.id is None:
            raise ValueError("Step has no ID to update")
        query = """
        UPDATE exposure_steps SET
            step_order = ?,
            description = ?,
            target_suds = ?,
            repetitions_done = ?,
            last_pre_suds = ?,
            last_post_suds = ?,
            status = ?,
            completed_at = ?,
            notes = ?
        WHERE id = ?
        """
        params = (
            step.step_order,
            step.description,
            step.target_suds,
            step.repetitions_done,
            step.last_pre_suds,
            step.last_post_suds,
            step.status,
            step.completed_at,
            step.notes,
            step.id,
        )
        with self._get_connection() as conn:
            conn.execute(query, params)
            conn.commit()

    def get_exposure_step(self, step_id: int) -> Optional[ExposureStep]:
        query = "SELECT * FROM exposure_steps WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (step_id,))
            row = cursor.fetchone()
            if row:
                return ExposureStep.from_row(dict(row))
        return None

    def list_exposure_steps(self, ladder_id: Optional[int] = None) -> List[ExposureStep]:
        query = "SELECT * FROM exposure_steps"
        params = []
        if ladder_id is not None:
            query += " WHERE ladder_id = ?"
            params.append(ladder_id)
        query += " ORDER BY target_suds ASC, step_order ASC"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [ExposureStep.from_row(dict(r)) for r in rows]

    def delete_exposure_step(self, step_id: int) -> bool:
        query = "DELETE FROM exposure_steps WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (step_id,))
            conn.commit()
            return cursor.rowcount > 0

    # Aliases for exposure ladder management
    list_exposure_ladders = list_ladders
    get_exposure_steps = list_exposure_steps

    # --- Backup & Restore ---
    def backup_all(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM entries")
            entries = [dict(r) for r in c.fetchall()]

            c.execute("SELECT * FROM actions")
            actions = [dict(r) for r in c.fetchall()]

            c.execute("SELECT * FROM anti_procrastination_tasks")
            tasks = [dict(r) for r in c.fetchall()]

            c.execute("SELECT * FROM das_assessments")
            das = [dict(r) for r in c.fetchall()]

            c.execute("SELECT * FROM behavioral_experiments")
            experiments = [dict(r) for r in c.fetchall()]

            c.execute("SELECT * FROM exposure_ladders")
            ladders = [dict(r) for r in c.fetchall()]

            c.execute("SELECT * FROM exposure_steps")
            steps = [dict(r) for r in c.fetchall()]

            return {
                "version": 1,
                "exported_at": datetime.now().isoformat(),
                "entries": entries,
                "actions": actions,
                "tasks": tasks,
                "das": das,
                "experiments": experiments,
                "ladders": ladders,
                "exposure_steps": steps,
            }

    def restore_all(self, data: Dict[str, Any]) -> Tuple[int, int, int, int]:
        entries_count = 0
        actions_count = 0
        tasks_count = 0
        das_count = 0

        with self._get_connection() as conn:
            # Insert entries
            for e in data.get("entries", []):
                e_copy = dict(e)
                e_copy.pop("id", None)
                keys = list(e_copy.keys())
                placeholders = ", ".join(["?"] * len(keys))
                sql = f"INSERT INTO entries ({', '.join(keys)}) VALUES ({placeholders})"
                conn.execute(sql, [e_copy[k] for k in keys])
                entries_count += 1

            for a in data.get("actions", []):
                a_copy = dict(a)
                a_copy.pop("id", None)
                keys = list(a_copy.keys())
                sql = f"INSERT INTO actions ({', '.join(keys)}) VALUES ({', '.join(['?']*len(keys))})"
                conn.execute(sql, [a_copy[k] for k in keys])
                actions_count += 1

            for t in data.get("tasks", []):
                t_copy = dict(t)
                t_copy.pop("id", None)
                keys = list(t_copy.keys())
                sql = f"INSERT INTO anti_procrastination_tasks ({', '.join(keys)}) VALUES ({', '.join(['?']*len(keys))})"
                conn.execute(sql, [t_copy[k] for k in keys])
                tasks_count += 1

            for d in data.get("das", []):
                d_copy = dict(d)
                d_copy.pop("id", None)
                keys = list(d_copy.keys())
                sql = f"INSERT INTO das_assessments ({', '.join(keys)}) VALUES ({', '.join(['?']*len(keys))})"
                conn.execute(sql, [d_copy[k] for k in keys])
                das_count += 1

            conn.commit()

        return entries_count, actions_count, tasks_count, das_count
