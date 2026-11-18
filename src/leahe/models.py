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

    def tags_as_csv(self) -> str:
        return ", ".join(self.tags)

    @classmethod
    def from_row(cls, row: dict) -> "MoodEntry":
        distortions_raw = row.get("distortions")
        distortions_list = []
        if distortions_raw:
            try:
                distortions_list = json.loads(distortions_raw)
            except Exception:
                distortions_list = [d.strip() for d in distortions_raw.split(",") if d.strip()]

        tags_raw = row.get("tags")
        tags_list = []
        if tags_raw:
            try:
                tags_list = json.loads(tags_raw)
            except Exception:
                tags_list = [t.strip().lstrip("#") for t in tags_raw.split(",") if t.strip()]

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
            tags=tags_list,
            notes=row.get("notes"),
        )

@dataclass
class ActionItem:
    id: Optional[int] = None
    entry_id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    action_text: str = ""
    is_done: bool = False
    completed_at: Optional[str] = None

    @classmethod
    def from_row(cls, row: dict) -> "ActionItem":
        return cls(
            id=row.get("id"),
            entry_id=row.get("entry_id"),
            created_at=row.get("created_at") or datetime.now().isoformat(),
            action_text=row.get("action_text", ""),
            is_done=bool(row.get("is_done", 0)),
            completed_at=row.get("completed_at"),
        )

@dataclass
class AntiProcrastinationTask:
    id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    task_name: str = ""
    predicted_difficulty: int = 50   # 0-100%
    predicted_pleasure: int = 50     # 0-100%
    actual_difficulty: Optional[int] = None  # 0-100%
    actual_pleasure: Optional[int] = None    # 0-100%
    status: str = "pending"          # "pending" or "completed"
    completed_at: Optional[str] = None
    notes: Optional[str] = None

    @property
    def is_completed(self) -> bool:
        return self.status == "completed" or self.actual_pleasure is not None

    @property
    def difficulty_delta(self) -> Optional[int]:
        if self.actual_difficulty is not None:
            # Positive value means it was easier than predicted (predicted - actual)
            return self.predicted_difficulty - self.actual_difficulty
        return None

    @property
    def pleasure_delta(self) -> Optional[int]:
        if self.actual_pleasure is not None:
            # Positive value means it was more pleasant than predicted (actual - predicted)
            return self.actual_pleasure - self.predicted_pleasure
        return None

    @classmethod
    def from_row(cls, row: dict) -> "AntiProcrastinationTask":
        return cls(
            id=row.get("id"),
            created_at=row.get("created_at") or datetime.now().isoformat(),
            task_name=row.get("task_name", ""),
            predicted_difficulty=int(row.get("predicted_difficulty", 50)),
            predicted_pleasure=int(row.get("predicted_pleasure", 50)),
            actual_difficulty=int(row["actual_difficulty"]) if row.get("actual_difficulty") is not None else None,
            actual_pleasure=int(row["actual_pleasure"]) if row.get("actual_pleasure") is not None else None,
            status=row.get("status", "pending"),
            completed_at=row.get("completed_at"),
            notes=row.get("notes"),
        )

@dataclass
class DASAssessment:
    id: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    scores_json: str = "{}"
    total_score: int = 0
    top_vulnerabilities: str = ""
    notes: Optional[str] = None

    @classmethod
    def from_row(cls, row: dict) -> "DASAssessment":
        return cls(
            id=row.get("id"),
            timestamp=row.get("timestamp") or datetime.now().isoformat(),
            scores_json=row.get("scores_json", "{}"),
            total_score=int(row.get("total_score", 0)),
            top_vulnerabilities=row.get("top_vulnerabilities", ""),
            notes=row.get("notes"),
        )

