import pytest
from pathlib import Path
from leahe.models import MoodEntry
from leahe.database import Database

def test_database_crud(tmp_path: Path):
    db_file = tmp_path / "test_leahe.db"
    db = Database(db_file)

    # 1. Insert Quick Entry
    entry1 = MoodEntry(
        entry_type="quick",
        initial_mood=7,
        primary_emotion="Calm",
        emotion_intensity_initial=40,
        energy_level=6,
        situation="Working on project",
        notes="All smooth",
    )
    id1 = db.save_entry(entry1)
    assert id1 is not None
    assert id1 > 0

    # 2. Insert CBT Entry
    entry2 = MoodEntry(
        entry_type="cbt_record",
        initial_mood=3,
        primary_emotion="Anxious",
        emotion_intensity_initial=80,
        energy_level=4,
        situation="Upcoming deadline",
        automatic_thought="I cannot finish this in time.",
        belief_initial=85,
        distortions=["catastrophizing", "jumping_fortune_telling"],
        evidence_for="Remaining tasks are complex",
        evidence_against="I have 3 full days and previously finished similar tasks in 1 day",
        alternative_thought="I have sufficient time if I break it down step-by-step.",
        belief_final=90,
        final_mood=7,
        emotion_intensity_final=30,
        action_plan="Outline the next 3 subtasks.",
    )
    id2 = db.save_entry(entry2)
    assert id2 > id1

    # 3. Read back
    fetched1 = db.get_entry(id1)
    assert fetched1 is not None
    assert fetched1.primary_emotion == "Calm"
    assert fetched1.initial_mood == 7
    assert fetched1.is_cbt is False

    fetched2 = db.get_entry(id2)
    assert fetched2 is not None
    assert fetched2.is_cbt is True
    assert fetched2.distortions == ["catastrophizing", "jumping_fortune_telling"]
    assert fetched2.mood_delta == 4  # 7 - 3
    assert fetched2.intensity_delta == 50  # 80 - 30

    # 4. List and filter
    all_entries = db.get_all_entries()
    assert len(all_entries) == 2

    cbt_only = db.list_entries(entry_type="cbt_record")
    assert len(cbt_only) == 1
    assert cbt_only[0].id == id2

    dist_filtered = db.list_entries(distortion="catastrophizing")
    assert len(dist_filtered) == 1
    assert dist_filtered[0].id == id2

    # 5. Delete
    deleted = db.delete_entry(id1)
    assert deleted is True
    assert db.get_entry(id1) is None
    assert db.count_entries() == 1
