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


def test_forbidden_overclaim_detector_blocks_known_evasions() -> None:
    # A negation in a different comma/colon/dash clause must not excuse the claim.
    assert find_forbidden_overclaim_lines(
        "Summary - no longer open: we have proven Erdos Problem #97"
    )
    assert find_forbidden_overclaim_lines(
        "Cannot stress enough, we have proven Erdos Problem #97 today"
    )
    # Synonym proof/refutation verbs applied to the global target.
    for line in (
        "We resolved Erdos Problem #97.",
        "We have refuted the conjecture.",
        "We have settled the problem.",
    ):
        assert find_forbidden_overclaim_lines(line), line
    # An uppercase-led wrapped continuation line still joins to the claim verb.
    assert find_forbidden_overclaim_lines(
        "We have constructed a valid\nCounterexample to the conjecture."
    )


def test_forbidden_overclaim_detector_does_not_carry_block_line_negation() -> None:
    # A negation on a heading / list item / block quote must NOT be joined to a
    # following standalone overclaim and excuse it (regression for the wrap-join).
    assert find_forbidden_overclaim_lines(
        "## Not solved\nWe have proven Erdos Problem #97."
    )
    assert find_forbidden_overclaim_lines(
        "- not yet\nWe have proven Erdos Problem #97."
    )
    assert find_forbidden_overclaim_lines(
        "> not a proof\nWe have proven Erdos Problem #97."
    )
    # A genuine wrapped prose sentence with a governing negation is still allowed.
    assert (
        find_forbidden_overclaim_lines(
            "This fixed-pattern obstruction does not\nProve Erdos Problem #97."
        )
        == []
    )


def test_forbidden_overclaim_detector_keeps_governing_negation() -> None:
    # A negation that genuinely governs the verb in its own clause stays allowed.
    assert find_forbidden_overclaim_lines("This does not prove Erdos Problem #97.") == []
    assert (
        find_forbidden_overclaim_lines(
            "minimality produces a remaining center; this is not a counterexample."
        )
        == []
    )
