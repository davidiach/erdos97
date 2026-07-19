from __future__ import annotations

from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import product

from erdos97.external_exact_seven_l0_audit import (
    EXPECTED_E_LANDINGS,
    EXPECTED_LF_SHA256,
    EXPECTED_P_LANDINGS,
    EXPECTED_POINT_COUNT_DISTRIBUTION,
    EXPECTED_ROWS,
    EXPECTED_SCHEMA_COUNT,
    EXPECTED_SCHEMA_SHA256,
    _all_expected_schemas,
    _canonical_schema_sha256,
    _expected_schema,
    _has_named_source,
    _lf_bytes,
    _schema_issues,
)


def test_lf_bytes_makes_checkout_hash_line_ending_invariant() -> None:
    lf = b"alpha\nbeta\n"
    crlf = b"alpha\r\nbeta\r\n"
    assert _lf_bytes(lf) == lf
    assert _lf_bytes(crlf) == lf
    assert sha256(_lf_bytes(crlf)).digest() == sha256(lf).digest()


def test_pinned_landing_inventory_has_expected_product_size() -> None:
    assert len(EXPECTED_LF_SHA256) == 7
    assert len(EXPECTED_E_LANDINGS) == 8
    assert len(EXPECTED_P_LANDINGS) == 5
    assert len(EXPECTED_ROWS) == 3
    assert len(EXPECTED_E_LANDINGS) * len(EXPECTED_P_LANDINGS) ** 3 == 1000


def test_independent_schema_inventory_has_pinned_digest_and_distribution() -> None:
    schemas = _all_expected_schemas()
    assert len(schemas) == EXPECTED_SCHEMA_COUNT
    assert len({schema["id"] for schema in schemas}) == EXPECTED_SCHEMA_COUNT
    assert _canonical_schema_sha256(schemas) == EXPECTED_SCHEMA_SHA256
    assert Counter(len(schema["points"]) for schema in schemas) == (
        EXPECTED_POINT_COUNT_DISTRIBUTION
    )


def test_schema_contract_rejects_duplicate_point_and_incomplete_exclusion() -> None:
    e_pair = EXPECTED_E_LANDINGS[0]
    row_pairs = tuple(EXPECTED_P_LANDINGS[0] for _ in EXPECTED_ROWS)
    schema = _expected_schema(e_pair, row_pairs)
    assert not _schema_issues(schema, e_pair, row_pairs)

    duplicate = deepcopy(schema)
    duplicate["points"].append(duplicate["points"][-1])
    assert _schema_issues(duplicate, e_pair, row_pairs) == (
        f"{schema['id']}.points",
    )

    incomplete = deepcopy(schema)
    incomplete["exact_classes"][0]["exclude"].pop()
    assert _schema_issues(incomplete, e_pair, row_pairs) == (
        f"{schema['id']}.exact_classes",
    )


def test_all_landing_tuples_build_contract_cleanly() -> None:
    for e_pair in EXPECTED_E_LANDINGS:
        for row_pairs in product(
            EXPECTED_P_LANDINGS,
            repeat=len(EXPECTED_ROWS),
        ):
            schema = _expected_schema(e_pair, row_pairs)
            assert not _schema_issues(schema, e_pair, row_pairs)


def test_named_theorem_source_detection_uses_exact_basename() -> None:
    source = "scratch/Round188ExactSevenNamedInteriorNormalForm.lean"
    assert _has_named_source([source])
    assert not _has_named_source([f"notes/{source}.md"])
