"""Markdown note storage with YAML frontmatter and YAML conversion tools.

Strictly NO emojis. Clean ASCII formatting.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from .models import (
    MoodEntry,
    AntiProcrastinationTask,
    BehavioralExperiment,
    ExposureLadder,
    ExposureStep,
)
from .cbt_data import COGNITIVE_DISTORTIONS
from .burns_methods import BURNS_METHODS


def get_default_notes_dir() -> Path:
    """Return the default notes directory: ~/Notes or LEAHE_NOTES_DIR."""
    env_dir = os.getenv("LEAHE_NOTES_DIR")
    if env_dir:
        return Path(env_dir)
    return Path.home() / "Notes"


def ensure_notes_dir(notes_dir: Optional[Any] = None) -> Path:
    """Ensure notes directory exists, falling back to local fallback if home is read-only."""
    if notes_dir is not None:
        target = Path(notes_dir)
    else:
        target = get_default_notes_dir()

    try:
        target.mkdir(parents=True, exist_ok=True)
        return target
    except OSError:
        fallback = Path("./data/notes")
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def slugify(text: str, max_len: int = 40) -> str:
    """Create a safe filesystem-friendly slug from text."""
    if not text:
        return "entry"
    slug = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug[:max_len].strip("-") or "entry"


def entry_to_frontmatter_dict(entry: MoodEntry) -> Dict[str, Any]:
    """Convert MoodEntry metadata into a clean dictionary suitable for YAML frontmatter."""
    fm: Dict[str, Any] = {
        "id": entry.id,
        "timestamp": entry.timestamp,
        "type": entry.entry_type,
        "initial_mood": entry.initial_mood,
    }

    if entry.final_mood is not None:
        fm["final_mood"] = entry.final_mood
        fm["mood_shift"] = entry.final_mood - entry.initial_mood

    fm["primary_emotion"] = entry.primary_emotion
    fm["emotion_intensity_initial"] = entry.emotion_intensity_initial

    if entry.emotion_intensity_final is not None:
        fm["emotion_intensity_final"] = entry.emotion_intensity_final
        fm["relief_percent"] = entry.emotion_intensity_initial - entry.emotion_intensity_final

    if entry.energy_level is not None:
        fm["energy_level"] = entry.energy_level

    if entry.situation:
        fm["situation"] = entry.situation

    if entry.distortions:
        fm["distortions"] = entry.distortions

    if entry.technique_used:
        fm["technique"] = entry.technique_used

    if entry.tags:
        fm["tags"] = entry.tags

    return fm


def entry_to_markdown(entry: MoodEntry) -> str:
    """Generate Markdown text with clean YAML frontmatter from a MoodEntry."""
    fm_dict = entry_to_frontmatter_dict(entry)
    yaml_header = yaml.dump(fm_dict, sort_keys=False, allow_unicode=True).strip()

    title = entry.situation or f"Entry #{entry.id or 'New'}"
    date_str = entry.parsed_datetime.strftime("%Y-%m-%d %H:%M")

    lines = [
        "---",
        yaml_header,
        "---",
        "",
        f"# {title}",
        "",
        f"- **Date:** {date_str}",
        f"- **Entry Type:** {entry.entry_type}",
        f"- **Initial Mood:** {entry.initial_mood}/10",
        f"- **Primary Emotion:** {entry.primary_emotion} ({entry.emotion_intensity_initial}%)",
    ]

    if entry.final_mood is not None:
        shift = entry.final_mood - entry.initial_mood
        shift_str = f"+{shift}" if shift > 0 else str(shift)
        lines.append(f"- **Final Mood:** {entry.final_mood}/10 (Shift: {shift_str})")

    if entry.emotion_intensity_final is not None:
        relief = entry.emotion_intensity_initial - entry.emotion_intensity_final
        lines.append(f"- **Final Emotion Intensity:** {entry.emotion_intensity_final}% (Relief: {relief}%)")

    if entry.energy_level is not None:
        lines.append(f"- **Energy Level:** {entry.energy_level}/10")

    if entry.tags:
        lines.append(f"- **Tags:** {', '.join(f'#{t}' for t in entry.tags)}")

    lines.append("")

    if entry.situation:
        lines.extend([
            "## Situation / Trigger",
            "",
            entry.situation,
            "",
        ])

    if entry.automatic_thought:
        belief_str = f" (Belief: {entry.belief_initial}%)" if entry.belief_initial is not None else ""
        lines.extend([
            "## Automatic Negative Thought (NAT)",
            "",
            f"> \"{entry.automatic_thought}\"{belief_str}",
            "",
        ])

    if entry.distortions:
        lines.extend([
            "## Cognitive Distortions Identified",
            "",
        ])
        for code in entry.distortions:
            if code in COGNITIVE_DISTORTIONS:
                d = COGNITIVE_DISTORTIONS[code]
                lines.append(f"- **{d.name}**: {d.summary}")
            else:
                lines.append(f"- **{code}**")
        lines.append("")

    if entry.evidence_for:
        lines.extend([
            "## Evidence For",
            "",
            entry.evidence_for,
            "",
        ])

    if entry.evidence_against:
        lines.extend([
            "## Evidence Against",
            "",
            entry.evidence_against,
            "",
        ])

    if entry.alternative_thought:
        belief_str = f" (Belief: {entry.belief_final}%)" if entry.belief_final is not None else ""
        lines.extend([
            "## Rational Alternative Thought / Reframe",
            "",
            f"> \"{entry.alternative_thought}\"{belief_str}",
            "",
        ])

    if entry.technique_used:
        t_name = BURNS_METHODS[entry.technique_used].name if entry.technique_used in BURNS_METHODS else entry.technique_used
        lines.extend([
            "## Restructuring Technique",
            "",
            f"- **Method:** {t_name}",
        ])
        if entry.technique_details:
            lines.append(f"- **Details:** {entry.technique_details}")
        lines.append("")

    if entry.action_plan:
        lines.extend([
            "## Action Step",
            "",
            f"- [ ] {entry.action_plan}",
            "",
        ])

    if entry.notes:
        lines.extend([
            "## Reflection & Notes",
            "",
            entry.notes,
            "",
        ])

    return "\n".join(lines).strip() + "\n"


def parse_markdown_with_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Extract YAML frontmatter and body text from a Markdown string."""
    content = content.strip()
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()
            try:
                fm_data = yaml.safe_load(fm_text) or {}
                if isinstance(fm_data, dict):
                    return fm_data, body
            except Exception:
                pass
    return {}, content


