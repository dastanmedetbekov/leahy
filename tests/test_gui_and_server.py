"""Tests for Leahe REST API server and new terminal commands."""

import json
import threading
import time
import urllib.request
import pytest
from click.testing import CliRunner

from leahe.database import Database
from leahe.models import MoodEntry
from leahe.server import run_server
from leahe.cli import main

@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_api.db"
    db = Database(db_path=db_file)
    entry = MoodEntry(
        entry_type="cbt_record",
        initial_mood=3,
        primary_emotion="Anxious",
        emotion_intensity_initial=80,
        situation="Test situation",
        automatic_thought="Everything will go wrong",
        distortions=["catastrophizing"],
        alternative_thought="Things usually turn out fine",
        final_mood=7,
        emotion_intensity_final=20,
    )
    db.save_entry(entry)
    return db

def test_api_server_endpoints(test_db):
    port = 14299
    server = run_server(test_db, port=port)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.3)

    try:
        # 1. Status
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/status") as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["status"] == "ok"
            assert data["app"] == "Leahe"
            assert data["entries_count"] == 1

        # 2. Entries
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/entries") as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert len(data["entries"]) == 1
            assert data["entries"][0]["automatic_thought"] == "Everything will go wrong"

        # 3. Stats
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/stats") as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["total_entries"] == 1
            assert data["avg_relief_percent"] == 60.0

        # 4. Distortions catalog
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/distortions") as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert len(data) >= 10

        # 5. POST new entry
        new_entry_payload = json.dumps({
            "entry_type": "quick",
            "initial_mood": 8,
            "primary_emotion": "Grateful",
            "emotion_intensity_initial": 85,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/entries",
            data=new_entry_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 201
            res_data = json.loads(resp.read().decode("utf-8"))
            assert res_data["primary_emotion"] == "Grateful"

        # Check total increased to 2
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/status") as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["entries_count"] == 2

        # 6. Tasks (GET, POST, COMPLETE)
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/tasks") as resp:
            tasks_data = json.loads(resp.read().decode("utf-8"))
            assert isinstance(tasks_data, list)
            assert len(tasks_data) == 0

        post_task_payload = json.dumps({
            "task_name": "Write documentation",
            "predicted_difficulty": 70,
            "predicted_pleasure": 30,
        }).encode("utf-8")
        req_task = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/tasks",
            data=post_task_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req_task) as resp:
            assert resp.status == 201
            task_res = json.loads(resp.read().decode("utf-8"))
            task_id = task_res["id"]

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/tasks") as resp:
            tasks_data = json.loads(resp.read().decode("utf-8"))
            assert len(tasks_data) == 1
            assert tasks_data[0]["task_name"] == "Write documentation"
            assert tasks_data[0]["status"] == "pending"

        complete_task_payload = json.dumps({
            "actual_difficulty": 40,
            "actual_pleasure": 80,
            "notes": "Was much easier than expected",
        }).encode("utf-8")
        req_complete_task = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/tasks/{task_id}/complete",
            data=complete_task_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req_complete_task) as resp:
            assert resp.status == 200
            comp_res = json.loads(resp.read().decode("utf-8"))
            assert comp_res["status"] == "completed"

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/tasks") as resp:
            tasks_data = json.loads(resp.read().decode("utf-8"))
            assert tasks_data[0]["status"] == "completed"
            assert tasks_data[0]["actual_difficulty"] == 40

        # 7. Experiments (GET, POST, COMPLETE)
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/experiments") as resp:
            exp_data = json.loads(resp.read().decode("utf-8"))
            assert isinstance(exp_data, list)

        post_exp_payload = json.dumps({
            "title": "Speak at meeting",
            "fear_prediction": "Everyone will laugh",
            "predicted_belief": 85,
            "experiment_plan": "Ask one question in the meeting",
        }).encode("utf-8")
        req_exp = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/experiments",
            data=post_exp_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req_exp) as resp:
            assert resp.status == 201
            exp_res = json.loads(resp.read().decode("utf-8"))
            exp_id = exp_res["id"]

        complete_exp_payload = json.dumps({
            "actual_outcome": "Nobody laughed, they answered politely",
            "actual_severity": 10,
            "fear_realized": False,
            "conclusion": "Catastrophe did not happen",
        }).encode("utf-8")
        req_complete_exp = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/experiments/{exp_id}/complete",
            data=complete_exp_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req_complete_exp) as resp:
            assert resp.status == 200
            comp_exp_res = json.loads(resp.read().decode("utf-8"))
            assert comp_exp_res["status"] == "completed"

        # 8. Ladders (GET)
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/ladders") as resp:
            ladders_data = json.loads(resp.read().decode("utf-8"))
            assert isinstance(ladders_data, list)

    finally:
        server.shutdown()

def test_cli_search_command(tmp_path):
    runner = CliRunner()
    db_file = tmp_path / "search_test.db"

    # Add demo data
    res = runner.invoke(main, ["--db", str(db_file), "seed-demo", "--count", "3"])
    assert res.exit_code == 0

    # Search for known scenario keyword
    res = runner.invoke(main, ["--db", str(db_file), "search", "presentation"])
    assert res.exit_code == 0
    assert "Found" in res.output or "No records" in res.output
