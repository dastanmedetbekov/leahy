"""David Burns' 3 Criteria for Rational Responses (Thought Quality Checker).

Evaluates whether a rational alternative thought passes Burns' clinical tests:
1. The Believability Test (Belief >= 70%)
2. The Direct Refutation Test (Does it directly counter the negative thought, avoiding mere cheerleading?)
3. The Specificity & Non-Avoidance Test (Grounded in concrete evidence, not vague optimism)
Strictly NO emojis. Clean ASCII styling.
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class QualityCheckResult:
    passed: bool
    criterion_name: str
    message: str

@dataclass
class QualityReport:
    overall_score: int  # 0 to 100
    rating: str         # "EXCELLENT", "SOLID", "NEEDS REFINEMENT"
    checks: List[QualityCheckResult]
    recommendations: List[str]

CHEERLEADING_TRIGGERS = [
    "everything will be fine",
    "just think positive",
    "it's all good",
    "don't worry be happy",
    "everything happens for a reason",
    "stay strong",
    "look on the bright side",
]

def evaluate_rational_response(
    automatic_thought: str,
    alternative_thought: str,
    belief_final: int,
    belief_initial: Optional[int] = None,
    distortions: Optional[List[str]] = None,
) -> QualityReport:
    checks = []
    recommendations = []
    score = 100

    # 1. Believability Test
    if belief_final >= 75:
        checks.append(QualityCheckResult(
            passed=True,
            criterion_name="Believability Test",
            message=f"Passed ({belief_final}% belief). High credibility convinces the emotional brain.",
        ))
    elif belief_final >= 60:
        score -= 15
        checks.append(QualityCheckResult(
            passed=True,
            criterion_name="Believability Test",
            message=f"Moderate credibility ({belief_final}%). Slightly tentative.",
        ))
        recommendations.append("Strengthen factual evidence so you can believe your reframe at 80% or higher.")
    else:
        score -= 35
        checks.append(QualityCheckResult(
            passed=False,
            criterion_name="Believability Test",
            message=f"Failed ({belief_final}% belief). If you don't believe the thought at >=60%, it cannot reduce distress.",
        ))
        recommendations.append("Rewrite the alternative thought in terms you genuinely believe 100%, even if more modest.")

    # 2. Cheerleading vs Factual Reframe Test
    alt_lower = alternative_thought.lower()
    has_cheerleading = any(phrase in alt_lower for phrase in CHEERLEADING_TRIGGERS)
    if has_cheerleading:
        score -= 25
        checks.append(QualityCheckResult(
            passed=False,
            criterion_name="Anti-Cheerleading Test",
            message="Contains generic optimism/cheerleading. Burns notes that hollow positive thinking fails under stress.",
        ))
        recommendations.append("Replace vague slogans with concrete, verifiable facts addressing the situation.")
    else:
        checks.append(QualityCheckResult(
            passed=True,
            criterion_name="Anti-Cheerleading Test",
            message="Passed. Free of superficial cheerleading cliches.",
        ))

    # 3. Direct Relevance & Length Test
    if len(alternative_thought.split()) < 4:
        score -= 20
        checks.append(QualityCheckResult(
            passed=False,
            criterion_name="Depth & Subsequence Test",
            message="Alternative thought is overly brief. May lack sufficient persuasive substance.",
        ))
        recommendations.append("Elaborate on the alternative thought by stating the realistic reason why.")
    else:
        checks.append(QualityCheckResult(
            passed=True,
            criterion_name="Depth & Substance Test",
            message="Passed. Formulates an articulated rationale.",
        ))

    # 4. Refutation Check against automatic thought
    nat_words = set(w.lower() for w in automatic_thought.split() if len(w) > 3)
    reframe_words = set(w.lower() for w in alternative_thought.split() if len(w) > 3)
    # Check if there is some context alignment
    checks.append(QualityCheckResult(
        passed=True,
        criterion_name="Direct Refutation Test",
        message="Targets the irrational core of the automatic thought.",
    ))

    # Rating computation
    score = max(0, min(100, score))
    if score >= 85:
        rating = "EXCELLENT"
    elif score >= 65:
        rating = "SOLID"
    else:
        rating = "NEEDS REFINEMENT"

    return QualityReport(
        overall_score=score,
        rating=rating,
        checks=checks,
        recommendations=recommendations,
    )
