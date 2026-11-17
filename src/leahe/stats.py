"""Detailed statistics calculation and ASCII visualization for CBT mood data."""

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from .models import MoodEntry
from .cbt_data import COGNITIVE_DISTORTIONS
from .burns_methods import BURNS_METHODS

def calculate_summary_stats(entries: List[MoodEntry]) -> Dict[str, Any]:
    if not entries:
        return {"total_entries": 0}

    total_count = len(entries)
    cbt_entries = [e for e in entries if e.is_cbt]
    quick_entries = [e for e in entries if not e.is_cbt]

    # Initial mood averages
    moods = [e.initial_mood for e in entries]
    avg_mood = sum(moods) / total_count
    min_mood = min(moods)
    max_mood = max(moods)

    # Mood brackets
    low_mood_count = sum(1 for m in moods if m <= 3)      # 1-3
    mid_mood_count = sum(1 for m in moods if 4 <= m <= 6)  # 4-6
    high_mood_count = sum(1 for m in moods if m >= 7)     # 7-10

    # CBT Efficacy metrics
    cbt_with_outcomes = [e for e in cbt_entries if e.final_mood is not None]
    cbt_count = len(cbt_entries)
    avg_cbt_initial_mood = (
        sum(e.initial_mood for e in cbt_with_outcomes) / len(cbt_with_outcomes)
        if cbt_with_outcomes else None
    )
    avg_cbt_final_mood = (
        sum(e.final_mood for e in cbt_with_outcomes) / len(cbt_with_outcomes)
        if cbt_with_outcomes else None
    )
    avg_mood_delta = (
        avg_cbt_final_mood - avg_cbt_initial_mood
        if (avg_cbt_initial_mood is not None and avg_cbt_final_mood is not None)
        else None
    )

    improved_count = sum(1 for e in cbt_with_outcomes if e.final_mood > e.initial_mood)
    unchanged_count = sum(1 for e in cbt_with_outcomes if e.final_mood == e.initial_mood)
    worsened_count = sum(1 for e in cbt_with_outcomes if e.final_mood < e.initial_mood)
    improvement_rate = (
        (improved_count / len(cbt_with_outcomes) * 100) if cbt_with_outcomes else 0.0
    )

    # Distress intensity metrics
    cbt_with_intensities = [
        e for e in cbt_entries
        if e.emotion_intensity_final is not None
    ]
    avg_intensity_initial = (
        sum(e.emotion_intensity_initial for e in cbt_with_intensities) / len(cbt_with_intensities)
        if cbt_with_intensities else None
    )
    avg_intensity_final = (
        sum(e.emotion_intensity_final for e in cbt_with_intensities) / len(cbt_with_intensities)
        if cbt_with_intensities else None
    )
    avg_relief_percent = (
        (avg_intensity_initial - avg_intensity_final)
        if (avg_intensity_initial is not None and avg_intensity_final is not None)
        else None
    )

    # Cognitive Distortions breakdown
    all_distortions = []
    distortion_moods = defaultdict(list)
    for e in cbt_entries:
        for d in e.distortions:
            all_distortions.append(d)
            distortion_moods[d].append(e.initial_mood)

    distortion_counts = Counter(all_distortions)
    distortion_stats = []
    for code, count in distortion_counts.most_common():
        name = COGNITIVE_DISTORTIONS.get(code, None)
        disp_name = name.name if name else code
        pct = (count / cbt_count * 100) if cbt_count > 0 else 0
        avg_dist_mood = sum(distortion_moods[code]) / len(distortion_moods[code])
        distortion_stats.append({
            "code": code,
            "name": disp_name,
            "count": count,
            "percentage": pct,
            "avg_initial_mood": avg_dist_mood,
        })

    # Emotion breakdown
    emotion_counts = Counter(e.primary_emotion for e in entries)
    emotion_intensities = defaultdict(list)
    for e in entries:
        emotion_intensities[e.primary_emotion].append(e.emotion_intensity_initial)

    emotion_stats = []
    for emotion, count in emotion_counts.most_common(8):
        avg_int = sum(emotion_intensities[emotion]) / len(emotion_intensities[emotion])
        emotion_stats.append({
            "emotion": emotion,
            "count": count,
            "percentage": (count / total_count * 100),
            "avg_intensity": avg_int,
        })

    # Burns Technique breakdown
    technique_counts = Counter(e.technique_used for e in cbt_entries if e.technique_used)
    technique_deltas = defaultdict(list)
    technique_reliefs = defaultdict(list)

    for e in cbt_entries:
        if e.technique_used:
            if e.mood_delta is not None:
                technique_deltas[e.technique_used].append(e.mood_delta)
            if e.intensity_delta is not None:
                technique_reliefs[e.technique_used].append(e.intensity_delta)

    technique_stats = []
    for code, count in technique_counts.most_common():
        name = BURNS_METHODS[code].name if code in BURNS_METHODS else (
            "Classic Evidence Examination" if code == "classic_evidence" else code
        )
        avg_delta = (
            sum(technique_deltas[code]) / len(technique_deltas[code])
            if technique_deltas[code] else 0.0
        )
        avg_relief = (
            sum(technique_reliefs[code]) / len(technique_reliefs[code])
            if technique_reliefs[code] else 0.0
        )
        technique_stats.append({
            "code": code,
            "name": name,
            "count": count,
            "avg_mood_delta": avg_delta,
            "avg_distress_relief": avg_relief,
        })

    # Streaks and Dates
    sorted_entries = sorted(entries, key=lambda x: x.parsed_datetime)
    first_date = sorted_entries[0].parsed_datetime.date()
    last_date = sorted_entries[-1].parsed_datetime.date()
    days_span = (last_date - first_date).days + 1

    current_streak, longest_streak = _calculate_streaks(sorted_entries)

    return {
        "total_entries": total_count,
        "cbt_entries_count": cbt_count,
        "quick_entries_count": len(quick_entries),
        "avg_mood": avg_mood,
        "min_mood": min_mood,
        "max_mood": max_mood,
        "low_mood_count": low_mood_count,
        "mid_mood_count": mid_mood_count,
        "high_mood_count": high_mood_count,
        "cbt_with_outcomes": len(cbt_with_outcomes),
        "avg_cbt_initial_mood": avg_cbt_initial_mood,
        "avg_cbt_final_mood": avg_cbt_final_mood,
        "avg_mood_delta": avg_mood_delta,
        "improved_count": improved_count,
        "unchanged_count": unchanged_count,
        "worsened_count": worsened_count,
        "improvement_rate": improvement_rate,
        "avg_intensity_initial": avg_intensity_initial,
        "avg_intensity_final": avg_intensity_final,
        "avg_relief_percent": avg_relief_percent,
        "distortions": distortion_stats,
        "emotions": emotion_stats,
        "techniques": technique_stats,
        "first_date": first_date.isoformat(),
        "last_date": last_date.isoformat(),
        "days_span": days_span,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
    }

