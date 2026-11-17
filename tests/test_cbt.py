from leahe.cbt_data import COGNITIVE_DISTORTIONS, STANDARD_EMOTIONS, SOCRATIC_QUESTIONS

def test_cognitive_distortions_catalog():
    assert len(COGNITIVE_DISTORTIONS) >= 10

    expected_codes = [
        "all_or_nothing",
        "overgeneralization",
        "mental_filter",
        "disqualifying_positive",
        "jumping_mind_reading",
        "jumping_fortune_telling",
        "catastrophizing",
        "emotional_reasoning",
        "should_statements",
        "labeling",
        "personalization",
    ]

    for code in expected_codes:
        assert code in COGNITIVE_DISTORTIONS
        info = COGNITIVE_DISTORTIONS[code]
        assert info.name
        assert info.summary
        assert info.description
        assert info.example
        assert len(info.challenge_questions) >= 2

def test_standard_emotions():
    assert "Anxiety / Fear" in STANDARD_EMOTIONS
    assert "Sadness / Depression" in STANDARD_EMOTIONS
    assert "Anger / Frustration" in STANDARD_EMOTIONS

    for category, emotions in STANDARD_EMOTIONS.items():
        assert len(emotions) >= 3

def test_socratic_questions():
    assert len(SOCRATIC_QUESTIONS) >= 4
