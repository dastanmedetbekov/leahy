from datetime import datetime, timedelta
from leahe.models import MoodEntry
from leahe.stats import calculate_summary_stats, render_ascii_bar_chart, render_mood_timeline

def test_calculate_summary_stats():
    now = datetime.now()
    entries = [
        MoodEntry(
            id=1,
            timestamp=(now - timedelta(days=2)).isoformat(),
            entry_type="quick",
            initial_mood=5,
            primary_emotion="Neutral",
            emotion_intensity_initial=50,
        ),
        MoodEntry(
            id=2,
            timestamp=(now - timedelta(days=1)).isoformat(),
            entry_type="cbt_record",
            initial_mood=3,
            primary_emotion="Anxious",
            emotion_intensity_initial=80,
            distortions=["catastrophizing", "all_or_nothing"],
            final_mood=7,
            emotion_intensity_final=30,
        ),
        MoodEntry(
            id=3,
            timestamp=now.isoformat(),
            entry_type="cbt_record",
            initial_mood=4,
            primary_emotion="Anxious",
            emotion_intensity_initial=70,
            distortions=["catastrophizing"],
            final_mood=6,
            emotion_intensity_final=40,
        ),
    ]

    stats = calculate_summary_stats(entries)
    assert stats["total_entries"] == 3
    assert stats["cbt_entries_count"] == 2
    assert stats["quick_entries_count"] == 1
    assert stats["avg_mood"] == 4.0
    assert stats["min_mood"] == 3
    assert stats["max_mood"] == 5

    # CBT metrics
    assert stats["avg_cbt_initial_mood"] == 3.5
    assert stats["avg_cbt_final_mood"] == 6.5
    assert stats["avg_mood_delta"] == 3.0
    assert stats["improvement_rate"] == 100.0
    assert stats["avg_relief_percent"] == 40.0

    # Distortions
    top_dist = stats["distortions"][0]
    assert top_dist["code"] == "catastrophizing"
    assert top_dist["count"] == 2

    # ASCII chart tests
    chart_rows = render_ascii_bar_chart([("Catastrophizing", 2, 100.0), ("All-or-Nothing", 1, 50.0)])
    assert len(chart_rows) == 2
    assert "#" in chart_rows[0]

    timeline_rows = render_mood_timeline(entries)
    assert len(timeline_rows) > 5
