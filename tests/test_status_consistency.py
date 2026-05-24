from __future__ import annotations

from scripts.check_status_consistency import find_forbidden_overclaim_lines


def test_forbidden_overclaim_detector_flags_positive_proof_and_counterexample() -> None:
    text = "\n".join(
        [
            "We have proven Erdos Problem #97 and have a definitive counterexample.",
            "We have a proof of Erdos Problem #97.",
            "No one should overclaim, but we solved Erdos Problem #97.",
        ]
    )

    hits = find_forbidden_overclaim_lines(text)

    assert hits == [
        (1, "We have proven Erdos Problem #97 and have a definitive counterexample."),
        (2, "We have a proof of Erdos Problem #97."),
        (3, "No one should overclaim, but we solved Erdos Problem #97."),
    ]


def test_forbidden_overclaim_detector_allows_explicit_nonclaims() -> None:
    text = "\n".join(
        [
            "No general proof and no counterexample are claimed.",
            "This fixed-pattern obstruction is not a proof of Erdos Problem #97.",
            "Forbidden overclaiming text: this proves Erdos Problem #97.",
            "This diagnostic does not prove Erdos Problem #97.",
            "This diagnostic does not",
            "prove Erdos Problem #97.",
        ]
    )

    assert find_forbidden_overclaim_lines(text) == []
