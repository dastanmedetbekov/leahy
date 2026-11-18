"""Embedded local REST API and Web GUI server for Leahe.

Zero external dependencies - built using Python's standard http.server.
Handles CORS for local development with Vite/Tauri, serves GUI static assets,
and provides complete REST API for the Leahe CBT database.
"""

import os
import json
import mimetypes
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from .database import Database
from .models import (
    MoodEntry,
    ActionItem,
    AntiProcrastinationTask,
    BehavioralExperiment,
    ExposureLadder,
    ExposureStep,
)
from .stats import calculate_summary_stats
from .cbt_data import COGNITIVE_DISTORTIONS, STANDARD_EMOTIONS

DEFAULT_PORT = 14200
GUI_DIST_PATH = Path(__file__).parent.parent.parent / "gui" / "dist"

def entry_to_dict(e: MoodEntry) -> Dict[str, Any]:
    return {
        "id": e.id,
        "timestamp": e.timestamp,
        "entry_type": e.entry_type,
        "initial_mood": e.initial_mood,
        "primary_emotion": e.primary_emotion,
        "emotion_intensity_initial": e.emotion_intensity_initial,
        "energy_level": e.energy_level,
        "situation": e.situation,
        "automatic_thought": e.automatic_thought,
        "belief_initial": e.belief_initial,
        "distortions": e.distortions,
        "evidence_for": e.evidence_for,
        "evidence_against": e.evidence_against,
        "alternative_thought": e.alternative_thought,
        "belief_final": e.belief_final,
        "final_mood": e.final_mood,
        "emotion_intensity_final": e.emotion_intensity_final,
        "action_plan": e.action_plan,
        "technique_used": e.technique_used,
        "technique_details": e.technique_details,
        "tags": e.tags,
        "notes": e.notes,
        "is_cbt": e.is_cbt,
        "mood_delta": e.mood_delta,
        "intensity_delta": e.intensity_delta,
    }