def _clean_thought_text(raw_text: str) -> Tuple[str, Optional[int]]:
    """Clean markdown blockquote text and extract belief percentage if present."""
    cleaned = raw_text.strip()
    if cleaned.startswith(">"):
        cleaned = cleaned.lstrip(">").strip()

    belief = None
    belief_match = re.search(r"\(Belief:\s*(\d+)%\)", cleaned)
    if belief_match:
        try:
            belief = int(belief_match.group(1))
        except ValueError:
            pass
        cleaned = cleaned[:belief_match.start()].strip()

    cleaned = cleaned.strip('"\'')
    return cleaned, belief


def markdown_to_entry(content: str, filename: Optional[str] = None) -> MoodEntry:
    """Parse a Markdown document (with or without YAML frontmatter) into a MoodEntry."""
    fm, body = parse_markdown_with_frontmatter(content)

    entry_id = fm.get("id")
    timestamp = fm.get("timestamp")
    if not timestamp:
        timestamp = datetime.now().isoformat()

    entry_type = fm.get("type") or fm.get("entry_type") or "quick"
    initial_mood = int(fm.get("initial_mood") or fm.get("mood") or 5)
    final_mood = int(fm["final_mood"]) if fm.get("final_mood") is not None else None
    primary_emotion = fm.get("primary_emotion") or fm.get("emotion") or "Neutral"
    emotion_intensity_initial = int(fm.get("emotion_intensity_initial") or fm.get("intensity") or 50)
    emotion_intensity_final = int(fm["emotion_intensity_final"]) if fm.get("emotion_intensity_final") is not None else None
    energy_level = int(fm["energy_level"]) if fm.get("energy_level") is not None else None
    distortions = fm.get("distortions") or []
    if isinstance(distortions, str):
        distortions = [d.strip() for d in distortions.split(",") if d.strip()]
    tags = fm.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip().lstrip("#") for t in tags.split(",") if t.strip()]

    situation = fm.get("situation")
    automatic_thought = fm.get("automatic_thought") or fm.get("thought")
    belief_initial = int(fm["belief_initial"]) if fm.get("belief_initial") is not None else None
    evidence_for = fm.get("evidence_for")
    evidence_against = fm.get("evidence_against")
    alternative_thought = fm.get("alternative_thought") or fm.get("reframe")
    belief_final = int(fm["belief_final"]) if fm.get("belief_final") is not None else None
    action_plan = fm.get("action_plan") or fm.get("action")
    technique_used = fm.get("technique") or fm.get("technique_used")
    notes = fm.get("notes")

    # Extract sections from body if present
    sections: Dict[str, str] = {}
    current_sec = "main"
    sec_lines: List[str] = []
    top_title = None

    for line in body.splitlines():
        if line.startswith("#"):
            if sec_lines:
                sections[current_sec] = "\n".join(sec_lines).strip()
                sec_lines = []

            # Check if this is the level-1 document title: # Title
            if line.startswith("# ") and not line.startswith("## "):
                top_title = line[2:].strip()
                current_sec = "main"
                continue

            header = line.lstrip("#").strip().lower()
            if "alternative" in header or "reframe" in header or "rational" in header:
                current_sec = "alternative_thought"
            elif "automatic" in header or re.search(r"\bnat\b", header) or "negative thought" in header:
                current_sec = "automatic_thought"
            elif "evidence for" in header or "supporting" in header:
                current_sec = "evidence_for"
            elif "evidence against" in header or "contradicting" in header:
                current_sec = "evidence_against"
            elif "situation" in header or "trigger" in header:
                current_sec = "situation"
            elif "action" in header:
                current_sec = "action_plan"
            elif "note" in header or "reflection" in header:
                current_sec = "notes"
            else:
                current_sec = header
        else:
            sec_lines.append(line)
    if sec_lines:
        sections[current_sec] = "\n".join(sec_lines).strip()

    if not situation:
        if "situation" in sections:
            situation = sections["situation"]
        elif top_title:
            situation = top_title

    if "automatic_thought" in sections:
        c_thought, b_init = _clean_thought_text(sections["automatic_thought"])
        if not automatic_thought:
            automatic_thought = c_thought
        if belief_initial is None and b_init is not None:
            belief_initial = b_init

    if not evidence_for and "evidence_for" in sections:
        evidence_for = sections["evidence_for"]
    if not evidence_against and "evidence_against" in sections:
        evidence_against = sections["evidence_against"]

    if "alternative_thought" in sections:
        c_alt, b_fin = _clean_thought_text(sections["alternative_thought"])
        if not alternative_thought:
            alternative_thought = c_alt
        if belief_final is None and b_fin is not None:
            belief_final = b_fin

    if not action_plan and "action_plan" in sections:
        action_plan = sections["action_plan"].lstrip("- [ ]").strip()
    if not notes and "notes" in sections:
        notes = sections["notes"]
    elif not notes and "main" in sections and sections["main"]:
        cleaned_main = sections["main"]
        cleaned_lines = [l for l in cleaned_main.splitlines() if not l.startswith("- **")]
        leftover = "\n".join(cleaned_lines).strip()
        if leftover:
            notes = leftover

    return MoodEntry(
        id=entry_id,
        timestamp=timestamp,
        entry_type=entry_type,
        initial_mood=initial_mood,
        primary_emotion=primary_emotion,
        emotion_intensity_initial=emotion_intensity_initial,
        energy_level=energy_level,
        situation=situation,
        automatic_thought=automatic_thought,
        belief_initial=belief_initial,
        distortions=distortions,
        evidence_for=evidence_for,
        evidence_against=evidence_against,
        alternative_thought=alternative_thought,
        belief_final=belief_final,
        final_mood=final_mood,
        emotion_intensity_final=emotion_intensity_final,
        action_plan=action_plan,
        technique_used=technique_used,
        tags=tags,
        notes=notes,
    )


