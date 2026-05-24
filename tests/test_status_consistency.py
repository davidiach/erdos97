from __future__ import annotations

from scripts.check_status_consistency import find_forbidden_overclaim_lines


def test_forbidden_overclaim_detector_flags_positive_proof_and_counterexample() -> None:
    text = "We have proven Erdos Problem #97 and have a definitive counterexample."

    hits = find_forbidden_overclaim_lines(text)

    assert hits == [(1, text)]


def test_forbidden_overclaim_detector_allows_explicit_nonclaims() -> None:
    text = "\n".join(
        [
            "No general proof and no counterexample are claimed.",
            "This fixed-pattern obstruction is not a proof of Erdos Problem #97.",
            "Forbidden overclaiming text: this proves Erdos Problem #97.",
        ]
    )

    assert find_forbidden_overclaim_lines(text) == []
