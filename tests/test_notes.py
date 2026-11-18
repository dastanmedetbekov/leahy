import pytest
from pathlib import Path
from click.testing import CliRunner
import yaml

from leahe.models import MoodEntry
from leahe.database import Database
from leahe.notes import (
    entry_to_markdown,
    markdown_to_entry,
    save_note_file,
    delete_note_file,
    list_note_files,
    convert_md_file_to_yaml,
    convert_notes_to_yaml,
    convert_yaml_to_md,
    sync_notes_with_db,
    parse_markdown_with_frontmatter,
)
from leahe.cli import main


def test_markdown_with_yaml_frontmatter_roundtrip():
    entry = MoodEntry(
        id=42,
        timestamp="2026-11-17T20:00:00",
        entry_type="cbt_record",
        initial_mood=3,
        primary_emotion="Anxious",
        emotion_intensity_initial=80,
        energy_level=6,
        situation="Challenging code review",
        automatic_thought="I made mistakes so I am terrible at this",
        belief_initial=85,
        distortions=["all_or_nothing", "catastrophizing"],
        evidence_for="Found 2 bugs",
        evidence_against="Fixed them easily and PR was approved",
        alternative_thought="Bugs happen and catching them makes the system reliable",
        belief_final=90,
        final_mood=7,
        emotion_intensity_final=25,
        action_plan="Write unit tests for edge cases",
        technique_used="double_standard",
        tags=["coding", "review"],
        notes="Felt much lighter after reframing.",
    )

    md_text = entry_to_markdown(entry)

    # Verify YAML frontmatter is present and valid YAML
    assert md_text.startswith("---\n")
    fm, body = parse_markdown_with_frontmatter(md_text)
    assert fm["id"] == 42
    assert fm["type"] == "cbt_record"
    assert fm["initial_mood"] == 3
    assert fm["final_mood"] == 7
    assert fm["mood_shift"] == 4
    assert fm["primary_emotion"] == "Anxious"
    assert fm["emotion_intensity_initial"] == 80
    assert fm["relief_percent"] == 55
    assert "all_or_nothing" in fm["distortions"]
    assert "coding" in fm["tags"]

    # Verify Markdown sections are present
    assert "# Challenging code review" in md_text
    assert "## Automatic Negative Thought (NAT)" in md_text
    assert "## Cognitive Distortions Identified" in md_text
    assert "## Evidence For" in md_text
    assert "## Evidence Against" in md_text
    assert "## Rational Alternative Thought / Reframe" in md_text
    assert "## Action Step" in md_text

    # Parse back into MoodEntry
    reconstructed = markdown_to_entry(md_text)
    assert reconstructed.id == 42
    assert reconstructed.initial_mood == 3
    assert reconstructed.final_mood == 7
    assert reconstructed.primary_emotion == "Anxious"
    assert reconstructed.automatic_thought == "I made mistakes so I am terrible at this"
    assert reconstructed.alternative_thought == "Bugs happen and catching them makes the system reliable"
    assert reconstructed.action_plan == "Write unit tests for edge cases"
    assert reconstructed.tags == ["coding", "review"]


def test_save_and_list_note_files(tmp_path: Path):
    notes_dir = tmp_path / "Notes"
    entry = MoodEntry(
        id=1,
        timestamp="2026-11-17T21:00:00",
        entry_type="note",
        initial_mood=8,
        primary_emotion="Calm",
        situation="Evening Walk",
        notes="Walked through the park, quiet and peaceful.",
        tags=["walk", "evening"],
    )

    saved_file = save_note_file(entry, notes_dir)
    assert saved_file.exists()
    assert saved_file.suffix == ".md"
    assert "evening-walk" in saved_file.name

    notes = list_note_files(notes_dir)
    assert len(notes) == 1
    file_p, fm = notes[0]
    assert file_p == saved_file
    assert fm["id"] == 1
    assert fm["initial_mood"] == 8

    # Delete
    deleted = delete_note_file(1, notes_dir)
    assert deleted is True
    assert not saved_file.exists()
    assert len(list_note_files(notes_dir)) == 0


