"""Tests for CBT Fear & Anxiety Mechanics.

Includes:
- Behavioral Experiments (empirical fear prediction vs reality, prediction error).
- Exposure Ladders (hierarchies, SUDS 0-100, habituation tracking).
- Decatastrophizing protocol (worst / best / likely / coping).
- Downward Arrow, Evidence validation, and Cognitive Defusion in CBT sessions.
- Categorized CLI Main Menu and command aliases.

Strictly NO emojis. Clean ASCII symbols only.
"""

from pathlib import Path
from click.testing import CliRunner
import pytest

from leahe.models import BehavioralExperiment, ExposureLadder, ExposureStep, ActionItem, MoodEntry
from leahe.database import Database
from leahe.notes import (
    experiment_to_markdown,
    save_experiment_note_file,
    parse_markdown_with_frontmatter,
)
from leahe.stats import calculate_experiment_stats
from leahe.notifications import get_smart_reminder_content
from leahe.cli import main


def test_behavioral_experiment_model_and_stats(tmp_path: Path):
    exp = BehavioralExperiment(
        id=1,
        title="Ask question in all-hands meeting",
        fear_prediction="Everyone will judge my question as stupid and laugh",
        predicted_belief=85,
        experiment_plan="Raise hand during Q&A and ask about the new API rollout",
    )
    assert not exp.is_completed
    assert exp.prediction_error is None

    # Mark completed
    exp.actual_outcome = "The VP praised the question and answered in detail. Nobody laughed."
    exp.fear_realized = False
    exp.actual_severity = 10
    exp.conclusion = "My anxiety overestimates social catastrophe. Speaking up was well-received."
    exp.status = "completed"

    assert exp.is_completed
    # prediction_error = 85 - 10 = 75
    assert exp.prediction_error == 75

    # Test experiment stats calculation
    stats = calculate_experiment_stats([exp])
    assert stats["total"] == 1
    assert stats["completed"] == 1
    assert stats["pending"] == 0
    assert stats["disproven_count"] == 1
    assert stats["disproven_rate"] == 100.0
    assert stats["avg_predicted_belief"] == 85.0
    assert stats["avg_actual_severity"] == 10.0
    assert stats["avg_prediction_gap"] == 75.0


def test_behavioral_experiment_markdown_and_notes(tmp_path: Path):
    notes_dir = tmp_path / "Notes"
    exp = BehavioralExperiment(
        id=42,
        created_at="2026-11-17T22:00:00",
        title="Approaching colleague for coffee",
        fear_prediction="They will give a cold rejection and avoid me",
        predicted_belief=80,
        experiment_plan="Ask if they want to grab espresso after standup",
    )

    # 1. Pending experiment markdown
    md_text = experiment_to_markdown(exp)
    assert md_text.startswith("---\n")
    fm, body = parse_markdown_with_frontmatter(md_text)
    assert fm["id"] == 42
    assert fm["type"] == "behavioral_experiment"
    assert fm["status"] == "pending"
    assert fm["predicted_belief"] == 80
    assert "Approaching colleague for coffee" in md_text

    saved_file = save_experiment_note_file(exp, notes_dir)
    assert saved_file.exists()
    assert "experiment" in saved_file.name

    # 2. Completed experiment markdown
    exp.actual_outcome = "They eagerly agreed and we talked about books for 20 minutes."
    exp.fear_realized = False
    exp.actual_severity = 0
    exp.conclusion = "People are friendly; my fear was 100% false alarm."
    exp.status = "completed"
    exp.completed_at = "2026-11-17T23:00:00"

    completed_md = experiment_to_markdown(exp)
    fm2, _ = parse_markdown_with_frontmatter(completed_md)
    assert fm2["status"] == "completed"
    assert fm2["prediction_error"] == 80
    assert "+80% better than feared" in completed_md


def test_database_experiment_crud(tmp_path: Path):
    db_file = tmp_path / "test_exp.db"
    db = Database(db_path=db_file, auto_sync_notes=False)

    exp = BehavioralExperiment(
        title="Public Speech Trial",
        fear_prediction="I will freeze and stumble",
        predicted_belief=90,
        experiment_plan="Speak for 2 minutes without slides",
    )
    exp_id = db.save_experiment(exp)
    assert exp_id == 1

    fetched = db.get_experiment(exp_id)
    assert fetched is not None
    assert fetched.title == "Public Speech Trial"
    assert fetched.predicted_belief == 90
    assert not fetched.is_completed

    # Update outcome
    fetched.actual_outcome = "Spoke smoothly, slight pause at 1 min."
    fetched.fear_realized = False
    fetched.actual_severity = 15
    fetched.conclusion = "Stumbling did not happen."
    fetched.status = "completed"
    db.update_experiment(fetched)

    updated = db.get_experiment(exp_id)
    assert updated.is_completed
    assert updated.prediction_error == 75

    all_exps = db.list_experiments()
    assert len(all_exps) == 1

    # Delete
    deleted = db.delete_experiment(exp_id)
    assert deleted
    assert db.get_experiment(exp_id) is None


