"""Export tools for CBT mood records (Markdown and JSON formats).

Strictly NO emojis.
"""

import json
from pathlib import Path
from typing import List
from .models import MoodEntry
from .cbt_data import COGNITIVE_DISTORTIONS
from .burns_methods import BURNS_METHODS

def export_to_json(entries: List[MoodEntry], file_path: Path) -> None:
    data = []
    for e in entries:
        data.append({
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
            "notes": e.notes,
        })
    file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def export_to_markdown(entries: List[MoodEntry], file_path: Path) -> None:
    lines = [
        "# CBT Mood & Thought Records Export",
        "",
        f"Total Records: {len(entries)}",
        "",
        "---",
        "",
    ]

    for e in entries:
        dt = e.parsed_datetime.strftime("%Y-%m-%d %H:%M")
        etype = "CBT Thought Record" if e.is_cbt else "Quick Mood Check-in"
        lines.append(f"## Entry #{e.id}: {dt} [{etype}]")
        lines.append("")
        lines.append(f"- **Initial Mood:** {e.initial_mood}/10")
        lines.append(f"- **Primary Emotion:** {e.primary_emotion} ({e.emotion_intensity_initial}%)")
        if e.energy_level is not None:
            lines.append(f"- **Energy Level:** {e.energy_level}/10")
        if e.situation:
            lines.append(f"- **Situation / Context:** {e.situation}")

        if e.is_cbt:
            if e.technique_used:
                t_name = BURNS_METHODS[e.technique_used].name if e.technique_used in BURNS_METHODS else e.technique_used
                lines.append(f"- **David Burns Method:** {t_name}")

            lines.append(f"- **Automatic Negative Thought (NAT):** \"{e.automatic_thought or 'N/A'}\" (Belief: {e.belief_initial}%)")

            if e.distortions:
                d_names = [f"{COGNITIVE_DISTORTIONS[d].name}" if d in COGNITIVE_DISTORTIONS else d for d in e.distortions]
                lines.append(f"- **Cognitive Distortions Identified:** {', '.join(d_names)}")

            if e.evidence_for:
                lines.append(f"- **Evidence Supporting:** {e.evidence_for}")
            if e.evidence_against:
                lines.append(f"- **Evidence Contradicting:** {e.evidence_against}")
            if e.alternative_thought:
                lines.append(f"- **Balanced Reframe:** \"{e.alternative_thought}\" (Belief: {e.belief_final}%)")

            if e.final_mood is not None:
                delta = e.final_mood - e.initial_mood
                delta_str = f"+{delta}" if delta > 0 else str(delta)
                lines.append(f"- **Post-CBT Mood:** {e.final_mood}/10 (Shift: {delta_str})")
            if e.emotion_intensity_final is not None:
                lines.append(f"- **Post-CBT Emotion Intensity:** {e.emotion_intensity_final}%")
            if e.action_plan:
                lines.append(f"- **Action Step:** {e.action_plan}")

        if e.notes:
            lines.append(f"- **Notes:** {e.notes}")

        lines.append("")
        lines.append("---")
        lines.append("")

    file_path.write_text("\n".join(lines), encoding="utf-8")