def get_note_filename(entry: MoodEntry) -> str:
    """Generate a clean, standardized filename for an entry."""
    dt = entry.parsed_datetime
    date_prefix = dt.strftime("%Y-%m-%d")
    slug_text = entry.situation or entry.entry_type
    slug = slugify(slug_text, max_len=30)
    eid = entry.id or "draft"
    return f"{date_prefix}-{slug}-{eid}.md"


def save_note_file(entry: MoodEntry, notes_dir: Optional[Path] = None) -> Path:
    """Save a MoodEntry as an individual Markdown file in the notes directory."""
    folder = ensure_notes_dir(notes_dir)
    filename = get_note_filename(entry)
    file_path = folder / filename
    md_content = entry_to_markdown(entry)
    file_path.write_text(md_content, encoding="utf-8")
    return file_path


def delete_note_file(entry_id: int, notes_dir: Optional[Path] = None) -> bool:
    """Delete the note file corresponding to an entry ID if it exists."""
    folder = notes_dir or get_default_notes_dir()
    if not folder.exists():
        return False

    pattern = f"*-{entry_id}.md"
    matches = list(folder.glob(pattern))
    deleted = False
    for f in matches:
        try:
            f.unlink()
            deleted = True
        except OSError:
            pass
    return deleted


def list_note_files(notes_dir: Optional[Path] = None) -> List[Tuple[Path, Dict[str, Any]]]:
    """List all markdown note files in the notes directory along with parsed frontmatter."""
    folder = notes_dir or get_default_notes_dir()
    if not folder.exists():
        return []

    results = []
    for p in sorted(folder.glob("*.md"), reverse=True):
        try:
            content = p.read_text(encoding="utf-8")
            fm, _ = parse_markdown_with_frontmatter(content)
            results.append((p, fm))
        except Exception:
            continue
    return results