def test_exposure_ladder_model_and_database(tmp_path: Path):
    db_file = tmp_path / "test_ladder.db"
    db = Database(db_path=db_file, auto_sync_notes=False)

    ladder = ExposureLadder(
        fear_theme="Agoraphobia & Crowded Places",
        notes="Gradual desensitization steps",
    )
    ladder_id = db.save_ladder(ladder)
    assert ladder_id == 1

    # Add steps
    step1 = ExposureStep(
        ladder_id=ladder_id,
        step_order=1,
        description="Walk to the corner grocery store alone",
        target_suds=35,
    )
    s1_id = db.save_exposure_step(step1)

    step2 = ExposureStep(
        ladder_id=ladder_id,
        step_order=2,
        description="Sit in busy cafe for 15 minutes",
        target_suds=65,
    )
    s2_id = db.save_exposure_step(step2)

    ladders = db.list_ladders()
    assert len(ladders) == 1
    assert len(ladders[0].steps) == 2

    # Practice step 2
    s2 = db.get_exposure_step(s2_id)
    assert s2.repetitions_done == 0
    assert s2.status == "pending"

    s2.last_pre_suds = 70
    s2.last_post_suds = 30
    s2.repetitions_done += 1
    s2.status = "in_progress"
    s2.notes = "Anxiety peaked at minute 4, then dropped substantially."
    db.update_exposure_step(s2)

    s2_updated = db.get_exposure_step(s2_id)
    assert s2_updated.repetitions_done == 1
    assert s2_updated.habituation_delta == 40  # 70 - 30
    assert s2_updated.status == "in_progress"

    # Mastery
    s2_updated.status = "mastered"
    db.update_exposure_step(s2_updated)
    assert db.get_exposure_step(s2_id).status == "mastered"


def test_cli_behavioral_experiment_workflow(tmp_path: Path):
    db_file = tmp_path / "cli_exp.db"
    notes_dir = tmp_path / "Notes"
    runner = CliRunner()

    # 1. Create new experiment with flags
    new_res = runner.invoke(main, [
        "--db", str(db_file),
        "--notes-dir", str(notes_dir),
        "experiment", "new", "Ask for code review clarification",
        "-f", "Reviewer will be annoyed and condescending",
        "-b", "80",
        "-p", "Send a short message asking for clarification on thread",
    ], env={"COLUMNS": "120"})
    assert new_res.exit_code == 0
    assert "Behavioral Experiment #1 created" in new_res.output
    assert "80%" in new_res.output

    # 2. Check list shows pending experiment
    list_res = runner.invoke(main, ["--db", str(db_file), "exp", "list"], env={"COLUMNS": "120"})
    assert list_res.exit_code == 0
    assert "Ask for code review clarification" in list_res.output
    assert "PENDING" in list_res.output

    # 3. Complete experiment
    comp_res = runner.invoke(main, [
        "--db", str(db_file),
        "--notes-dir", str(notes_dir),
        "experiment", "complete", "1",
        "-o", "Reviewer was helpful and provided code example immediately",
        "--not-realized",
        "-s", "5",
        "-c", "Asking questions is encouraged and welcomed",
    ], env={"COLUMNS": "120"})
    assert comp_res.exit_code == 0
    assert "Experiment #1 marked completed" in comp_res.output
    assert "+75% better" in comp_res.output

    # 4. Check stats displays experiments table and disconfirmation audit
    stats_res = runner.invoke(main, ["--db", str(db_file), "stats"], env={"COLUMNS": "120"})
    assert stats_res.exit_code == 0
    assert "BEHAVIORAL EXPERIMENTS LAB" in stats_res.output
    assert "Fear Disconfirmation Rate: 100.0%" in stats_res.output
    assert "+75.0%" in stats_res.output