def _calculate_streaks(sorted_entries: List[MoodEntry]) -> Tuple[int, int]:
    if not sorted_entries:
        return 0, 0

    dates = sorted(list({e.parsed_datetime.date() for e in sorted_entries}))
    if not dates:
        return 0, 0

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    # Current streak
    current_streak = 0
    if dates[-1] in (today, yesterday):
        check_date = dates[-1]
        idx = len(dates) - 1
        while idx >= 0 and dates[idx] == check_date:
            current_streak += 1
            check_date -= timedelta(days=1)
            idx -= 1

    # Longest streak
    longest_streak = 1
    curr = 1
    for i in range(1, len(dates)):
        if dates[i] == dates[i - 1] + timedelta(days=1):
            curr += 1
            if curr > longest_streak:
                longest_streak = curr
        else:
            curr = 1

    return current_streak, longest_streak

def render_ascii_bar_chart(items: List[Tuple[str, int, float]], max_width: int = 30) -> List[str]:
    """Generates ASCII horizontal bar chart rows for labels, values, and percentages.
    items: List of (label, count, percentage)
    """
    if not items:
        return ["  No data available."]

    max_count = max(item[1] for item in items) if items else 1
    max_label_len = max(len(item[0]) for item in items) if items else 10

    lines = []
    for label, count, pct in items:
        bar_len = int((count / max_count) * max_width) if max_count > 0 else 0
        bar = "#" * bar_len + "-" * (max_width - bar_len)
        lbl = label.ljust(max_label_len)
        lines.append(f"  {lbl} |{bar}| {count:>3} ({pct:>5.1f}%)")
    return lines

def render_mood_timeline(entries: List[MoodEntry], limit: int = 20) -> List[str]:
    """Renders an ASCII line/scatter plot showing recent mood scores (1-10 scale)."""
    if not entries:
        return ["  No entries available for timeline."]

    recent = sorted(entries, key=lambda x: x.parsed_datetime)[-limit:]
    chart_height = 10  # 1 to 10 scale
    lines = []

    lines.append("  Mood Scale (1 - 10)")
    lines.append("  " + "-" * (len(recent) * 4 + 8))

    for level in range(10, 0, -1):
        row_str = f"  {level:>2} | "
        for entry in recent:
            if entry.initial_mood == level:
                # Mark with 'o' or '*'
                if entry.is_cbt and entry.final_mood is not None:
                    row_str += " *  "
                else:
                    row_str += " o  "
            elif entry.final_mood == level and entry.is_cbt:
                row_str += " +  "
            else:
                row_str += " .  "
        lines.append(row_str)

    lines.append("     +" + "-" * (len(recent) * 4 + 2))
    # Time markers
    date_str = "       "
    for entry in recent:
        dt = entry.parsed_datetime
        date_str += f"{dt.strftime('%d/%m')[:4]} "
    lines.append(date_str)
    lines.append("  Legend: [o] Initial mood  [*] CBT pre-mood  [+] Post-CBT re-rate  [.] Empty")

    return lines
