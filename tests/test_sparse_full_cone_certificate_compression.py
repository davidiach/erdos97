from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "exploration" / "compress_sparse_full_cone_certificates.py"
SPEC = importlib.util.spec_from_file_location("sparse_full_cone_compression", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
COMPRESS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = COMPRESS
SPEC.loader.exec_module(COMPRESS)


def test_random_lp_support_finds_a_positive_two_row_dependency() -> None:
    rows = [
        COMPRESS.InequalityRow("K1", (0, 1, 2, 3), (1, 0)),
        COMPRESS.InequalityRow("K1", (0, 1, 3, 2), (-1, 0)),
        COMPRESS.InequalityRow("K2", (0, 2, 1, 3), (0, 1)),
        COMPRESS.InequalityRow("K2", (0, 2, 3, 1), (0, -1)),
    ]
    matrix = np.asarray([row.vector for row in rows], dtype=float)
    equality_matrix = np.vstack([matrix.T, np.ones((1, len(rows)))])
    equality_rhs = np.asarray([0.0, 0.0, 1.0])

    support = COMPRESS.random_lp_support(
        rows,
        equality_matrix,
        equality_rhs,
        seed=3,
        tolerance=1.0e-9,
    )

    assert support in ([0, 1], [2, 3])


def test_modular_rank_is_exact_on_small_integer_rows() -> None:
    assert COMPRESS.modular_rank([[1, 0, 1], [2, 0, 2], [0, 1, 3]]) == 2
    assert COMPRESS.modular_rank([[1, 2], [2, 4], [3, 6]]) == 1


def test_order_quad_coverage_is_exact() -> None:
    quads = [(0, 2, 1, 4), (2, 1, 3, 4)]

    assert COMPRESS.order_satisfies_quads([0, 2, 1, 3, 4], quads)
    assert not COMPRESS.order_satisfies_quads([0, 1, 2, 3, 4], quads)


def test_checker_replays_an_exact_source_certificate_as_baseline() -> None:
    source = json.loads(
        (
            ROOT
            / "data"
            / "runs"
            / "sparse_full_cone_cegar_2026-07-22"
            / "summary.json"
        ).read_text(encoding="utf-8")
    )
    c25 = next(run for run in source["runs"] if run["pattern"].startswith("C25"))
    model = next(item for item in c25["models"] if item["lightweight_filters"]["survives"])
    certificate = model["full_kalmanson"]["certificate"]
    quad_count = model["full_kalmanson"]["unique_ordered_quad_count"]
    circuit_audit = COMPRESS.positive_circuit_audit(certificate)
    payload = {
        "runs": [
            {
                "compressed_models": [
                    {
                        "source_model_index": model["model_index"],
                        "order": model["order"],
                        "source_unique_ordered_quad_count": quad_count,
                        "compressed_unique_ordered_quad_count": quad_count,
                        "quad_reduction": 0,
                        "positive_circuit_audit": circuit_audit,
                        "compressed_certificate": certificate,
                    }
                ],
                "compressed_clause_coverage": [
                    {
                        "source_model_index": model["model_index"],
                        "covered_strong_model_indices": [model["model_index"]],
                    }
                ],
            }
        ]
    }

    assert COMPRESS.check_payload(payload) == {
        "status": "OK",
        "verified_compressed_exact_certificates": 1,
    }