def test_cli_exposure_ladder_workflow(tmp_path: Path):
    db_file = tmp_path / "cli_ladder.db"
    runner = CliRunner()

    # 1. Create ladder non-interactively
    new_res = runner.invoke(main, [
        "--db", str(db_file),
        "ladder", "new", "Fear of Heights / Balconies",
        "-n", "Overcoming elevator and balcony anxiety",
    ], env={"COLUMNS": "120"})
    assert new_res.exit_code == 0
    assert "Fear Hierarchy #1 created" in new_res.output

    # 2. Add steps
    add1 = runner.invoke(main, [
        "--db", str(db_file),
        "ladder", "add-step", "1", "Look out 3rd floor window",
        "--suds", "30",
    ], env={"COLUMNS": "120"})
    assert add1.exit_code == 0
    assert "Step #1 added to ladder #1" in add1.output

    add2 = runner.invoke(main, [
        "--db", str(db_file),
        "ladder", "add-step", "1", "Stand on 5th floor balcony for 2 minutes",
        "--suds", "70",
    ], env={"COLUMNS": "120"})
    assert add2.exit_code == 0
    assert "Step #2 added to ladder #1" in add2.output

    # 3. Practice step non-interactively
    practice_res = runner.invoke(main, [
        "--db", str(db_file),
        "ladder", "practice", "2",
        "--pre", "75",
        "--post", "35",
        "--notes", "Used slow breathing, anxiety dropped after 90 seconds",
    ], env={"COLUMNS": "120"})
    assert practice_res.exit_code == 0
    assert "Exposure Trial #1 recorded" in practice_res.output
    assert "Reduced by -40 SUDS points" in practice_res.output

    # 4. Show ladder using alias 'exposure'
    show_res = runner.invoke(main, ["--db", str(db_file), "exposure", "show", "1"], env={"COLUMNS": "120"})
    assert show_res.exit_code == 0
    assert "Fear Hierarchy #1: Fear of Heights / Balconies" in show_res.output
    assert "Look out 3rd floor window" in show_res.output
    assert "Stand on 5th floor balcony" in show_res.output
    assert "Relief: -40" in show_res.output


def test_cli_decatastrophize_session(tmp_path: Path):
    db_file = tmp_path / "cli_decat.db"
    runner = CliRunner()

    # Inputs for decatastrophizing:
    # 1. Situation: "Client requested an urgent video call"
    # 2. Initial fear (0-100%): "85"
    # 3. Worst case: "They fire us immediately and terminate the contract"
    # 4. Best case: "They want to expand the project and double our budget"
    # 5. Most realistic: "They have a few bug reports and want to clarify deployment timeline"
    # 6. Coping plan: "Listen calmly, take notes, answer honestly, follow up with action items"
    # 7. Final fear (0-100%): "25"
    inputs = "\n".join([
        "Client requested an urgent video call",
        "85",
        "They fire us immediately and terminate the contract",
        "They want to expand the project and double our budget",
        "They have a few bug reports and want to clarify deployment timeline",
        "Listen calmly, take notes, answer honestly, follow up with action items",
        "25",
    ])

    res = runner.invoke(main, ["--db", str(db_file), "decat"], input=inputs, env={"COLUMNS": "120"})
    assert res.exit_code == 0
    assert "DECATASTROPHIZING PROTOCOL" in res.output
    assert "Anxiety Relief: 85% -> 25% (Relief: -60%)" in res.output
    assert "Empowering Reframe:" in res.output

    # Verify entry in DB
    db = Database(db_path=db_file, auto_sync_notes=False)
    entries = db.get_all_entries()
    assert len(entries) == 1
    entry = entries[0]
    assert entry.technique_used == "what_if_decatastrophize"
    assert "Worst case" in entry.automatic_thought
    assert entry.final_mood == 8
    assert "Listen calmly" in entry.action_plan


