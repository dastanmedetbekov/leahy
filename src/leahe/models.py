"""Data models for CBT mood tracker entries and statistics."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import json

@dataclass
class MoodEntry:
    id: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    entry_type: str = "quick"  # "quick" or "cbt_record"
    initial_mood: int = 5      # 1-10 scale
    primary_emotion: str = "Neutral"
    emotion_intensity_initial: int = 50  # 0-100%
    energy_level: Optional[int] = None   # 1-10 scale
    situation: Optional[str] = None
    automatic_thought: Optional[str] = None
    belief_initial: Optional[int] = None  # 0-100%
    distortions: List[str] = field(default_factory=list)
    evidence_for: Optional[str] = None
    evidence_against: Optional[str] = None
    alternative_thought: Optional[str] = None
    belief_final: Optional[int] = None    # 0-100%
    final_mood: Optional[int] = None      # 1-10 scale
    emotion_intensity_final: Optional[int] = None  # 0-100%
    action_plan: Optional[str] = None
    technique_used: Optional[str] = None       # e.g. "double_standard", "cost_benefit", "downward_arrow"
    technique_details: Optional[str] = None    # structured JSON or text detailing the Burns technique output
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None

    @property
    def is_cbt(self) -> bool:
        return self.entry_type == "cbt_record"

    @property
    def mood_delta(self) -> Optional[int]:
        if self.final_mood is not None:
            return self.final_mood - self.initial_mood
        return None

    @property
    def intensity_delta(self) -> Optional[int]:
        if self.emotion_intensity_final is not None:
            # Positive value means reduction in distress/intensity
            return self.emotion_intensity_initial - self.emotion_intensity_final
        return None

    @property
    def parsed_datetime(self) -> datetime:
        try:
            return datetime.fromisoformat(self.timestamp)
        except Exception:
            return datetime.now()

    def distortions_as_json(self) -> str:
        return json.dumps(self.distortions)

    @classmethod
    def from_row(cls, row: dict) -> "MoodEntry":
        distortions_raw = row.get("distortions")
        distortions_list = []
        if distortions_raw:
            try:
                distortions_list = json.loads(distortions_raw)
            except Exception:
                distortions_list = [d.strip() for d in distortions_raw.split(",") if d.strip()]

        return cls(
            id=row.get("id"),
            timestamp=row.get("timestamp") or datetime.now().isoformat(),
            entry_type=row.get("entry_type") or "quick",
            initial_mood=int(row.get("initial_mood", 5)),
            primary_emotion=row.get("primary_emotion") or "Neutral",
            emotion_intensity_initial=int(row.get("emotion_intensity_initial", 50)),
            energy_level=int(row["energy_level"]) if row.get("energy_level") is not None else None,
            situation=row.get("situation"),
            automatic_thought=row.get("automatic_thought"),
            belief_initial=int(row["belief_initial"]) if row.get("belief_initial") is not None else None,
            distortions=distortions_list,
            evidence_for=row.get("evidence_for"),
            evidence_against=row.get("evidence_against"),
            alternative_thought=row.get("alternative_thought"),
            belief_final=int(row["belief_final"]) if row.get("belief_final") is not None else None,
            final_mood=int(row["final_mood"]) if row.get("final_mood") is not None else None,
            emotion_intensity_final=int(row["emotion_intensity_final"]) if row.get("emotion_intensity_final") is not None else None,
            action_plan=row.get("action_plan"),
            technique_used=row.get("technique_used"),
            technique_details=row.get("technique_details"),
            notes=row.get("notes"),
        )