def entry_to_yaml_data(entry: MoodEntry) -> Dict[str, Any]:
    """Generate a rich, standalone YAML-serializable dictionary for an entry."""
    data = entry_to_frontmatter_dict(entry)

    if entry.automatic_thought:
        data["automatic_thought"] = entry.automatic_thought
        if entry.belief_initial is not None:
            data["belief_initial"] = entry.belief_initial

    if entry.evidence_for:
        data["evidence_for"] = entry.evidence_for

    if entry.evidence_against:
        data["evidence_against"] = entry.evidence_against

    if entry.alternative_thought:
        data["alternative_thought"] = entry.alternative_thought
        if entry.belief_final is not None:
            data["belief_final"] = entry.belief_final

    if entry.action_plan:
        data["action_plan"] = entry.action_plan

    if entry.technique_details:
        data["technique_details"] = entry.technique_details

    if entry.notes:
        data["notes"] = entry.notes

    return data


def convert_md_file_to_yaml(md_path: Path, yaml_path: Optional[Path] = None) -> Path:
    """Convert a single Markdown note into a standalone YAML file."""
    content = md_path.read_text(encoding="utf-8")
    entry = markdown_to_entry(content, filename=md_path.name)
    yaml_dict = entry_to_yaml_data(entry)

    if yaml_path is None:
        yaml_path = md_path.with_suffix(".yaml")

    yaml_text = yaml.dump(yaml_dict, sort_keys=False, allow_unicode=True)
    yaml_path.write_text(yaml_text, encoding="utf-8")
    return yaml_path


