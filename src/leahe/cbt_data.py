"""CBT (Cognitive Behavioral Therapy) reference data and taxonomies.

This module contains clinically established definitions for cognitive distortions,
emotion taxonomies, and Socratic reflection questions.
Strictly ASCII/Unicode text without emojis.
"""

from dataclasses import dataclass
from typing import List, Dict

@dataclass(frozen=True)
class DistortionInfo:
    code: str
    name: str
    summary: str
    description: str
    example: str
    challenge_questions: List[str]

COGNITIVE_DISTORTIONS: Dict[str, DistortionInfo] = {
    "all_or_nothing": DistortionInfo(
        code="all_or_nothing",
        name="All-or-Nothing Thinking",
        summary="Thinking in absolute extremes (black-and-white) with no middle ground.",
        description=(
            "Viewing a situation in only two categories instead of on a continuum. "
            "If an outcome or performance falls short of perfection, you see it as a complete failure."
        ),
        example="'If I don't get an A on this exam, I am a complete failure.'",
        challenge_questions=[
            "Is the situation truly 100% bad, or is there a grey area?",
            "Can something be partially successful even if it is not perfect?",
            "Where does this fall on a scale from 0 to 100 rather than all-or-nothing?",
        ],
    ),
    "overgeneralization": DistortionInfo(
        code="overgeneralization",
        name="Overgeneralization",
        summary="Viewing a single negative event as a never-ending pattern of defeat.",
        description=(
            "Using words like 'always', 'never', 'everyone', or 'no one' based on a single "
            "or isolated negative occurrence."
        ),
        example="'I stumbled during my presentation. I always mess things up.'",
        challenge_questions=[
            "Am I assuming that because it happened once, it will always happen?",
            "What are times in the past when things turned out differently or positively?",
            "Is it accurate to use absolute terms like 'always' or 'never' here?",
        ],
    ),
    "mental_filter": DistortionInfo(
        code="mental_filter",
        name="Mental Filter",
        summary="Dwelling obsessively on a single negative detail while ignoring positive aspects.",
        description=(
            "Picking out a single negative detail and dwelling on it exclusively, so that "
            "your vision of all reality becomes darkened, like a drop of ink discoloring a beaker of water."
        ),
        example="'I received 9 positive reviews and 1 critical review; my work is terrible.'",
        challenge_questions=[
            "Am I filtering out all the positive or neutral facts?",
            "What positive evidence am I ignoring or discounting right now?",
            "What would the full picture look like if I weighed all evidence equally?",
        ],
    ),
    "disqualifying_positive": DistortionInfo(
        code="disqualifying_positive",
        name="Disqualifying the Positive",
        summary="Rejecting positive experiences by insisting they 'don't count'.",
        description=(
            "Transforming neutral or positive experiences into negative ones by arguing "
            "that they don't matter, were mere flukes, or were done out of pity/politeness."
        ),
        example="'They said I did a good job, but they were just being nice.'",
        challenge_questions=[
            "Why am I rejecting genuine positive feedback or successes?",
            "If someone else achieved this, would I acknowledge their achievement?",
            "What would happen if I accepted this positive outcome at face value?",
        ],
    ),
    "jumping_mind_reading": DistortionInfo(
        code="jumping_mind_reading",
        name="Mind Reading (Jumping to Conclusions)",
        summary="Assuming you know what people are thinking without sufficient evidence.",
        description=(
            "Concluding arbitrarily that someone is reacting negatively to you, without "
            "checking it out or possessing objective verification."
        ),
        example="'He didn't reply to my message right away; he must be annoyed with me.'",
        challenge_questions=[
            "Do I have concrete, verifiable proof of what they are thinking?",
            "What are other plausible explanations for their behavior (e.g. busy, tired)?",
            "Have I directly asked them, or am I projecting my own fears?",
        ],
    ),
    "jumping_fortune_telling": DistortionInfo(
        code="jumping_fortune_telling",
        name="Fortune Telling (Jumping to Conclusions)",
        summary="Predicting that things will turn out badly as an established fact.",
        description=(
            "Anticipating that things will turn out badly, and feeling convinced that your "
            "prediction is an already established reality."
        ),
        example="'I know I am going to bomb the interview tomorrow.'",
        challenge_questions=[
            "Can I truly predict the future with 100% certainty?",
            "How many times in the past has my worst prediction failed to happen?",
            "What is the most realistic outcome rather than the worst imaginable one?",
        ],
    ),
    "catastrophizing": DistortionInfo(
        code="catastrophizing",
        name="Catastrophizing (Magnification/Minimization)",
        summary="Blowing negative events out of proportion or shrinking positive ones.",
        description=(
            "Exaggerating the importance or consequences of problems and mistakes, "
            "or inappropriately shrinking the value of your own desirable qualities."
        ),
        example="'I made a typo in the team email. My reputation is ruined forever.'",
        challenge_questions=[
            "What is the realistic worst that could happen, and could I survive it?",
            "Will this matter in 6 months, 1 year, or 5 years?",
            "What is the most likely, middle-of-the-road outcome?",
        ],
    ),
    "emotional_reasoning": DistortionInfo(
        code="emotional_reasoning",
        name="Emotional Reasoning",
        summary="Believing that something must be true simply because you feel it strongly.",
        description=(
            "Assuming that your negative emotions necessarily reflect the true state of external reality: "
            "'I feel like an idiot, therefore I must be one.'"
        ),
        example="'I feel overwhelmed and anxious, so this project must be doomed.'",
        challenge_questions=[
            "Are feelings facts, or are feelings emotional reactions to thoughts?",
            "Has there been a time when I felt strongly about something, but the facts were different?",
            "What are the objective facts separate from what I am currently feeling?",
        ],
    ),
    "should_statements": DistortionInfo(
        code="should_statements",
        name="'Should' & 'Must' Statements",
        summary="Using rigid rules about how you or others 'must', 'ought to', or 'should' behave.",
        description=(
            "Motivating yourself or evaluating others with rigid imperatives. Directing shoulds "
            "inward produces guilt and frustration; directing them outward produces anger and resentment."
        ),
        example="'I should never get anxious. I must be strong at all times.'",
        challenge_questions=[
            "Who established this unbending rule?",
            "What happens if I replace 'I should' with 'I would prefer to' or 'It would be helpful if'?",
            "Is my standard realistic and compassionate given human limitations?",
        ],
    ),
    "labeling": DistortionInfo(
        code="labeling",
        name="Labeling and Mislabeling",
        summary="Attaching a fixed, global, negative label to yourself or others.",
        description=(
            "An extreme form of all-or-nothing thinking. Instead of describing an error "
            "or behavior, you attach an absolute label: 'I am a failure' instead of 'I made an error.'"
        ),
        example="'I missed the deadline. I am completely incompetent.'",
        challenge_questions=[
            "Does this one mistake define my entire identity as a human being?",
            "Can a person be summarized by a single derogatory label?",
            "How would I describe the specific behavior without labeling the whole person?",
        ],
    ),
    "personalization": DistortionInfo(
        code="personalization",
        name="Personalization and Blame",
        summary="Holding yourself responsible for events outside your control, or blaming others entirely.",
        description=(
            "Taking responsibility for a negative event when there is no basis for doing so, "
            "or conversely, blaming others exclusively while ignoring one's own contribution."
        ),
        example="'My friend seems unhappy today. It must be something I did wrong.'",
        challenge_questions=[
            "Was I truly the sole cause of this event, or were other factors at play?",
            "Do I have complete control over other people's moods or decisions?",
            "What factors outside my control contributed to this situation?",
        ],
    ),
}

STANDARD_EMOTIONS: Dict[str, List[str]] = {
    "Anxiety / Fear": ["Anxious", "Worried", "Apprehensive", "Panicked", "Overwhelmed", "Nervous"],
    "Sadness / Depression": ["Sad", "Depressed", "Hopeless", "Lonely", "Grief-stricken", "Empty"],
    "Anger / Frustration": ["Angry", "Frustrated", "Irritated", "Resentful", "Enraged", "Annoyed"],
    "Guilt / Shame": ["Guilty", "Ashamed", "Inadequate", "Self-critical", "Embarrassed"],
    "Calm / Neutral": ["Calm", "Grounded", "Relaxed", "Content", "Neutral", "Reflective"],
    "Positive / Hope": ["Hopeful", "Encouraged", "Confident", "Relieved", "Grateful", "Determined"],
}

SOCRATIC_QUESTIONS: List[str] = [
    "What is the objective, factual evidence that supports this automatic thought?",
    "What is the objective, factual evidence that contradicts or weakens this thought?",
    "What would I say to a dear friend or colleague who came to me with this exact thought?",
    "If the worst possible scenario happened, what steps could I realistically take to cope?",
    "What is a more balanced, compassionate, and evidence-based way to view this situation?",
]
