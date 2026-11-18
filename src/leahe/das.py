"""David Burns' Dysfunctional Attitude Scale (DAS) assessment.

Tests underlying silent assumptions and psychological vulnerabilities
(Approval, Love, Achievement, Perfectionism, Entitlement, Omnipotence, Autonomy).
Strictly NO emojis. Clean ASCII styling.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Any

@dataclass(frozen=True)
class DASQuestion:
    id: int
    text: str
    domain: str
    rationale: str

DAS_QUESTIONS: List[DASQuestion] = [
    DASQuestion(
        id=1,
        text="If I do not perform at the highest level at all times, I will likely end up a failure.",
        domain="Perfectionism",
        rationale="Perfectionism is an all-or-nothing trap. Mistakes are essential for learning, not proof of failure.",
    ),
    DASQuestion(
        id=2,
        text="I cannot be truly happy or content unless most people I encounter like and approve of me.",
        domain="Approval Addiction",
        rationale="Approval addiction places your self-esteem in other people's hands. Self-worth is not democratic.",
    ),
    DASQuestion(
        id=3,
        text="My value as a human being depends almost entirely on how much I accomplish and achieve.",
        domain="Achievement Addiction",
        rationale="Confusing human worth with productivity turns you into a human doing rather than a human being.",
    ),
    DASQuestion(
        id=4,
        text="If someone I deeply care about is disappointed with me, it means I am inherently deficient.",
        domain="Love & Validation",
        rationale="Other people's moods are influenced by their own thoughts, biology, and stressors, not solely by you.",
    ),
    DASQuestion(
        id=5,
        text="If I treat people well and work conscientiously, the world and others should treat me fairly.",
        domain="Entitlement & Demand for Fairness",
        rationale="Demanding universal fairness causes chronic resentment. The universe has no contractual guarantee of fairness.",
    ),
    DASQuestion(
        id=6,
        text="If a friend or family member is unhappy, it is my fault and my direct duty to fix their feelings.",
        domain="Omnipotence & Hyper-Responsibility",
        rationale="You have influence over others, but zero absolute control over their internal emotional state.",
    ),
    DASQuestion(
        id=7,
        text="It is better to sacrifice my own wishes and needs than risk disappointing or annoying others.",
        domain="Submissiveness & Pleasing",
        rationale="Compulsive people-pleasing breeds chronic inner resentment and destroys genuine intimacy.",
    ),
    DASQuestion(
        id=8,
        text="Making a mistake in front of peers or colleagues is thoroughly humiliating and intolerable.",
        domain="Perfectionism",
        rationale="Everyone makes mistakes daily. Exposure of normal fallibility fosters connection, not contempt.",
    ),
    DASQuestion(
        id=9,
        text="If I am alone on weekends or evenings, it proves that I am socially undesirable and unloved.",
        domain="Love & Validation",
        rationale="Solitude is an opportunity for renewal and autonomy, not an indictment of your social desirability.",
    ),
    DASQuestion(
        id=10,
        text="Criticism from a supervisor or peer implies that my overall competence is deeply compromised.",
        domain="Approval Addiction",
        rationale="Constructive criticism is specific behavioral feedback, not a character execution.",
    ),
]

DOMAIN_ANTIDOTES: Dict[str, str] = {
    "Perfectionism": (
        "Burns Antidote: Give yourself permission to be a fallible human being. "
        "Lower your standard from 100% flawless to 80% competent. "
        "Paradoxically, your productivity and enjoyment will increase as anxiety drops."
    ),
    "Approval Addiction": (
        "Burns Antidote: Other people's opinions reflect their personal filters and mood, not your intrinsic worth. "
        "If someone disapproves of you, it may be inconvenient, but it is never fatal."
    ),
    "Achievement Addiction": (
        "Burns Antidote: Your human worth was established at birth and cannot be augmented or diminished by your resume. "
        "Productivity can produce satisfaction, but it cannot purchase human worth."
    ),
    "Love & Validation": (
        "Burns Antidote: Rejection does not make you unlovable; it simply means there is a mismatch of values, timing, or needs. "
        "You are whole and complete on your own."
    ),
    "Entitlement & Demand for Fairness": (
        "Burns Antidote: Replace the rigid demand 'People must be fair' with 'I prefer fairness, but when others are unfair, "
        "I will focus on what I can control without burning myself in anger.'"
    ),
    "Omnipotence & Hyper-Responsibility": (
        "Burns Antidote: You cannot control another adult's emotions. "
        "Offer support and empathy, but drop the burden of being their psychological savior."
    ),
    "Submissiveness & Pleasing": (
        "Burns Antidote: Asserting your genuine preferences is an act of honesty and self-respect. "
        "Saying 'no' to others is saying 'yes' to your mental health."
    ),
}