def convert_notes_to_yaml(
    source_path: Path,
    output_path: Optional[Path] = None,
    single_file: bool = False,
) -> List[Path]:
    """Convert Markdown notes from a file or folder into convenient YAML.

    If source_path is a file, converts that file.
    If source_path is a directory:
      - If single_file is True (or output_path is a .yaml file), combines all notes into one YAML document.
      - If output_path is a directory, writes individual .yaml files into that directory.
      - Otherwise, writes .yaml files alongside the .md files.
    """
    if source_path.is_file():
        dest = output_path if (output_path and not output_path.is_dir()) else source_path.with_suffix(".yaml")
        out = convert_md_file_to_yaml(source_path, dest)
        return [out]

    md_files = sorted(source_path.glob("*.md"))
    if not md_files:
        return []

    # Check if user requested single-file output
    combine = single_file or (output_path is not None and output_path.suffix.lower() in [".yaml", ".yml"])

    if combine:
        if output_path is None or output_path.is_dir():
            out_file = (output_path or source_path) / "notes_combined.yaml"
        else:
            out_file = output_path

        all_entries = []
        for p in md_files:
            try:
                entry = markdown_to_entry(p.read_text(encoding="utf-8"), filename=p.name)
                all_entries.append(entry_to_yaml_data(entry))
            except Exception:
                continue

        yaml_text = yaml.dump(all_entries, sort_keys=False, allow_unicode=True)
        out_file.write_text(yaml_text, encoding="utf-8")
        return [out_file]

    # Multiple individual YAML files
    created_paths = []
    dest_dir = output_path if (output_path and output_path.is_dir()) else source_path
    dest_dir.mkdir(parents=True, exist_ok=True)

    for p in md_files:
        try:
            target_file = dest_dir / (p.stem + ".yaml")
            convert_md_file_to_yaml(p, target_file)
            created_paths.append(target_file)
        except Exception:
            continue

    return created_paths


def convert_yaml_to_md(yaml_path: Path, out_dir: Optional[Path] = None) -> Path:
    """Convert a YAML file back into a Markdown note with frontmatter."""
    yaml_text = yaml_path.read_text(encoding="utf-8")
    data = yaml.safe_load(yaml_text) or {}

    if isinstance(data, list):
        # List of entries
        dest_folder = out_dir or yaml_path.parent
        dest_folder.mkdir(parents=True, exist_ok=True)
        last_path = None
        for item in data:
            if isinstance(item, dict):
                e = MoodEntry.from_row(item)
                last_path = save_note_file(e, dest_folder)
        return last_path or dest_folder

    entry = MoodEntry.from_row(data)
    folder = out_dir or yaml_path.parent
    return save_note_file(entry, folder)


def sync_notes_with_db(db, notes_dir: Optional[Path] = None) -> Dict[str, int]:
    """Two-way synchronization between SQLite database and Markdown notes in ~/Notes."""
    folder = ensure_notes_dir(notes_dir)
    stats = {"exported": 0, "imported": 0, "updated": 0}

    # 1. Export DB entries that do not have a note file in folder
    db_entries = db.get_all_entries()
    existing_files = list(folder.glob("*.md"))
    existing_ids = set()

    for p in existing_files:
        try:
            content = p.read_text(encoding="utf-8")
            fm, _ = parse_markdown_with_frontmatter(content)
            if fm.get("id"):
                existing_ids.add(int(fm["id"]))
        except Exception:
            pass

    for entry in db_entries:
        if entry.id not in existing_ids:
            try:
                save_note_file(entry, folder)
                stats["exported"] += 1
            except Exception:
                pass

    # 2. Import or update any files from folder into DB
    for p in existing_files:
        try:
            content = p.read_text(encoding="utf-8")
            parsed_entry = markdown_to_entry(content, filename=p.name)
            if parsed_entry.id is not None and parsed_entry.id in {e.id for e in db_entries}:
                # Entry exists in DB, update if needed
                db.update_entry(parsed_entry)
                stats["updated"] += 1
            elif parsed_entry.id is None:
                # Brand new note created directly as a file in ~/Notes
                new_id = db.save_entry(parsed_entry)
                parsed_entry.id = new_id
                # Update file with assigned ID
                p.write_text(entry_to_markdown(parsed_entry), encoding="utf-8")
                stats["imported"] += 1
        except Exception:
            continue

    return stats