def test_convert_md_to_yaml_single_and_batch(tmp_path: Path):
    notes_dir = tmp_path / "Notes"
    yaml_out_dir = tmp_path / "YAML"

    entry1 = MoodEntry(
        id=1,
        timestamp="2026-11-17T10:00:00",
        entry_type="quick",
        initial_mood=7,
        primary_emotion="Energetic",
        situation="Morning Coffee",
    )
    entry2 = MoodEntry(
        id=2,
        timestamp="2026-11-17T14:00:00",
        entry_type="cbt_record",
        initial_mood=4,
        final_mood=8,
        primary_emotion="Stressed",
        situation="Meeting overload",
        automatic_thought="I cannot handle all these requests",
        alternative_thought="I can decline non-essential meetings and prioritize",
    )

    save_note_file(entry1, notes_dir)
    save_note_file(entry2, notes_dir)

    # 1. Convert to individual YAML files
    yaml_files = convert_notes_to_yaml(notes_dir, output_path=yaml_out_dir, single_file=False)
    assert len(yaml_files) == 2
    for yf in yaml_files:
        assert yf.exists()
        assert yf.suffix == ".yaml"
        parsed = yaml.safe_load(yf.read_text(encoding="utf-8"))
        assert isinstance(parsed, dict)
        assert "id" in parsed
        assert "initial_mood" in parsed

    # 2. Convert to a single combined YAML file
    combined_yaml_file = tmp_path / "all_notes.yaml"
    single_res = convert_notes_to_yaml(notes_dir, output_path=combined_yaml_file, single_file=True)
    assert len(single_res) == 1
    assert combined_yaml_file.exists()

    combined_data = yaml.safe_load(combined_yaml_file.read_text(encoding="utf-8"))
    assert isinstance(combined_data, list)
    assert len(combined_data) == 2
    ids = {item["id"] for item in combined_data}
    assert ids == {1, 2}

    # 3. Convert YAML back to Markdown (to-md)
    restored_notes_dir = tmp_path / "RestoredNotes"
    convert_yaml_to_md(combined_yaml_file, out_dir=restored_notes_dir)
    restored_mds = list(restored_notes_dir.glob("*.md"))
    assert len(restored_mds) == 2


def test_sync_notes_with_db(tmp_path: Path):
    db_file = tmp_path / "sync_test.db"
    notes_dir = tmp_path / "Notes"
    db = Database(db_path=db_file, notes_dir=notes_dir, auto_sync_notes=True)

    # Saving entry to DB automatically creates note file in notes_dir
    entry1 = MoodEntry(
        entry_type="cbt_record",
        initial_mood=5,
        primary_emotion="Neutral",
        situation="Sync test entry 1",
    )
    eid1 = db.save_entry(entry1)
    assert eid1 is not None

    note_files = list(notes_dir.glob("*.md"))
    assert len(note_files) == 1

    # Simulate user adding a new note directly into ~/Notes as a .md file
    custom_md_content = """---
timestamp: '2026-11-17T22:00:00'
type: note
initial_mood: 9
primary_emotion: Joy
tags: [offline, markdown]
---

# User Manual Note

Created directly in markdown folder without CLI!
"""
    manual_file = notes_dir / "2026-11-17-manual-offline.md"
    manual_file.write_text(custom_md_content, encoding="utf-8")

    # Run sync
    stats = sync_notes_with_db(db, notes_dir)
    assert stats["imported"] == 1

    all_entries = db.get_all_entries()
    assert len(all_entries) == 2
    imported_entry = next(e for e in all_entries if e.primary_emotion == "Joy")
    assert imported_entry.initial_mood == 9
    assert imported_entry.situation == "User Manual Note"


def test_cli_note_commands(tmp_path: Path):
    db_file = tmp_path / "cli_notes.db"
    notes_dir = tmp_path / "Notes"
    runner = CliRunner()

    # 1. 'leahe note' with flags
    res = runner.invoke(main, [
        "--db", str(db_file),
        "--notes-dir", str(notes_dir),
        "note", "Great walk",
        "--mood", "8",
        "--emotion", "Happy",
        "--intensity", "75",
        "--energy", "7",
        "--tags", "nature,relax",
        "--content", "Walked 5 miles, felt energetic.",
    ])
    assert res.exit_code == 0
    assert "saved" in res.output

    # Check that note was written to notes_dir
    md_notes = list(notes_dir.glob("*.md"))
    assert len(md_notes) == 1
    content = md_notes[0].read_text(encoding="utf-8")
    assert "Great walk" in content
    assert "nature" in content

    # 2. 'leahe notes' / 'leahe list-notes'
    list_res = runner.invoke(main, ["--notes-dir", str(notes_dir), "notes"])
    assert list_res.exit_code == 0
    assert "Great walk" in list_res.output
    assert "8/10" in list_res.output

    # 3. 'leahe to-yaml'
    yaml_out = tmp_path / "export_notes.yaml"
    conv_res = runner.invoke(main, ["--notes-dir", str(notes_dir), "to-yaml", "--output", str(yaml_out), "--single"])
    assert conv_res.exit_code == 0
    assert yaml_out.exists()
    yaml_data = yaml.safe_load(yaml_out.read_text(encoding="utf-8"))
    assert isinstance(yaml_data, list)
    assert len(yaml_data) == 1
    assert yaml_data[0]["situation"] == "Great walk"

    # 4. 'leahe export -f yaml'
    export_yaml_file = tmp_path / "db_export.yaml"
    exp_res = runner.invoke(main, ["--db", str(db_file), "export", "-f", "yaml", "-o", str(export_yaml_file)])
    assert exp_res.exit_code == 0
    assert export_yaml_file.exists()
    db_yaml_data = yaml.safe_load(export_yaml_file.read_text(encoding="utf-8"))
    assert isinstance(db_yaml_data, list)
    assert len(db_yaml_data) == 1
    assert db_yaml_data[0]["primary_emotion"] == "Happy"

    # 5. 'leahe sync'
    sync_res = runner.invoke(main, ["--db", str(db_file), "--notes-dir", str(notes_dir), "sync"])
    assert sync_res.exit_code == 0
    assert "Sync completed" in sync_res.output
