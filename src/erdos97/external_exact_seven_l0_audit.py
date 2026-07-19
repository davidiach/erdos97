"""Fail-closed audit of the external exact-seven L0 schema frontier.

The audit pins the public external snapshot, reconstructs the all-fresh L0
schema contract independently, and compares every generated schema with that
contract.  It does not prove that L0 covers all exact-seven configurations,
build the cited Lean normal-form theorem, or validate Euclidean realizability.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import importlib.util
from itertools import product
import json
from pathlib import Path
import subprocess
from types import ModuleType
from typing import Iterable

from erdos97.external_frontier_audit import _git_commit


EXPECTED_COMMIT = "b46c14df95b6509240f1083bb16beba30dd780be"

L0_ROOT = Path("scratch/atail-force/exact7-role-coverage-gate")
ENUMERATOR = L0_ROOT / "enumerate_l0.py"
ENCODER = L0_ROOT / "gate_encoder.py"
ENCODER_FACTS = L0_ROOT / "ENCODER_FACTS.md"
REPORT = L0_ROOT / "REPORT.md"
SMOKE_FIXTURE = L0_ROOT / "smoke_fixture.py"
SMOKE_RESULTS = L0_ROOT / "smoke_results.json"
CENSUS_RUNNER = L0_ROOT / "census_runner.py"

EXPECTED_LF_SHA256 = {
    ENUMERATOR: "d81aef9ae4b6d0d25ff177be7baa27a0f7a1bf1bfaa4d616412ee0604235cb57",
    ENCODER: "e9979f8e63373bcb0e2fb34e57c2def62c91a8ff87a280defebda588b2f79a57",
    ENCODER_FACTS: (
        "ebdc036c719501503d05b6357372aa601f2b75076ef13d708747b16d0ed85cee"
    ),
    REPORT: "465699dd4aff7b8a6126839519a4d520de865d30e2fb4e8524391dc2b7b7ab12",
    SMOKE_FIXTURE: (
        "03a7303e1174955b2a6a11213c7a970541a39c3a6d426d5597ce4921e8231a3d"
    ),
    SMOKE_RESULTS: (
        "5cc4235b7394a63704a576e9030ff143117fc588b4964535d832b7d8576d1373"
    ),
    CENSUS_RUNNER: (
        "d5ff300c3c7518c9c0e3b8dbd8582585aba9d3b4b9e3f2e0afed83ea26f5bc94"
    ),
}

NAMED_INTERIOR_SOURCE = "Round188ExactSevenNamedInteriorNormalForm.lean"
L0_SCHEMA_ARTIFACT = (L0_ROOT / "l0_schemas.json").as_posix()
EXPECTED_REPORT_STALE_MARKERS = (
    "SMOKE-VALIDATED (5/5)",
    "ENUMERATOR NOT YET\nBUILT",
)

EXPECTED_E_LANDINGS = (
    ("S", "S"),
    ("S", "O1"),
    ("S", "EA"),
    ("S", "W"),
    ("O1", "O1"),
    ("O1", "EA"),
    ("O1", "W"),
    ("EA", "W"),
)
EXPECTED_P_LANDINGS = (
    ("S", "S"),
    ("S", "O1"),
    ("S", "O"),
    ("O1", "O1"),
    ("O1", "O"),
)
EXPECTED_ROWS = (
    ("b0", ("s0", "s1"), ("p0a", "p0b")),
    ("b1", ("s1", "s2"), ("p1a", "p1b")),
    ("s1", ("s2", "s0"), ("p2a", "p2b")),
)
CAP_INTERIOR = ("s0", "b0", "s1", "b1", "s2")
EXPECTED_TIMEOUT_MS = 300_000
EXPECTED_SCHEMA_COUNT = 1000
EXPECTED_SCHEMA_SHA256 = (
    "6832099d275e3bc934bb1dff31ffa625824cb8596fe657643db9ba8a1179a256"
)
EXPECTED_POINT_COUNT_DISTRIBUTION = {
    11: 8,
    12: 68,
    13: 222,
    14: 351,
    15: 270,
    16: 81,
}
EXPECTED_SMOKE_VERDICTS = {
    "A_fixed_full": "unsat",
    "B_named_fixed": "sat",
    "C_symbolic_full": "unsat",
    "D_named_symbolic": "sat",
    "E_fixed_hingefree": "unsat",
    "F_named_floating": "sat",
    "G_uniq4_unit": "unsat",
}


def _lf_bytes(data: bytes) -> bytes:
    """Normalize checkout line endings to the committed LF convention."""
    return data.replace(b"\r\n", b"\n")


def _lf_sha256(path: Path) -> str:
    return sha256(_lf_bytes(path.read_bytes())).hexdigest()


def _canonical_schema_sha256(schemas: list[dict[str, object]]) -> str:
    encoded = json.dumps(
        schemas,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _git_tracked_files(checkout: Path) -> tuple[str, ...]:
    completed = subprocess.run(
        ["git", "-C", str(checkout), "ls-tree", "-r", "--name-only", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return tuple(line for line in completed.stdout.splitlines() if line)


def _load_pinned_enumerator(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("external_exact7_enumerate_l0", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load external enumerator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _expected_schema(
    e_pair: tuple[str, str],
    row_pairs: tuple[tuple[str, str], ...],
) -> dict[str, object]:
    """Build one L0 schema from the independently pinned public contract."""
    schema_id = "L0.e{}-{}.".format(*e_pair) + ".".join(
        "r{}{}-{}".format(index, *pair)
        for index, pair in enumerate(row_pairs)
    )
    bags: dict[str, list[str]] = {"S": [], "O1": []}
    points = ["EA", "O", "W", *CAP_INTERIOR]

    def land(role: str, site: str) -> str:
        if site in {"EA", "W", "O"}:
            return site
        bags[site].append(role)
        points.append(role)
        return role

    e_members = [land(f"e{index + 1}", site) for index, site in enumerate(e_pair)]
    row_members: list[tuple[str, list[str]]] = []
    for (center, forced, fresh_names), sites in zip(
        EXPECTED_ROWS,
        row_pairs,
        strict=True,
    ):
        landed = [land(name, site) for name, site in zip(fresh_names, sites)]
        row_members.append((center, [*forced, *landed]))

    point_set = set(points)
    o_class = ["s0", "s1", "s2", *e_members]
    exact_classes = [
        {
            "center": "O",
            "members": o_class,
            "exclude": sorted(point_set - {"O"} - set(o_class)),
        }
    ]
    for center, members in row_members:
        exact_classes.append(
            {
                "center": center,
                "members": members,
                "exclude": sorted(point_set - {center} - set(members)),
            }
        )

    return {
        "id": schema_id,
        "points": points,
        "blocks": [
            {"points": ["EA"], "ordered": True},
            {"points": bags["S"], "ordered": False},
            {"points": ["O"], "ordered": True},
            {"points": bags["O1"], "ordered": False},
            {"points": ["W"], "ordered": True},
            {"points": list(CAP_INTERIOR), "ordered": True},
        ],
        "exact_classes": exact_classes,
        "unique_class": [{"center": "O", "members": o_class}],
        "timeout_ms": EXPECTED_TIMEOUT_MS,
    }


def _schema_issues(
    schema: dict[str, object],
    e_pair: tuple[str, str],
    row_pairs: tuple[tuple[str, str], ...],
) -> tuple[str, ...]:
    expected = _expected_schema(e_pair, row_pairs)
    keys = set(expected) | set(schema)
    return tuple(
        f"{expected['id']}.{key}"
        for key in sorted(keys)
        if schema.get(key) != expected.get(key)
    )


def _all_expected_schemas() -> list[dict[str, object]]:
    return [
        _expected_schema(e_pair, row_pairs)
        for e_pair in EXPECTED_E_LANDINGS
        for row_pairs in product(EXPECTED_P_LANDINGS, repeat=len(EXPECTED_ROWS))
    ]


def _has_named_source(tracked_files: Iterable[str]) -> bool:
    return any(Path(path).name == NAMED_INTERIOR_SOURCE for path in tracked_files)


@dataclass(frozen=True)
class ExternalExactSevenL0Audit:
    checkout: str
    commit: str | None
    normalized_lf_sha256: dict[str, str]
    schema_summary: dict[str, object]
    smoke_summary: dict[str, object]
    public_provenance: dict[str, object]
    validation_issues: tuple[str, ...]
    expected_snapshot_match: bool

    def to_json(self) -> dict[str, object]:
        return {
            "type": "external_exact_seven_l0_audit",
            "trust": "EXTERNAL_L0_ENUMERATOR_PROVENANCE_AUDIT_ONLY",
            "mechanics_trust": "EXACT_FINITE_SCHEMA_MECHANICS",
            "checkout": self.checkout,
            "commit": self.commit,
            "normalized_lf_sha256": dict(
                sorted(self.normalized_lf_sha256.items())
            ),
            "schema_summary": self.schema_summary,
            "smoke_summary": self.smoke_summary,
            "public_provenance": self.public_provenance,
            "validation_issues": list(self.validation_issues),
            "expected_snapshot": {
                "commit": EXPECTED_COMMIT,
                "normalized_lf_sha256": {
                    path.as_posix(): digest
                    for path, digest in EXPECTED_LF_SHA256.items()
                },
                "schema_sha256": EXPECTED_SCHEMA_SHA256,
                "schema_count": EXPECTED_SCHEMA_COUNT,
            },
            "expected_snapshot_match": self.expected_snapshot_match,
            "frontier": {
                "slice": "exact-seven all-reverse aligned-cap L0 all-fresh",
                "l0_all_fresh_mechanics_checked": self.schema_summary[
                    "every_schema_matches_independent_contract"
                ],
                "coincidence_merge_refinement": "NOT_BUILT",
                "l1_first_apex_rows": "NOT_BUILT",
                "census": "NO_COMMITTED_TERMINAL_ARTIFACT",
                "next_acceptance_gate": (
                    "commit the named-interior Lean source and complete merge/L1 "
                    "coverage, or hand a checked SAT survivor to nonlinear geometry"
                ),
            },
            "claims": {
                "external_lean_build_checked": False,
                "full_exact_seven_coverage_checked": False,
                "euclidean_or_mec_realizability_checked": False,
                "proves_exact_seven_branch": False,
                "proves_erdos97": False,
                "changes_local_strongest_result": False,
            },
        }


def audit_external_exact_seven_l0(checkout: Path) -> ExternalExactSevenL0Audit:
    checkout = checkout.resolve()
    normalized_hashes: dict[str, str] = {}
    issues: list[str] = []
    for relative_path, expected_digest in EXPECTED_LF_SHA256.items():
        path = checkout / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"missing external exact-seven artifact: {path}")
        digest = _lf_sha256(path)
        normalized_hashes[relative_path.as_posix()] = digest
        if digest != expected_digest:
            issues.append(f"sha256.{relative_path.as_posix()}")

    generated_schemas: list[dict[str, object]] = []
    generated_e_landings: tuple[tuple[str, str], ...] = ()
    generated_p_landings: tuple[tuple[str, str], ...] = ()
    schema_contract_issues: list[str] = []
    if normalized_hashes[ENUMERATOR.as_posix()] == EXPECTED_LF_SHA256[ENUMERATOR]:
        enumerator = _load_pinned_enumerator(checkout / ENUMERATOR)
        generated_e_landings = tuple(enumerator.e_landings())
        generated_p_landings = tuple(enumerator.p_landings())
        generated_rows = tuple(
            (center, tuple(forced), tuple(fresh))
            for center, forced, fresh in enumerator.ROWS
        )
        if generated_e_landings != EXPECTED_E_LANDINGS:
            issues.append("enumerator.e_landings")
        if generated_p_landings != EXPECTED_P_LANDINGS:
            issues.append("enumerator.p_landings")
        if generated_rows != EXPECTED_ROWS:
            issues.append("enumerator.rows")
        if enumerator.TIMEOUT_MS != EXPECTED_TIMEOUT_MS:
            issues.append("enumerator.timeout_ms")

        for e_pair in EXPECTED_E_LANDINGS:
            for row_pairs in product(
                EXPECTED_P_LANDINGS,
                repeat=len(EXPECTED_ROWS),
            ):
                schema = enumerator.build_schema(e_pair, row_pairs)
                generated_schemas.append(schema)
                schema_contract_issues.extend(
                    _schema_issues(schema, e_pair, row_pairs)
                )
        issues.extend(schema_contract_issues)
    else:
        issues.append("enumerator.execution_skipped_unpinned_source")

    ids = [str(schema.get("id")) for schema in generated_schemas]
    schema_digest = _canonical_schema_sha256(generated_schemas)
    point_distribution = Counter(len(schema["points"]) for schema in generated_schemas)
    if len(generated_schemas) != EXPECTED_SCHEMA_COUNT:
        issues.append("schemas.count")
    if len(ids) != len(set(ids)):
        issues.append("schemas.ids_not_unique")
    if schema_digest != EXPECTED_SCHEMA_SHA256:
        issues.append("schemas.sha256")
    if dict(point_distribution) != EXPECTED_POINT_COUNT_DISTRIBUTION:
        issues.append("schemas.point_count_distribution")
    schema_contract_match = (
        generated_e_landings == EXPECTED_E_LANDINGS
        and generated_p_landings == EXPECTED_P_LANDINGS
        and len(generated_schemas) == EXPECTED_SCHEMA_COUNT
        and len(ids) == len(set(ids))
        and schema_digest == EXPECTED_SCHEMA_SHA256
        and dict(point_distribution) == EXPECTED_POINT_COUNT_DISTRIBUTION
        and not schema_contract_issues
    )


    smoke_results = json.loads((checkout / SMOKE_RESULTS).read_text(encoding="utf-8"))
    if not isinstance(smoke_results, dict):
        raise ValueError(f"expected JSON object: {checkout / SMOKE_RESULTS}")
    smoke_verdicts = {
        str(name): result.get("verdict")
        for name, result in smoke_results.items()
        if isinstance(result, dict)
    }
    if smoke_verdicts != EXPECTED_SMOKE_VERDICTS:
        issues.append("smoke.verdicts")

    tracked_files = _git_tracked_files(checkout)
    named_source_committed = _has_named_source(tracked_files)
    report = _lf_bytes((checkout / REPORT).read_bytes()).decode("utf-8")
    report_status_stale = all(
        marker in report for marker in EXPECTED_REPORT_STALE_MARKERS
    )
    schema_artifact_committed = L0_SCHEMA_ARTIFACT in tracked_files
    census_artifacts = tuple(
        path
        for path in tracked_files
        if path.startswith(f"{L0_ROOT.as_posix()}/")
        and ("ledger" in Path(path).name.lower() or "census" in Path(path).name.lower())
        and path != CENSUS_RUNNER.as_posix()
    )
    if named_source_committed:
        issues.append("provenance.unexpected_named_interior_source")
    if not report_status_stale:
        issues.append("provenance.report_stale_markers")
    if schema_artifact_committed:
        issues.append("provenance.unexpected_l0_schema_artifact")
    if census_artifacts:
        issues.append("provenance.unexpected_census_artifact")

    commit = _git_commit(checkout)
    if commit != EXPECTED_COMMIT:
        issues.append("git.commit")
    expected_match = not issues
    return ExternalExactSevenL0Audit(
        checkout=str(checkout),
        commit=commit,
        normalized_lf_sha256=normalized_hashes,
        schema_summary={
            "scope": "L0_ALL_FRESH_ONLY",
            "e_landings": [list(pair) for pair in generated_e_landings],
            "p_landings": [list(pair) for pair in generated_p_landings],
            "schema_count": len(generated_schemas),
            "unique_id_count": len(set(ids)),
            "canonical_schema_sha256": schema_digest,
            "point_count_distribution": {
                str(count): frequency
                for count, frequency in sorted(point_distribution.items())
            },
            "every_schema_matches_independent_contract": schema_contract_match,
        },
        smoke_summary={
            "recorded_gate_count": len(smoke_verdicts),
            "recorded_verdicts": dict(sorted(smoke_verdicts.items())),
            "recorded_verdicts_match": smoke_verdicts == EXPECTED_SMOKE_VERDICTS,
            "live_replay_by_this_audit": False,
        },
        public_provenance={
            "named_interior_theorem_source_committed": named_source_committed,
            "named_interior_theorem_source_name": NAMED_INTERIOR_SOURCE,
            "public_source_fidelity_complete": named_source_committed,
            "report_status_stale": report_status_stale,
            "l0_schema_artifact_committed": schema_artifact_committed,
            "committed_census_artifacts": list(census_artifacts),
            "full_l0_census_reproducible_from_committed_artifacts": False,
        },
        validation_issues=tuple(issues),
        expected_snapshot_match=expected_match,
    )