class LeaheApiHandler(BaseHTTPRequestHandler):
    db: Database = None
    dist_dir: Path = GUI_DIST_PATH

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, message: str, status: int = 400):
        self._send_json({"error": message, "status": status}, status=status)

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path.startswith("/api/"):
            self._handle_api_get(path, query)
        else:
            self._handle_static_get(path)

    def _handle_api_get(self, path: str, query: Dict[str, List[str]]):
        if path == "/api/status":
            entries_count = self.db.count_entries()
            self._send_json({
                "status": "ok",
                "app": "Leahe",
                "version": "1.0.0",
                "db_path": str(self.db.db_path),
                "entries_count": entries_count,
            })
            return

        if path == "/api/entries":
            limit = int(query.get("limit", [50])[0])
            offset = int(query.get("offset", [0])[0])
            entry_type = query.get("entry_type", [None])[0]
            distortion = query.get("distortion", [None])[0]
            search_query = query.get("q", [None])[0]

            entries = self.db.list_entries(
                limit=limit,
                offset=offset,
                entry_type=entry_type,
                distortion=distortion,
                query=search_query,
            )
            self._send_json({
                "entries": [entry_to_dict(e) for e in entries],
                "total": self.db.count_entries(),
            })
            return

        if path.startswith("/api/entries/"):
            try:
                entry_id = int(path.split("/")[-1])
                entry = self.db.get_entry(entry_id)
                if entry:
                    self._send_json(entry_to_dict(entry))
                else:
                    self._send_error("Entry not found", status=404)
            except ValueError:
                self._send_error("Invalid entry ID", status=400)
            return

        if path == "/api/stats":
            entries = self.db.get_all_entries()
            stats = calculate_summary_stats(entries)
            # Add experiment stats
            experiments = self.db.list_experiments()
            if experiments:
                completed = [e for e in experiments if e.is_completed]
                disconfirmed = [e for e in completed if e.fear_realized == 0]
                stats["experiments_total"] = len(experiments)
                stats["experiments_completed"] = len(completed)
                stats["disconfirmation_rate"] = (
                    (len(disconfirmed) / len(completed) * 100) if completed else 0.0
                )
            self._send_json(stats)
            return

        if path == "/api/distortions":
            distortions = [
                {
                    "code": d.code,
                    "name": d.name,
                    "summary": d.summary,
                    "description": d.description,
                    "example": d.example,
                    "challenge_questions": d.challenge_questions,
                }
                for d in COGNITIVE_DISTORTIONS.values()
            ]
            self._send_json(distortions)
            return

        if path == "/api/emotions":
            self._send_json(STANDARD_EMOTIONS)
            return

        if path == "/api/experiments":
            experiments = self.db.list_experiments()
            self._send_json([
                {
                    "id": exp.id,
                    "created_at": exp.created_at,
                    "title": exp.title,
                    "fear_prediction": exp.fear_prediction,
                    "predicted_belief": exp.predicted_belief,
                    "experiment_plan": exp.experiment_plan,
                    "actual_outcome": exp.actual_outcome,
                    "actual_severity": exp.actual_severity,
                    "fear_realized": exp.fear_realized,
                    "conclusion": exp.conclusion,
                    "status": exp.status,
                    "completed_at": exp.completed_at,
                    "notes": exp.notes,
                    "is_completed": exp.is_completed,
                    "fear_prediction_error": exp.fear_prediction_error,
                }
                for exp in experiments
            ])
            return

        if path == "/api/tasks":
            tasks = self.db.list_procrastination_tasks()
            self._send_json([
                {
                    "id": t.id,
                    "created_at": t.created_at,
                    "task_name": t.task_name,
                    "predicted_difficulty": t.predicted_difficulty,
                    "predicted_pleasure": t.predicted_pleasure,
                    "actual_difficulty": t.actual_difficulty,
                    "actual_pleasure": t.actual_pleasure,
                    "status": t.status,
                    "completed_at": t.completed_at,
                    "notes": t.notes,
                    "difficulty_delta": t.difficulty_delta,
                    "pleasure_delta": t.pleasure_delta,
                }
                for t in tasks
            ])
            return

        if path == "/api/ladders":
            ladders = self.db.list_exposure_ladders()
            res = []
            for l in ladders:
                steps = self.db.get_exposure_steps(l.id)
                res.append({
                    "id": l.id,
                    "created_at": l.created_at,
                    "fear_theme": l.fear_theme,
                    "notes": l.notes,
                    "steps": [
                        {
                            "id": s.id,
                            "ladder_id": s.ladder_id,
                            "step_order": s.step_order,
                            "description": s.description,
                            "target_suds": s.target_suds,
                            "repetitions_done": s.repetitions_done,
                            "last_pre_suds": s.last_pre_suds,
                            "last_post_suds": s.last_post_suds,
                            "status": s.status,
                            "completed_at": s.completed_at,
                            "notes": s.notes,
                            "is_mastered": s.is_mastered,
                            "suds_relief": s.suds_relief,
                        }
                        for s in steps
                    ],
                })
            self._send_json(res)
            return

        self._send_error("Endpoint not found", status=404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"
            payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception as e:
            self._send_error(f"Invalid JSON: {str(e)}", status=400)
            return

        if path == "/api/entries":
            try:
                entry = MoodEntry(
                    entry_type=payload.get("entry_type", "quick"),
                    initial_mood=int(payload.get("initial_mood", 5)),
                    primary_emotion=payload.get("primary_emotion", "Neutral"),
                    emotion_intensity_initial=int(payload.get("emotion_intensity_initial", 50)),
                    energy_level=int(payload["energy_level"]) if payload.get("energy_level") is not None else None,
                    situation=payload.get("situation"),
                    automatic_thought=payload.get("automatic_thought"),
                    belief_initial=int(payload["belief_initial"]) if payload.get("belief_initial") is not None else None,
                    distortions=payload.get("distortions", []),
                    evidence_for=payload.get("evidence_for"),
                    evidence_against=payload.get("evidence_against"),
                    alternative_thought=payload.get("alternative_thought"),
                    belief_final=int(payload["belief_final"]) if payload.get("belief_final") is not None else None,
                    final_mood=int(payload["final_mood"]) if payload.get("final_mood") is not None else None,
                    emotion_intensity_final=int(payload["emotion_intensity_final"]) if payload.get("emotion_intensity_final") is not None else None,
                    action_plan=payload.get("action_plan"),
                    technique_used=payload.get("technique_used"),
                    technique_details=payload.get("technique_details"),
                    tags=payload.get("tags", []),
                    notes=payload.get("notes"),
                )
                entry_id = self.db.save_entry(entry)
                entry.id = entry_id
                self._send_json(entry_to_dict(entry), status=201)
            except Exception as e:
                self._send_error(f"Error saving entry: {str(e)}", status=400)
            return

        if path == "/api/experiments":
            try:
                exp = BehavioralExperiment(
                    title=payload.get("title", "Behavioral Experiment"),
                    fear_prediction=payload.get("fear_prediction", ""),
                    predicted_belief=int(payload.get("predicted_belief", 80)),
                    experiment_plan=payload.get("experiment_plan", ""),
                    notes=payload.get("notes"),
                )
                exp_id = self.db.save_experiment(exp)
                exp.id = exp_id
                self._send_json({"id": exp_id, "status": "created"}, status=201)
            except Exception as e:
                self._send_error(f"Error saving experiment: {str(e)}", status=400)
            return

        if path.startswith("/api/experiments/") and path.endswith("/complete"):
            try:
                exp_id = int(path.split("/")[3])
                self.db.complete_experiment(
                    experiment_id=exp_id,
                    actual_outcome=payload.get("actual_outcome", ""),
                    actual_severity=int(payload.get("actual_severity", 0)),
                    fear_realized=bool(payload.get("fear_realized", False)),
                    conclusion=payload.get("conclusion", ""),
                )
                self._send_json({"status": "completed", "id": exp_id})
            except Exception as e:
                self._send_error(f"Error completing experiment: {str(e)}", status=400)
            return

        if path == "/api/tasks":
            try:
                task = AntiProcrastinationTask(
                    task_name=payload.get("task_name", ""),
                    predicted_difficulty=int(payload.get("predicted_difficulty", 50)),
                    predicted_pleasure=int(payload.get("predicted_pleasure", 50)),
                    notes=payload.get("notes"),
                )
                task_id = self.db.save_procrastination_task(task)
                self._send_json({"id": task_id, "status": "created"}, status=201)
            except Exception as e:
                self._send_error(f"Error saving task: {str(e)}", status=400)
            return

        if path.startswith("/api/tasks/") and path.endswith("/complete"):
            try:
                task_id = int(path.split("/")[3])
                self.db.complete_procrastination_task(
                    task_id=task_id,
                    actual_difficulty=int(payload.get("actual_difficulty", 50)),
                    actual_pleasure=int(payload.get("actual_pleasure", 50)),
                    notes=payload.get("notes"),
                )
                self._send_json({"status": "completed", "id": task_id})
            except Exception as e:
                self._send_error(f"Error completing task: {str(e)}", status=400)
            return

        if path == "/api/sync":
            try:
                from .notes import sync_notes_with_db
                stats = sync_notes_with_db(self.db, self.db.notes_dir)
                self._send_json({"status": "synced", "stats": stats})
            except Exception as e:
                self._send_error(f"Error syncing notes: {str(e)}", status=500)
            return

        self._send_error("Endpoint not found", status=404)

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/entries/"):
            try:
                entry_id = int(path.split("/")[-1])
                success = self.db.delete_entry(entry_id)
                if success:
                    self._send_json({"status": "deleted", "id": entry_id})
                else:
                    self._send_error("Entry not found", status=404)
            except ValueError:
                self._send_error("Invalid entry ID", status=400)
            return

        self._send_error("Endpoint not found", status=404)

    def _handle_static_get(self, path: str):
        if not self.dist_dir.exists():
            # If dist doesn't exist, show simple fallback status page
            msg = f"Leahe API Server is running. Dist not found at {self.dist_dir}. Access /api/status for API."
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(msg.encode("utf-8"))
            return

        clean_path = path.lstrip("/")
        if not clean_path:
            clean_path = "index.html"

        file_path = (self.dist_dir / clean_path).resolve()
        # Security check: ensure path is inside dist_dir
        if not str(file_path).startswith(str(self.dist_dir.resolve())):
            self.send_response(403)
            self.end_headers()
            return

        if not file_path.exists() or file_path.is_dir():
            # SPA fallback to index.html
            file_path = self.dist_dir / "index.html"

        if not file_path.exists():
            self.send_response(404)
            self.end_headers()
            return

        mime_type, _ = mimetypes.guess_type(str(file_path))
        mime_type = mime_type or "application/octet-stream"

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(len(content)))
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()

def run_server(db: Database, port: int = DEFAULT_PORT, host: str = "127.0.0.1") -> HTTPServer:
    LeaheApiHandler.db = db
    server = HTTPServer((host, port), LeaheApiHandler)
    return server
