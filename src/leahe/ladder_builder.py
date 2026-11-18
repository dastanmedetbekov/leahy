"""Ladder Builder & Fear Hierarchy Comparator.

Assists in constructing systematic desensitization hierarchies by:
1. Brainstorming / collecting a collection of sub-fears related to a core theme.
2. Ranking them from least scary to most scary via interactive pairwise comparisons.
3. Automatically calibrating SUDS (Subjective Units of Distress) across the hierarchy.
4. Persisting the ladder and its steps into the Leahe database.
"""

from typing import List, Callable, Optional, Dict, Any
from .models import ExposureLadder, ExposureStep
from .database import Database


def calculate_suds_distribution(count: int, min_suds: int = 15, max_suds: int = 95) -> List[int]:
    """Calculate evenly distributed SUDS values for a given number of steps."""
    if count <= 0:
        return []
    if count == 1:
        return [50]
    step_size = (max_suds - min_suds) / (count - 1)
    return [round(min_suds + i * step_size) for i in range(count)]


def pairwise_sort(items: List[str], compare_fn: Callable[[str, str], int]) -> List[str]:
    """Sort items using binary insertion sort with minimal pairwise comparisons.

    compare_fn(a, b) should return:
      < 0 if a feels LESS anxiety-provoking than b
      > 0 if a feels MORE anxiety-provoking than b
      0 if equal
    """
    if len(items) <= 1:
        return list(items)

    sorted_items = [items[0]]
    for item in items[1:]:
        low = 0
        high = len(sorted_items)
        while low < high:
            mid = (low + high) // 2
            res = compare_fn(item, sorted_items[mid])
            if res <= 0:
                high = mid
            else:
                low = mid + 1
        sorted_items.insert(low, item)
    return sorted_items


def build_exposure_ladder(
    db: Database,
    fear_theme: str,
    ranked_steps: List[Dict[str, Any]],
    notes: Optional[str] = None,
) -> ExposureLadder:
    """Save an exposure ladder along with its ordered steps in the database."""
    ladder = ExposureLadder(
        fear_theme=fear_theme.strip(),
        notes=notes,
    )
    ladder_id = db.save_ladder(ladder)
    ladder.id = ladder_id

    suds_values = calculate_suds_distribution(len(ranked_steps))
    saved_steps = []

    for idx, item in enumerate(ranked_steps):
        desc = item.get("description", "") if isinstance(item, dict) else str(item)
        target_suds = item.get("target_suds") if isinstance(item, dict) else None
        if target_suds is None:
            target_suds = suds_values[idx]

        step = ExposureStep(
            ladder_id=ladder_id,
            step_order=idx + 1,
            description=desc.strip(),
            target_suds=max(0, min(100, int(target_suds))),
            notes=item.get("notes") if isinstance(item, dict) else None,
        )
        step_id = db.save_exposure_step(step)
        step.id = step_id
        saved_steps.append(step)

    ladder.steps = saved_steps
    return ladder