def task_to_markdown(task: AntiProcrastinationTask) -> str:
    """Format an AntiProcrastinationTask as a Markdown document with YAML frontmatter."""
    fm: Dict[str, Any] = {
        "id": task.id,
        "timestamp": task.created_at,
        "type": "pleasure_prediction",
        "task_name": task.task_name,
        "status": task.status,
        "predicted_difficulty": task.predicted_difficulty,
        "predicted_pleasure": task.predicted_pleasure,
    }

    if task.actual_difficulty is not None:
        fm["actual_difficulty"] = task.actual_difficulty
        fm["difficulty_delta"] = task.difficulty_delta

    if task.actual_pleasure is not None:
        fm["actual_pleasure"] = task.actual_pleasure
        fm["pleasure_delta"] = task.pleasure_delta

    if task.completed_at:
        fm["completed_at"] = task.completed_at

    if task.notes:
        fm["notes"] = task.notes

    yaml_header = yaml.dump(fm, sort_keys=False, allow_unicode=True).strip()

    lines = [
        "---",
        yaml_header,
        "---",
        "",
        f"# Pleasure Prediction: {task.task_name}",
        "",
        f"- **Date Logged:** {task.created_at[:16].replace('T', ' ')}",
        f"- **Status:** {task.status.upper()}",
        f"- **Predicted Difficulty:** {task.predicted_difficulty}% (0% = effortless, 100% = excruciating)",
        f"- **Predicted Pleasure / Joy:** {task.predicted_pleasure}% (0% = zero joy, 100% = deeply rewarding)",
    ]

    if task.is_completed:
        lines.append(f"- **Completed At:** {str(task.completed_at)[:16].replace('T', ' ')}")
        diff_str = f"Easier by {task.difficulty_delta}%" if (task.difficulty_delta and task.difficulty_delta > 0) else f"{task.difficulty_delta}%"
        lines.append(f"- **Actual Difficulty:** {task.actual_difficulty}% ({diff_str})")
        pleas_str = f"+{task.pleasure_delta}% more rewarding than expected" if (task.pleasure_delta and task.pleasure_delta > 0) else f"{task.pleasure_delta}%"
        lines.append(f"- **Actual Pleasure:** {task.actual_pleasure}% ({pleas_str})")
        lines.append("")
        lines.append("## Burns Anti-Procrastination Analysis")
        lines.append("")
        lines.append("Reality almost always outperforms depressive or anxious predictions. Notice how dread exaggerates difficulty and minimizes reward.")
    else:
        lines.append("")
        lines.append("> [!] Activity is currently pending.")
        lines.append(f"> After completing even 10 minutes of this activity, run `leahy complete {task.id or 1}` to record actual pleasure vs prediction!")

    if task.notes:
        lines.extend([
            "",
            "## Notes & Reflection",
            "",
            task.notes,
        ])

    return "\n".join(lines).strip() + "\n"


def save_task_note_file(task: AntiProcrastinationTask, notes_dir: Optional[Path] = None) -> Path:
    """Save an AntiProcrastinationTask as an individual Markdown file in ~/Notes."""
    folder = ensure_notes_dir(notes_dir)
    dt_str = task.created_at[:10]
    slug = slugify(task.task_name, max_len=25)
    tid = task.id or "draft"
    filename = f"{dt_str}-pleasure-{slug}-{tid}.md"
    file_path = folder / filename
    md_content = task_to_markdown(task)
    file_path.write_text(md_content, encoding="utf-8")
    return file_path


def delete_task_note_file(task_id: int, notes_dir: Optional[Path] = None) -> bool:
    """Delete the note file corresponding to a task ID if it exists."""
    folder = notes_dir or get_default_notes_dir()
    if not folder.exists():
        return False

    pattern = f"*-pleasure-*-{task_id}.md"
    matches = list(folder.glob(pattern))
    deleted = False
    for f in matches:
        try:
            f.unlink()
            deleted = True
        except OSError:
            pass
    return deleted


