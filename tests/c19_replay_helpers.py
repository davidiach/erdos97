"""Helpers for platform-stable C19 artifact replay assertions."""

from __future__ import annotations

from typing import Any

VOLATILE_C19_REPLAY_KEYS = {
    "certificate",
    "certificate_kind_counts",
    "certificate_summary",
    "certificate_weight_counts",
    "closed_certificate_examples",
    "closed_support_size_histogram",
    "closed_support_size_histograms",
    "direct_closed_examples",
    "fallback_certificate_digest",
    "fallback_certificates",
    "fifth_pair_closed_examples",
    "fourth_pair_closed_examples",
    "sample_certificates",
}

VOLATILE_C19_HISTOGRAM_KEYS = {
    "certificate_kind_pattern",
    "fallback_support_size",
    "kind_pattern",
    "max_weight",
    "support_size",
    "weight_sum",
}


def stable_c19_replay_view(value: Any) -> Any:
    """Drop solver-selected certificate details from a replay payload.

    The scripts validate any regenerated certificate exactly before returning
    JSON.  Across HiGHS/SciPy builds the chosen positive certificate can differ,
    so replay tests compare the stable finite accounting and labels rather than
    byte-for-byte LP support choices.
    """

    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            if key in VOLATILE_C19_REPLAY_KEYS:
                continue
            if key in VOLATILE_C19_HISTOGRAM_KEYS:
                continue
            result[key] = stable_c19_replay_view(item)
        return result
    if isinstance(value, list):
        return [stable_c19_replay_view(item) for item in value]
    return value


def assert_c19_replay_matches_artifact(payload: Any, artifact: Any) -> None:
    assert stable_c19_replay_view(payload) == stable_c19_replay_view(artifact)
