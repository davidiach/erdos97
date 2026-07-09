#!/usr/bin/env python3
"""Check the n=9 vertex-circle local-lemma audit path as one chain."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Mapping

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPT_DIR = ROOT / "scripts"
for path in (SRC, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from check_n9_vertex_circle_exhaustive_local_lemma_crosswalk import (  # noqa: E402
    DEFAULT_CLASSIFICATION,
    DEFAULT_EXHAUSTIVE,
    assert_expected_exhaustive_local_lemma_crosswalk,
    exhaustive_local_lemma_crosswalk_payload,
)
from check_n9_vertex_circle_focused_minireplay_crosswalk import (  # noqa: E402
    DEFAULT_MINIREPLAY_PATHS,
    assert_expected_focused_minireplay_crosswalk,
    focused_minireplay_crosswalk_payload,
)
from check_n9_vertex_circle_focused_packet_catalog_audit import (  # noqa: E402
    DEFAULT_LOCAL_LEMMAS as DEFAULT_FOCUSED_LOCAL_LEMMAS,
    DEFAULT_PACKET_PATHS,
    DEFAULT_TEMPLATE_CATALOG,
    DEFAULT_TEMPLATE_PACKET_PATHS,
    assert_expected_focused_packet_catalog_audit,
    focused_packet_catalog_audit_payload,
)
from check_n9_vertex_circle_local_lemma_replay_crosswalk import (  # noqa: E402
    DEFAULT_AGGREGATE,
    DEFAULT_SIMPLE_REPLAY,
    assert_expected_replay_crosswalk,
    crosswalk_payload as local_replay_crosswalk_payload,
    load_artifact,
)
from check_n9_relation_skeleton_closed_descent_crosswalk import (  # noqa: E402
    DEFAULT_CLOSED_DESCENT,
    assert_expected_relation_closed_descent_crosswalk,
    relation_closed_descent_crosswalk_payload,
)
from check_artifact_provenance import (  # noqa: E402
    DEFAULT_MANIFEST as DEFAULT_GENERATED_ARTIFACTS_MANIFEST,
    SCHEMA as GENERATED_ARTIFACTS_SCHEMA,
    load_manifest as load_generated_artifact_manifest,
    validate_native_trust_policy,
)
from check_relation_skeleton_local_lemma_crosswalk import (  # noqa: E402
    DEFAULT_RELATION_SKELETONS,
    assert_expected_relation_local_crosswalk,
    crosswalk_payload as relation_local_crosswalk_payload,
)
from erdos97.path_display import display_path  # noqa: E402

SCHEMA = "erdos97.n9_vertex_circle_local_lemma_audit_path.v1"
ASSERT_EXPECTED_FAILURE_SCHEMA = (
    "erdos97.n9_vertex_circle_local_lemma_audit_path.assert_expected_failure.v1"
)
ASSERT_EXPECTED_FAILURE_KEYS = frozenset(
    {
        "schema",
        "stage",
        "exception_type",
        "message",
        "validation_error_count",
    }
)
STATUS = "REVIEW_PENDING_LOCAL_LEMMA_AUDIT_PATH"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Cross-artifact audit path for the review-pending n=9 vertex-circle "
    "local-lemma packets. It joins focused packet/catalog bookkeeping, "
    "focused mini-replays, aggregate/simple replay accounting, the "
    "exhaustive/local-lemma count crosswalk, and the relation-skeleton "
    "crosswalk, with a relation-skeleton/closed-descent companion check. "
    "It does not prove packet soundness, does not prove mini-replay "
    "soundness, does not prove local-lemma completeness, does not prove "
    "frontier coverage, does not prove n=9, is not a counterexample, and "
    "is not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_local_lemma_audit_path.py",
    "command": (
        "python scripts/check_n9_vertex_circle_local_lemma_audit_path.py "
        "--check --assert-expected --json"
    ),
}

EXPECTED_LAYER_IDS = [
    "focused_packet_catalog",
    "focused_minireplay",
    "aggregate_simple_replay",
    "exhaustive_local_lemma",
    "relation_skeleton_local_lemma",
]
EXPECTED_TEMPLATE_IDS = [f"T{index:02d}" for index in range(1, 13)]
EXPECTED_HANDOFF_EDGES = list(zip(EXPECTED_LAYER_IDS, EXPECTED_LAYER_IDS[1:]))
EXPECTED_INPUT_ARTIFACT_COUNT = 33
EXPECTED_MANIFEST_CONTRACT_IDS = [
    "manifest_role_contract",
    "manifest_digest_contract",
    "manifest_header_contract",
    "manifest_provenance_contract",
    "manifest_metadata_contract",
    "manifest_claim_contract",
    "manifest_consistency",
]
EXPECTED_AUDIT_CONTRACT_COMPONENT_IDS = [
    "layer_contracts",
    "layer_provenance",
    "layer_source_artifact_contracts",
    "claim_scope_guards",
    "layer_output_contracts",
    "layer_input_contracts",
    "focused_minireplay_record_path_contract",
    "handoff_checks",
    "closed_descent_companion",
    "reviewer_command_surface",
    "manifest_contracts",
]
EXPECTED_LAYER_CONTRACTS = {
    "focused_packet_catalog": {
        "schema": "erdos97.n9_vertex_circle_focused_packet_catalog_audit.v1",
        "status": "REVIEW_PENDING_FOCUSED_PACKET_CATALOG_AUDIT",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "validation_status": "passed",
    },
    "focused_minireplay": {
        "schema": "erdos97.n9_vertex_circle_focused_minireplay_crosswalk.v1",
        "status": "REVIEW_PENDING_FOCUSED_MINIREPLAY_CROSSWALK",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "validation_status": "passed",
    },
    "aggregate_simple_replay": {
        "schema": "erdos97.n9_vertex_circle_local_lemma_replay_crosswalk.v1",
        "status": "REVIEW_PENDING_PACKET_AUDIT",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "validation_status": "passed",
    },
    "exhaustive_local_lemma": {
        "schema": "erdos97.n9_vertex_circle_exhaustive_local_lemma_crosswalk.v1",
        "status": "REVIEW_PENDING_PACKET_AUDIT",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "validation_status": "passed",
    },
    "relation_skeleton_local_lemma": {
        "schema": "erdos97.relation_skeleton_local_lemma_crosswalk.v1",
        "status": "REVIEW_PENDING_PACKET_AUDIT",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "validation_status": "passed",
    },
}
EXPECTED_LAYER_PROVENANCE = {
    "focused_packet_catalog": {
        "generator": "scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py",
        "command": (
            "python scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py "
            "--check --assert-expected --json"
        ),
    },
    "focused_minireplay": {
        "generator": "scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py",
        "command": (
            "python scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py "
            "--check --assert-expected --json"
        ),
    },
    "aggregate_simple_replay": {
        "generator": "scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py",
        "command": (
            "python scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py "
            "--check --assert-expected --json"
        ),
    },
    "exhaustive_local_lemma": {
        "generator": (
            "scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py"
        ),
        "command": (
            "python scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py "
            "--check --assert-expected --json"
        ),
    },
    "relation_skeleton_local_lemma": {
        "generator": "scripts/check_relation_skeleton_local_lemma_crosswalk.py",
        "command": (
            "python scripts/check_relation_skeleton_local_lemma_crosswalk.py "
            "--check --assert-expected --json"
        ),
    },
}
CLOSED_DESCENT_COMPANION_PROVENANCE = {
    "generator": "scripts/check_n9_relation_skeleton_closed_descent_crosswalk.py",
    "command": (
        "python scripts/check_n9_relation_skeleton_closed_descent_crosswalk.py "
        "--check --assert-expected --json"
    ),
}
REVIEWER_COMMAND_DOC_REQUIREMENTS = {
    "combined_audit_path": (
        "docs/n9-vertex-circle-local-lemma-review-packet.md",
        "docs/n9-vertex-circle-local-lemmas.md",
        "docs/reviewer-guide.md",
        "docs/review-priorities.md",
    ),
    "focused_packet_catalog": (
        "docs/n9-vertex-circle-local-lemma-review-packet.md",
        "docs/n9-vertex-circle-local-lemmas.md",
    ),
    "focused_minireplay": (
        "docs/n9-vertex-circle-local-lemma-review-packet.md",
        "docs/n9-vertex-circle-local-lemmas.md",
    ),
    "aggregate_simple_replay": (
        "docs/n9-vertex-circle-local-lemma-review-packet.md",
        "docs/n9-vertex-circle-local-lemmas.md",
    ),
    "exhaustive_local_lemma": (
        "docs/n9-vertex-circle-local-lemma-review-packet.md",
        "docs/n9-vertex-circle-local-lemmas.md",
    ),
    "relation_skeleton_local_lemma": (
        "docs/n9-vertex-circle-local-lemma-review-packet.md",
        "docs/n9-vertex-circle-local-lemmas.md",
    ),
    "relation_skeleton_closed_descent": (
        "docs/n9-vertex-circle-local-lemma-review-packet.md",
        "docs/n9-vertex-circle-local-lemmas.md",
    ),
}
SOURCE_ARTIFACT_KEYS = ("path", "role", "schema", "status", "trust")
EXPECTED_LAYER_SOURCE_ARTIFACTS = {
    "focused_packet_catalog": (
        {
            "path": "data/certificates/n9_vertex_circle_template_lemma_catalog.json",
            "role": "template lemma-candidate catalog",
            "schema": "erdos97.n9_vertex_circle_template_lemma_catalog.v1",
            "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
        {
            "path": "data/certificates/n9_vertex_circle_local_lemmas.json",
            "role": "aggregate local-lemma scan",
            "schema": "erdos97.n9_vertex_circle_local_lemmas.v1",
            "status": "REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
        {
            "path": "data/certificates/n9_vertex_circle_self_edge_template_packet.json",
            "role": "self-edge template packet",
            "schema": "erdos97.n9_vertex_circle_self_edge_template_packet.v1",
            "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
        {
            "path": "data/certificates/n9_vertex_circle_strict_cycle_template_packet.json",
            "role": "strict-cycle template packet",
            "schema": "erdos97.n9_vertex_circle_strict_cycle_template_packet.v1",
            "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
    ),
    "focused_minireplay": (),
    "aggregate_simple_replay": (
        {
            "path": "data/certificates/n9_vertex_circle_local_lemmas.json",
            "role": "aggregate local-lemma scan",
            "schema": "erdos97.n9_vertex_circle_local_lemmas.v1",
            "status": "REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
        {
            "path": (
                "data/certificates/"
                "n9_vertex_circle_local_lemma_simple_replay.json"
            ),
            "role": "simple packet replay audit",
            "schema": "erdos97.n9_vertex_circle_local_lemma_simple_replay.v1",
            "status": "REVIEW_PENDING_PACKET_AUDIT",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
    ),
    "exhaustive_local_lemma": (
        {
            "path": "data/certificates/n9_vertex_circle_exhaustive.json",
            "role": "review-pending exhaustive n=9 count artifact",
            "schema": "n9_vertex_circle_exhaustive_v1",
            "status": None,
            "trust": "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING",
        },
        {
            "path": (
                "data/certificates/"
                "n9_vertex_circle_frontier_motif_classification.json"
            ),
            "role": "frontier assignment motif classification",
            "schema": (
                "erdos97.n9_vertex_circle_frontier_motif_classification.v1"
            ),
            "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
        {
            "path": "data/certificates/n9_vertex_circle_local_lemmas.json",
            "role": "aggregate local-lemma scan",
            "schema": "erdos97.n9_vertex_circle_local_lemmas.v1",
            "status": "REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
        {
            "path": (
                "data/certificates/"
                "n9_vertex_circle_local_lemma_simple_replay.json"
            ),
            "role": "simple local-lemma replay audit",
            "schema": "erdos97.n9_vertex_circle_local_lemma_simple_replay.v1",
            "status": "REVIEW_PENDING_PACKET_AUDIT",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
    ),
    "relation_skeleton_local_lemma": (
        {
            "path": "data/certificates/relation_skeleton_catalog.json",
            "role": "relation-skeleton catalog",
            "schema": "erdos97.relation_skeleton_catalog.v1",
            "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
        {
            "path": "data/certificates/n9_vertex_circle_local_lemmas.json",
            "role": "aggregate local-lemma scan",
            "schema": "erdos97.n9_vertex_circle_local_lemmas.v1",
            "status": "REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
        {
            "path": (
                "data/certificates/"
                "n9_vertex_circle_local_lemma_simple_replay.json"
            ),
            "role": "simple local-lemma replay audit",
            "schema": "erdos97.n9_vertex_circle_local_lemma_simple_replay.v1",
            "status": "REVIEW_PENDING_PACKET_AUDIT",
            "trust": "REVIEW_PENDING_DIAGNOSTIC",
        },
    ),
}
CLAIM_SCOPE_GUARDS = {
    "mentions_n9_scope": (("n=9",),),
    "denies_proof": (("does not prove",), ("not a proof",)),
    "denies_counterexample": (
        ("not a counterexample",),
        ("does not prove", "counterexample"),
    ),
    "denies_global_status_update": (
        ("not a global status update",),
        ("does not prove", "official/global status update"),
    ),
}
MANIFEST_SCOPE_GUARDS = {
    "marks_repo_local_finite_case": (("repo-local", "finite-case"),),
    "marks_candidate_scope": (("candidate",),),
    "denies_global_status_update": (("does not update", "official/global"),),
}
EXPECTED_LAYER_OUTPUT_CONTRACTS = {
    "focused_packet_catalog": {
        "summary_key": "focused_packet_catalog_audit",
        "required_top_level_keys": ("source_artifacts", "packet_artifacts"),
        "required_summary_keys": (
            "packet_count",
            "template_ids",
            "covered_family_count",
            "covered_assignment_count",
            "packet_records",
            "status_counts",
            "status_assignment_counts",
        ),
    },
    "focused_minireplay": {
        "summary_key": "focused_minireplay_crosswalk",
        "required_top_level_keys": (),
        "required_summary_keys": (
            "minireplay_count",
            "packet_count",
            "template_ids",
            "source_family_count",
            "source_assignment_count",
            "records",
            "status_counts",
            "status_assignment_counts",
        ),
    },
    "aggregate_simple_replay": {
        "summary_key": "coverage_summary",
        "required_top_level_keys": (
            "source_artifacts",
            "family_crosswalk",
            "focused_crosscheck_summary",
        ),
        "required_summary_keys": (
            "expected_family_count",
            "expected_assignment_count",
            "matched_family_count",
            "matched_assignment_count",
            "self_edge_family_count",
            "self_edge_assignment_count",
            "strict_cycle_family_count",
            "strict_cycle_assignment_count",
        ),
    },
    "exhaustive_local_lemma": {
        "summary_key": "coverage_summary",
        "required_top_level_keys": (
            "source_artifacts",
            "family_crosswalk",
            "local_replay_crosswalk_summary",
        ),
        "required_summary_keys": (
            "classification_assignment_count",
            "exhaustive_frontier_assignment_count",
            "family_count",
            "local_matched_assignment_count",
            "self_edge_assignment_count",
            "strict_cycle_assignment_count",
        )