def experiment_to_markdown(exp: BehavioralExperiment) -> str:
    """Format a BehavioralExperiment as a Markdown document with YAML frontmatter."""
    fm: Dict[str, Any] = {
        "id": exp.id,
        "timestamp": exp.created_at,
        "type": "behavioral_experiment",
        "title": exp.title,
        "fear_prediction": exp.fear_prediction,
        "predicted_belief": exp.predicted_belief,
        "experiment_plan": exp.experiment_plan,
        "status": "completed" if exp.is_completed else exp.status,
    }

    if exp.actual_outcome:
        fm["actual_outcome"] = exp.actual_outcome
    if exp.actual_severity is not None:
        fm["actual_severity"] = exp.actual_severity
        fm["prediction_error"] = exp.prediction_error
    if exp.fear_realized is not None:
        fm["fear_realized"] = exp.fear_realized
    if exp.conclusion:
        fm["conclusion"] = exp.conclusion
    if exp.completed_at:
        fm["completed_at"] = exp.completed_at
    if exp.notes:
        fm["notes"] = exp.notes

    yaml_header = yaml.dump(fm, sort_keys=False, allow_unicode=True).strip()

    lines = [
        "---",
        yaml_header,
        "---",
        "",
        f"# Behavioral Experiment: {exp.title}",
        "",
        f"- **Date Logged:** {exp.created_at[:16].replace('T', ' ')}",
        f"- **Status:** {exp.status.upper()}",
        f"- **Feared Prediction:** \"{exp.fear_prediction}\"",
        f"- **Predicted Probability / Belief:** {exp.predicted_belief}%",
        f"- **Experiment Plan (Action):** {exp.experiment_plan}",
    ]

    if exp.is_completed:
        lines.append(f"- **Completed At:** {str(exp.completed_at)[:16].replace('T', ' ')}")
        lines.append(f"- **Actual Outcome:** {exp.actual_outcome or 'N/A'}")
        lines.append(f"- **Actual Severity (0-100%):** {exp.actual_severity}%")
        err_str = f"Reality was +{exp.prediction_error}% better than feared" if (exp.prediction_error and exp.prediction_error > 0) else f"{exp.prediction_error}%"
        lines.append(f"- **Prediction Error (Fear Gap):** {err_str}")
        realized_str = "YES (Catastrophe occurred)" if exp.fear_realized else "NO (Fear was disproven or manageable)"
        lines.append(f"- **Was Feared Catastrophe Realized?** {realized_str}")
        if exp.conclusion:
            lines.extend([
                "",
                "## Conclusion & What I Learned",
                "",
                f"> \"{exp.conclusion}\"",
            ])
    else:
        lines.append("")
        lines.append("> [!] Experiment is currently pending.")
        lines.append(f"> Carry out the action plan and run `leahy experiment complete {exp.id or 1}` to record what actually happened!")

    if exp.notes:
        lines.extend([
            "",
            "## Notes",
            "",
            exp.notes,
        ])

    return "\n".join(lines).strip() + "\n"


def save_experiment_note_file(exp: BehavioralExperiment, notes_dir: Optional[Path] = None) -> Path:
    """Save a BehavioralExperiment as an individual Markdown file in ~/Notes."""
    folder = ensure_notes_dir(notes_dir)
    dt_str = exp.created_at[:10]
    slug = slugify(exp.title or exp.fear_prediction, max_len=25)
    eid = exp.id or "draft"
    filename = f"{dt_str}-experiment-{slug}-{eid}.md"
    file_path = folder / filename
    md_content = experiment_to_markdown(exp)
    file_path.write_text(md_content, encoding="utf-8")
    return file_path


def delete_experiment_note_file(exp_id: int, notes_dir: Optional[Path] = None) -> bool:
    """Delete the note file corresponding to an experiment ID if it exists."""
    folder = notes_dir or get_default_notes_dir()
    if not folder.exists():
        return False

    pattern = f"*-experiment-*-{exp_id}.md"
    matches = list(folder.glob(pattern))
    deleted = False
    for f in matches:
        try:
            f.unlink()
            deleted = True
        except OSError:
            pass
    return deleted


