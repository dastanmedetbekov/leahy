from leahe.burns_methods import BURNS_METHODS

def test_burns_methods_catalog():
    assert len(BURNS_METHODS) >= 10

    expected_methods = [
        "double_standard",
        "cost_benefit",
        "downward_arrow",
        "shades_of_grey",
        "semantic_method",
        "define_terms",
        "reattribution",
        "experimental_technique",
        "what_if_decatastrophize",
        "positive_reframing",
    ]

    for code in expected_methods:
        assert code in BURNS_METHODS
        method = BURNS_METHODS[code]
        assert method.name
        assert method.category
        assert method.summary
        assert method.description
        assert method.when_to_use
        assert len(method.guided_prompts) >= 2
        assert method.example
