import pytest
from pathlib import Path
from click.testing import CliRunner

from leahe.models import AntiProcrastinationTask
from leahe.database import Database
from leahe.notes import task_to_markdown, save_task_note_file, parse_markdown_with_frontmatter
from leahe.notifications import (
    generate_service_unit_content,
    generate_timer_unit_content,
    install_systemd_timer,
    get_systemd_timer_status,
    uninstall_systemd_timer,
    get_smart_reminder_content,
)
from leahe.cli import main


def test_pleasure_prediction_markdown_format(tmp_path: Path):
    notes_dir = tmp_path / "Notes"
    task = AntiProcrastinationTask(
        id=7,
        created_at="2026-11-17T22:30:00",
        task_name="Working on side project",
        predicted_difficulty=65,
        predicted_pleasure=30,
        status="pending",
        notes="Felt tired before starting",
    )

    # Test markdown generation
    md_text = task_to_markdown(task)
    assert md_text.startswith("---\n")
    fm, body = parse_markdown_with_frontmatter(md_text)
    assert fm["id"] == 7
    assert fm["type"] == "pleasure_prediction"
    assert fm["task_name"] == "Working on side project"
    assert fm["predicted_pleasure"] == 30
    assert fm["predicted_difficulty"] == 65
    assert fm["status"] == "pending"

    # Save to notes folder
    saved_file = save_task_note_file(task, notes_dir)
    assert saved_file.exists()
    assert "pleasure" in saved_file.name

    # Now mark completed and update markdown
    task.actual_pleasure = 80
    task.actual_difficulty = 25
    task.status = "completed"
    task.completed_at = "2026-11-17T23:15:00"
    task.notes = "Felt tired | Once started, got into deep flow and really enjoyed it!"

    updated_md = task_to_markdown(task)
    fm2, _ = parse_markdown_with_frontmatter(updated_md)
    assert fm2["status"] == "completed"
    assert fm2["actual_pleasure"] == 80
    assert fm2["pleasure_delta"] == 50
    assert fm2["difficulty_delta"] == 40
    assert "+50%" in updated_md
    assert "Easier by 40%" in updated_md


def test_cli_predict_and_complete_workflow(tmp_path: Path):
    db_file = tmp_path / "pleasure.db"
    notes_dir = tmp_path / "Notes"
    runner = CliRunner()

    # 1. Predict activity with flags
    pred_res = runner.invoke(main, [
        "--db", str(db_file),
        "--notes-dir", str(notes_dir),
        "predict", "Morning Exercise",
        "-p", "35",
        "-d", "70",
        "-n", "Did not feel like working out",
    ])
    assert pred_res.exit_code == 0
    assert "Activity #1 logged to Pleasure Prediction Sheet" in pred_res.output
    assert "Pleasure 35%" in pred_res.output
    assert "Difficulty 70%" in pred_res.output

    # Verify task note was saved in notes_dir
    note_files = list(notes_dir.glob("*-pleasure-*.md"))
    assert len(note_files) == 1
    content = note_files[0].read_text(encoding="utf-8")
    assert "Morning Exercise" in content
    assert "35%" in content

    # 2. Check tasks table shows pending task
    tasks_res = runner.invoke(main, ["--db", str(db_file), "tasks"], env={"COLUMNS": "120"})
    assert tasks_res.exit_code == 0
    assert "Morning Exercise" in tasks_res.output
    assert "PENDING" in tasks_res.output

    # 3. Complete activity and record reality
    comp_res = runner.invoke(main, [
        "--db", str(db_file),
        "--notes-dir", str(notes_dir),
        "complete", "1",
        "-p", "85",
        "-d", "20",
        "-n", "Endorphins kicked in, felt fantastic afterwards!",
    ])
    assert comp_res.exit_code == 0
    assert "Activity #1 marked completed" in comp_res.output
    assert "Predicted 35% -> Actual 85%" in comp_res.output
    assert "+50%" in comp_res.output
    assert "Easier by" in comp_res.output

    # Check updated markdown file in notes_dir
    updated_content = note_files[0].read_text(encoding="utf-8")
    assert "COMPLETED" in updated_content
    assert "85%" in updated_content

    # 4. Check tasks table shows completed activity with summary metrics
    tasks_done_res = runner.invoke(main, ["--db", str(db_file), "tasks", "--all"])
    assert tasks_done_res.exit_code == 0
    assert "COMPLETED" in tasks_done_res.output
    assert "Summary Analysis" in tasks_done_res.output
    assert "+50.0%" in tasks_done_res.output


def test_smart_reminder_pending_task(tmp_path: Path):
    db_file = tmp_path / "remind.db"
    db = Database(db_path=db_file, auto_sync_notes=False)

    task = AntiProcrastinationTask(
        task_name="Write research report",
        predicted_difficulty=80,
        predicted_pleasure=25,
        status="pending",
    )
    db.save_task(task)

    title, msg = get_smart_reminder_content(db)
    assert "Pleasure Prediction" in title
    assert "Write research report" in msg
    assert "25%" in msg


def test_systemd_unit_generation_and_lifecycle(tmp_path: Path):
    systemd_user_dir = tmp_path / "systemd" / "user"

    # Test generators
    svc_text = generate_service_unit_content(exec_cmd="/custom/bin/leahy notify")
    assert "ExecStart=/custom/bin/leahy notify" in svc_text
    assert "Type=oneshot" in svc_text

    timer_text = generate_timer_unit_content(schedule="*-*-* 09:00,18:00:00")
    assert "OnCalendar=*-*-* 09:00,18:00:00" in timer_text
    assert "Persistent=true" in timer_text

    # Test install to custom directory
    res = install_systemd_timer(schedule="*-*-* 09:00,18:00:00", custom_dir=systemd_user_dir, exec_cmd="/bin/true")
    assert res["service_path"].exists()
    assert res["timer_path"].exists()

    # Test status check
    status = get_systemd_timer_status(custom_dir=systemd_user_dir)
    assert status["installed"] is True
    assert status["schedule"] == "*-*-* 09:00,18:00:00"

    # Test uninstall
    un_res = uninstall_systemd_timer(custom_dir=systemd_user_dir)
    assert un_res["service_removed"] is True
    assert un_res["timer_removed"] is True
    assert not (systemd_user_dir / "leahy-reminder.service").exists()
    assert not (systemd_user_dir / "leahy-reminder.timer").exists()


def test_cli_systemd_commands(tmp_path: Path):
    runner = CliRunner()

    # Test systemd status when not installed
    st_res = runner.invoke(main, ["systemd", "status"])
    assert st_res.exit_code == 0
    assert "Systemd User Timer Status" in st_res.output

    # Test notify command in test mode
    notify_res = runner.invoke(main, ["notify", "--test"])
    assert notify_res.exit_code == 0
