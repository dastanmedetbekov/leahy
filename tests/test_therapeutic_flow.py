"""Tests for prioritized clinical improvements:
- SOS & Grounding (Breathing, 5-4-3-2-1)
- Scaffolding & Socratic hints
- Action commitment accountability loop
- Positive Data Log (Win / Credit List)
"""

from pathlib import Path
from click.testing import CliRunner

from leahe.cli import main
from leahe.database import Database
from leahe.models import MoodEntry, ActionItem
from leahe.grounding import run_box_breathing, run_478_breathing, run_54321_grounding
from leahe.session import prompt_evidence_against, prompt_balanced_reframe

def test_breathing_execution():
    # Test that breathing routines run cleanly without exceptions
    run_box_breathing(cycles=1, phase_seconds=1)
    run_478_breathing(cycles=1)

def test_cli_breathe_and_ground():
    runner = CliRunner()
    
    # 1. Test 'breathe' command with 1 cycle
    res_breathe = runner.invoke(main, ["breathe", "--cycles", "1"])
    assert res_breathe.exit_code == 0
    assert "BOX BREATHING" in res_breathe.output

    # 2. Test 'breathe --relax' (4-7-8)
    res_relax = runner.invoke(main, ["breathe", "--relax", "--cycles", "1"])
    assert res_relax.exit_code == 0
    assert "4-7-8 RELAXATION BREATHING" in res_relax.output

    # 3. Test 'ground' command
    res_ground = runner.invoke(main, ["ground"], input="\n\n\n\nI am safe\n")
    assert res_ground.exit_code == 0
    assert "5-4-3-2-1 SENSORY GROUNDING" in res_ground.output
    assert "Grounded Anchor:" in res_ground.output

def test_cli_sos_flow(tmp_path: Path):
    db_file = tmp_path / "sos.db"
    runner = CliRunner()

    # SOS inputs:
    # 1. Initial distress: 85%
    # 2. Choice: 1 (Box breathing, will run)
    # 3. Post distress: 40%
    # 4. Transition to CBT: n
    inputs = "85\n1\n40\nn\n"
    res = runner.invoke(main, ["--db", str(db_file), "sos"], input=inputs)
    assert res.exit_code == 0
    assert "ACUTE DISTRESS FIRST-AID (SOS)" in res.output
    assert "Physiological First-Aid Complete!" in res.output
    assert "Distress: 85% -> 40%" in res.output

def test_positive_data_log_win(tmp_path: Path):
    db_file = tmp_path / "win.db"
    runner = CliRunner()

    # 1. Log a win directly via CLI flags
    res = runner.invoke(main, [
        "--db", str(db_file),
        "win",
        "Finished refactoring legacy code without getting discouraged",
        "-m", "8",
        "-t", "code,resilience",
    ])
    assert res.exit_code == 0
    assert "Win recorded in Positive Data Log!" in res.output
    assert "Finished refactoring legacy code" in res.output

    # Check DB
    db = Database(db_path=db_file, auto_sync_notes=False)
    entries = db.get_all_entries()
    assert len(entries) == 1
    assert entries[0].entry_type == "credit"
    assert entries[0].initial_mood == 8
    assert "resilience" in entries[0].tags

    # 2. Test alias 'credit'
    res_alias = runner.invoke(main, [
        "--db", str(db_file),
        "credit",
        "Said no to an unreasonable request calmly",
    ])
    assert res_alias.exit_code == 0
    assert "Win recorded in Positive Data Log!" in res_alias.output

def test_action_accountability_startup_flow(tmp_path: Path):
    db_file = tmp_path / "action_loop.db"
    db = Database(db_path=db_file, auto_sync_notes=False)

    # Save a pending action
    action = ActionItem(action_text="Take a 15-minute walk outside", entry_id=42)
    action_id = db.save_action(action)

    runner = CliRunner()

    # Launch main menu with action pending: answer 'y' to mark done, then '0' to exit menu
    res = runner.invoke(main, ["--db", str(db_file)], input="y\n0\n")
    assert res.exit_code == 0
    assert "Action Commitment Follow-up:" in res.output
    assert "Take a 15-minute walk outside" in res.output
    assert "Action #" + str(action_id) + " marked as completed" in res.output

    # Verify action is marked done in DB
    actions = db.list_actions()
    assert actions[0].is_done is True

def test_main_menu_persistent_loop(tmp_path: Path):
    db_file = tmp_path / "loop_test.db"
    db = Database(db_path=db_file, auto_sync_notes=False)
    # Add a sample entry so stats displays
    entry = MoodEntry(initial_mood=7, primary_emotion="Calm", emotion_intensity_initial=60)
    db.save_entry(entry)

    runner = CliRunner()

    # Inputs:
    # 1. Choose Category 4 (Stats & Retrospective)
    # 2. Choose option 1 (View Stats)
    # 3. Pause prompt: press Enter (\n) to return to main menu
    # 4. Main menu: press '0\n' to exit
    inputs = "4\n1\n\n0\n"
    res = runner.invoke(main, ["--db", str(db_file)], input=inputs)
    assert res.exit_code == 0
    # Output should contain stats
    assert "Overview Metrics" in res.output or "CBT Mood Analytics" in res.output
    # Output should show pause prompt and returning to menu
    assert "Press Enter to return to main menu" in res.output
    # Output should show Select Category a second time
    assert res.output.count("Select Category:") == 2
    assert "Goodbye." in res.output