def test_cbt_session_downward_arrow_evidence_defusion(tmp_path: Path):
    db_file = tmp_path / "cbt_advanced.db"
    runner = CliRunner()

    # CBT Session Inputs:
    # 1. Situation: "Failed a test exam"
    # 2. Initial mood (1-10): "3"
    # 3. Emotion category: "1" (Anxiety / Fear)
    # 4. Specific emotion: "1" (Anxious)
    # 5. Initial intensity: "80"
    # 6. Energy (1-10): "4"
    # 7. Automatic thought: "I can't grasp this material"
    # 8. Belief initial (0-100): "85"
    # 9. Downward arrow prompt: "y"
    # 10. Step 1: "I will fail the whole course"
    # 11. Step 2: "I will be kicked out"
    # 12. Step 3: "It means I am fundamentally incompetent"
    # 13. Distortions: sequential y/n for 11 distortions
    # 14. Strategy: "1" (Classic Evidence)
    # 15. Evidence For: "i don't think I can pass" (triggers clinical fact-check hint!)
    # 16. Refine hint prompt: "y"
    # 17. Refined evidence for: "I scored 60% on trial quiz."
    # 18. Evidence Against: "I passed all previous homework assignments."
    # 19. Alternative thought: "A test score is a feedback diagnostic, not a measure of my worth."
    # 20. Belief final (0-100): "80"
    # 21. Final mood (1-10): "7"
    # 22. Final intensity (0-100): "25"
    # 23. Action plan: "Review the missed questions tomorrow"
    # 24. Tags: "study,exam"
    inputs = "\n".join([
        "Failed a test exam",
        "3",
        "1",
        "1",
        "80",
        "4",
        "I can't grasp this material",
        "85",
        "y",
        "I will fail the whole course",
        "I will be kicked out",
        "It means I am fundamentally incompetent",
        # 11 distortion questions (all_or_nothing and catastrophizing = y, others = n)
        "y",  # all_or_nothing
        "n",  # overgeneralization
        "n",  # mental_filter
        "n",  # disqualifying_positive
        "n",  # jumping_mind_reading
        "n",  # jumping_fortune_telling
        "y",  # catastrophizing
        "n",  # emotional_reasoning
        "n",  # should_statements
        "n",  # labeling
        "n",  # personalization
        "1",
        "i don't think I can pass",
        "y",
        "I scored 60% on trial quiz.",
        "I passed all previous homework assignments.",
        "A test score is a feedback diagnostic, not a measure of my worth.",
        "80",
        "7",
        "25",
        "Review the missed questions tomorrow",
        "study,exam",
    ])

    res = runner.invoke(main, ["--db", str(db_file), "cbt"], input=inputs, env={"COLUMNS": "120"})
    assert res.exit_code == 0
    assert "DOWNWARD / VERTICAL ARROW TECHNIQUE" in res.output
    assert "Clinical Fact-Check Hint:" in res.output
    assert "STEP 9: COGNITIVE DEFUSION (ACT MINDFULNESS)" in res.output
    assert "I notice that I am having the thought that" in res.output

    # Verify DB entry
    db = Database(db_path=db_file, auto_sync_notes=False)
    entries = db.get_all_entries()
    assert len(entries) == 1
    assert "Core Schema: It means I am fundamentally incompetent" in entries[0].notes


def test_smart_reminder_experiment_and_actions(tmp_path: Path):
    db_file = tmp_path / "remind_fear.db"
    db = Database(db_path=db_file, auto_sync_notes=False)

    # 1. When experiment is pending
    exp = BehavioralExperiment(
        title="Phone Call Trial",
        fear_prediction="They will hang up on me",
        predicted_belief=75,
        experiment_plan="Make the call at 3 PM",
    )
    db.save_experiment(exp)

    title, msg = get_smart_reminder_content(db)
    assert "Behavioral Experiment Check" in title
    assert "Phone Call Trial" in msg
    assert "They will hang up on me" in msg

    # Complete experiment
    exp.actual_outcome = "Call went great."
    exp.fear_realized = False
    exp.actual_severity = 0
    exp.conclusion = "No hangup."
    exp.status = "completed"
    db.update_experiment(exp)

    # 2. When action item is pending
    action = ActionItem(action_text="Read 10 pages of CBT book")
    db.save_action(action)

    title2, msg2 = get_smart_reminder_content(db)
    assert "Action Commitment Follow-up" in title2
    assert "Read 10 pages of CBT book" in msg2


def test_main_menu_categories(tmp_path: Path):
    db_file = tmp_path / "menu.db"
    runner = CliRunner()

    # 1. Exit cleanly from main menu
    exit_res = runner.invoke(main, ["--db", str(db_file)], input="0\n")
    assert exit_res.exit_code == 0
    assert "Select Category:" in exit_res.output
    assert "Thought Records & Restructuring" in exit_res.output
    assert "Behavioral Experiments & Exposure" in exit_res.output
    assert "Pleasure Predicting & Action Steps" in exit_res.output
    assert "Clinical Stats, DAS & Retrospective" in exit_res.output
    assert "Notes & Sync (Markdown in ~/Notes & YAML)" in exit_res.output
    assert "Settings & Reference Guides" in exit_res.output
    assert "Goodbye." in exit_res.output

    # 2. Enter Category 2 (Fears & Exposure) and then Back (0)
    cat2_res = runner.invoke(main, ["--db", str(db_file)], input="2\n0\n")
    assert cat2_res.exit_code == 0
    assert "== Behavioral Experiments & Exposure ==" in cat2_res.output
    assert "New Behavioral Fear Experiment" in cat2_res.output
    assert "New Exposure Ladder" in cat2_res.output