@dataclass
class BehavioralExperiment:
    id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    title: str = ""
    fear_prediction: str = ""
    predicted_belief: int = 80          # 0-100% confidence catastrophe will occur
    experiment_plan: str = ""           # Action designed to empirically test fear
    actual_outcome: Optional[str] = None
    actual_severity: Optional[int] = None # 0-100% how bad reality actually was
    fear_realized: Optional[bool] = None  # True if worst case happened, False if disproven
    conclusion: Optional[str] = None    # Takeaway / reframe learned
    status: str = "pending"             # "pending" or "completed"
    completed_at: Optional[str] = None
    notes: Optional[str] = None

    @property
    def is_completed(self) -> bool:
        return self.status == "completed" or (self.actual_outcome is not None and self.fear_realized is not None)

    @property
    def prediction_error(self) -> Optional[int]:
        """Difference between feared probability/severity and reality (positive = reality was better than feared)."""
        if self.actual_severity is not None:
            return self.predicted_belief - self.actual_severity
        return None

    @classmethod
    def from_row(cls, row: dict) -> "BehavioralExperiment":
        return cls(
            id=row.get("id"),
            created_at=row.get("created_at") or datetime.now().isoformat(),
            title=row.get("title", ""),
            fear_prediction=row.get("fear_prediction", ""),
            predicted_belief=int(row.get("predicted_belief", 80)),
            experiment_plan=row.get("experiment_plan", ""),
            actual_outcome=row.get("actual_outcome"),
            actual_severity=int(row["actual_severity"]) if row.get("actual_severity") is not None else None,
            fear_realized=bool(row["fear_realized"]) if row.get("fear_realized") is not None else None,
            conclusion=row.get("conclusion"),
            status=row.get("status", "pending"),
            completed_at=row.get("completed_at"),
            notes=row.get("notes"),
        )

@dataclass
class ExposureStep:
    id: Optional[int] = None
    ladder_id: int = 0
    step_order: int = 1
    description: str = ""
    target_suds: int = 50               # Subjective Units of Distress (0-100)
    repetitions_done: int = 0
    last_pre_suds: Optional[int] = None
    last_post_suds: Optional[int] = None
    status: str = "pending"             # "pending", "in_progress", "mastered"
    completed_at: Optional[str] = None
    notes: Optional[str] = None

    @property
    def habituation_delta(self) -> Optional[int]:
        """Anxiety reduction after repeated exposure (pre_suds - post_suds)."""
        if self.last_pre_suds is not None and self.last_post_suds is not None:
            return self.last_pre_suds - self.last_post_suds
        return None

    @property
    def suds_relief(self) -> Optional[int]:
        return self.habituation_delta

    @property
    def is_mastered(self) -> bool:
        return self.status == "mastered"

    @classmethod
    def from_row(cls, row: dict) -> "ExposureStep":
        return cls(
            id=row.get("id"),
            ladder_id=int(row.get("ladder_id", 0)),
            step_order=int(row.get("step_order", 1)),
            description=row.get("description", ""),
            target_suds=int(row.get("target_suds", 50)),
            repetitions_done=int(row.get("repetitions_done", 0)),
            last_pre_suds=int(row["last_pre_suds"]) if row.get("last_pre_suds") is not None else None,
            last_post_suds=int(row["last_post_suds"]) if row.get("last_post_suds") is not None else None,
            status=row.get("status", "pending"),
            completed_at=row.get("completed_at"),
            notes=row.get("notes"),
        )

@dataclass
class ExposureLadder:
    id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    fear_theme: str = ""                # e.g. "Social Anxiety / Rejection", "Public Speaking"
    steps: List[ExposureStep] = field(default_factory=list)
    notes: Optional[str] = None

    @classmethod
    def from_row(cls, row: dict, steps: Optional[List[ExposureStep]] = None) -> "ExposureLadder":
        return cls(
            id=row.get("id"),
            created_at=row.get("created_at") or datetime.now().isoformat(),
            fear_theme=row.get("fear_theme", ""),
            steps=steps or [],
            notes=row.get("notes"),
        )


