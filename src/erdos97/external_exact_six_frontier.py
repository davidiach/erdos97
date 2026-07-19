"""Fail-closed audit of the external exact-six research frontier.

This module checks source and artifact provenance plus shallow status fields.
It does not build Lean, replay Farkas arithmetic, or validate the external
repository's mathematical correspondence claims.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

from erdos97.external_frontier_audit import _git_commit


EXPECTED_COMMIT = "b6f8af856dd1d44ba9e11ea43033d14e3f214f9e"

EXACT_SIX_SOURCE = Path(
    "lean/Erdos9796Proof/P97/ATail/ParentExactFiveExactSix.lean"
)
SCHEMA_BANK = Path(
    "scratch/atail-force/exact6-allcenter-capaware-gate/"
    "combined_round1_round2_minimized_schema_bank.json"
)
CUT_BANK = Path(
    "scratch/atail-force/exact6-integrated-milp/"
    "global-cuts-cross-20260718.jsonl"
)
INITIAL_DIRECT_RESULT = Path(
    "scratch/atail-force/exact6-integrated-milp/direct-alive/"
    "sharesFirstAtSource.kalmanson.d14.json"
)
PORTFOLIO_SUMMARY = Path(
    "scratch/atail-force/exact6-integrated-milp/"
    "direct-portfolio-d14-20260718/summary.json"
)
BARE_N10_RESULT = Path(
    "scratch/atail-force/variable-card-positive-dual-proof-audit/"
    "exact-z3-allrows-n10-20260718.json"
)
BARE_N11_RESULT = Path(
    "scratch/atail-force/variable-card-positive-dual-proof-audit/"
    "exact-z3-allrows-n11-20260718.json"
)

EXPECTED_LF_SHA256 = {
    EXACT_SIX_SOURCE: (
        "8c7fb90c8023f96b72df19ee9801597e5a22eaeef094da497e1fbdc63f033952"
    ),
    SCHEMA_BANK: (
        "25aac2f8f0b2bc89c37610737aa5df55cb01b58207fe9810dd5cf5935e272b2a"
    ),
    CUT_BANK: (
        "92a88957465e7d9e3c47392e8748ad6a8da05089b75e14abb7b16181a17e7288"
    ),
    INITIAL_DIRECT_RESULT: (
        "320994ca63eae9038e1808b1bff561353e886cc8d4210150b9b8e276f8d25559"
    ),
    PORTFOLIO_SUMMARY: (
        "344e5c57fd1ab023217792ccbdbdf614e11ee3cf85ef855e2bee31a46d64f863"
    ),
    BARE_N10_RESULT: (
        "5782ba1bc2b8fa037a4e252af4cded43608c278f596ef91473398bd36cc509c5"
    ),
    BARE_N11_RESULT: (
        "59cce6bd08ba349d25acef063d08dc15c66ec695da5c48fe4301d6d5486b0cde"
    ),
}

EXPECTED_SOURCE_MARKERS = (
    "theorem false_of_fullParentExactFiveAllReverseData_"
    "of_secondCap_card_eq_six",
    "theorem false_of_fullParentExactFive_"
    "of_secondCap_card_eq_six_and_mutualConsumer",
    "mutualFalse : FullParentExactFiveMutualData L profile",
)

EXPECTED_ORBITS = frozenset(
    {
        "continuationOrder",
        "reverseContinuationOrder",
        "sharesFirstAtSource",
        "sharesFirstAtTarget",
        "sharesSecondAtSource",
        "sharesSecondAtTarget",
        "fourDistinct",
    }
)


def _lf_bytes(data: bytes) -> bytes:
    """Normalize checkout line endings to the committed LF convention."""
    return data.replace(b"\r\n", b"\n")


def _lf_sha256(path: Path) -> str:
    return sha256(_lf_bytes(path.read_bytes())).hexdigest()


def _missing_markers(source: str) -> tuple[str, ...]:
    return tuple(marker for marker in EXPECTED_SOURCE_MARKERS if marker not in source)


def _read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _summarize_cut_bank(path: Path) -> dict[str, int]:
    cut_count = 0
    shell_conditioned_count = 0
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line:
            continue
        record = json.loads(line)
        if not isinstance(record, dict):
            raise ValueError(f"cut line {line_number} is not an object")
        constraints = record.get("constraints")
        if not isinstance(constraints, list):
            raise ValueError(f"cut line {line_number} lacks constraints")
        cut_count += 1
        if any(
            isinstance(item, dict)
            and str(item.get("name", "")).startswith("shell_")
            for item in constraints
        ):
            shell_conditioned_count += 1
    return {
        "cut_count": cut_count,
        "shell_conditioned_count": shell_conditioned_count,
    }


@dataclass(frozen=True)
class ExternalExactSixFrontierAudit:
    checkout: str
    commit: str | None
    normalized_lf_sha256: dict[str, str]
    missing_source_markers: tuple[str, ...]
    artifact_summary: dict[str, object]
    validation_issues: tuple[str, ...]
    expected_snapshot_match: bool

    def to_json(self) -> dict[str, object]:
        return {
            "type": "external_exact_six_frontier_audit",
            "trust": "EXTERNAL_PROVENANCE_AND_STATUS_AUDIT_ONLY",
            "checkout": self.checkout,
            "commit": self.commit,
            "normalized_lf_sha256": dict(
                sorted(self.normalized_lf_sha256.items())
            ),
            "missing_source_markers": list(self.missing_source_markers),
            "artifact_summary": self.artifact_summary,
            "validation_issues": list(self.validation_issues),
            "expected_snapshot": {
                "commit": EXPECTED_COMMIT,
                "normalized_lf_sha256": {
                    path.as_posix(): digest
                    for path, digest in EXPECTED_LF_SHA256.items()
                },
            },
            "expected_snapshot_match": self.expected_snapshot_match,
            "frontier": {
                "closed_slice": "all-reverse exact-six",
                "open_slice": "mutual exact-six",
                "active_surface": (
                    "total all-center K4 plus source-indexed critical rows"
                ),
                "aggregate_kalmanson_theorem": "CONJECTURAL",
                "direct_exact_smt_orbits": "UNKNOWN",
            },
            "claims": {
                "external_lean_build_checked": False,
                "external_farkas_replay_checked_by_this_script": False,
                "proves_mutual_exact_six": False,
                "proves_erdos97": False,
                "changes_local_strongest_result": False,
            },
        }


def audit_external_exact_six_frontier(
    checkout: Path,
) -> ExternalExactSixFrontierAudit:
    checkout = checkout.resolve()
    normalized_hashes: dict[str, str] = {}
    for relative_path in EXPECTED_LF_SHA256:
        path = checkout / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"missing external frontier artifact: {path}")
        normalized_hashes[relative_path.as_posix()] = _lf_sha256(path)

    source = (checkout / EXACT_SIX_SOURCE).read_text(encoding="utf-8")
    missing_markers = _missing_markers(source)
    schema_bank = _read_json(checkout / SCHEMA_BANK)
    cut_summary = _summarize_cut_bank(checkout / CUT_BANK)
    initial = _read_json(checkout / INITIAL_DIRECT_RESULT)
    portfolio = _read_json(checkout / PORTFOLIO_SUMMARY)
    bare_n10 = _read_json(checkout / BARE_N10_RESULT)
    bare_n11 = _read_json(checkout / BARE_N11_RESULT)

    issues: list[str] = []
    expected_schema_fields = {
        "schema": "p97-exact6-allcenter-minimized-metric-schema-bank-v1",
        "unique_schema_count": 263,
        "compact_schema_count_k_le_8": 30,
        "minimal_core_count": 263,
    }
    for key, expected in expected_schema_fields.items():
        if schema_bank.get(key) != expected:
            issues.append(f"schema_bank.{key}")

    if cut_summary != {
        "cut_count": 12509,
        "shell_conditioned_count": 302,
    }:
        issues.append("cut_bank.summary")

    if initial.get("orbit") != "sharesFirstAtSource":
        issues.append("initial_direct.orbit")
    if initial.get("epistemic_status") != "EXACT_SMT_UNKNOWN":
        issues.append("initial_direct.epistemic_status")
    initial_solver = initial.get("solver")
    if not isinstance(initial_solver, dict) or initial_solver.get("status") != "unknown":
        issues.append("initial_direct.solver_status")

    portfolio_orbits = portfolio.get("orbits")
    if not isinstance(portfolio_orbits, list):
        portfolio_orbits = []
        issues.append("portfolio.orbits")
    direct_orbits = set(map(str, portfolio_orbits)) | {"sharesFirstAtSource"}
    if direct_orbits != EXPECTED_ORBITS:
        issues.append("direct_orbits.coverage")
    if portfolio.get("member_count") != 6:
        issues.append("portfolio.member_count")
    if portfolio.get("statuses") != ["unknown"]:
        issues.append("portfolio.statuses")
    if portfolio.get("epistemic_status") != (
        "EXACT_DIRECT_PORTFOLIO_COMPLETE_NO_ALIVE_NO_UNSAT_PROOF"
    ):
        issues.append("portfolio.epistemic_status")
    members = portfolio.get("members")
    if not isinstance(members, list) or any(
        not isinstance(member, dict) or member.get("alive_path") is not None
        for member in members
    ):
        issues.append("portfolio.alive_sidecars")

    if bare_n10.get("n") != 10 or bare_n10.get("status") != "UNSAT":
        issues.append("bare_all_center.n10")
    if bare_n11.get("n") != 11 or bare_n11.get("status") != "UNKNOWN":
        issues.append("bare_all_center.n11")

    commit = _git_commit(checkout)
    hashes_match = all(
        normalized_hashes[path.as_posix()] == digest
        for path, digest in EXPECTED_LF_SHA256.items()
    )
    expected_match = (
        commit == EXPECTED_COMMIT
        and hashes_match
        and not missing_markers
        and not issues
    )
    artifact_summary: dict[str, object] = {
        "schema_bank": {
            key: schema_bank.get(key) for key in expected_schema_fields
        },
        "cut_bank": cut_summary,
        "direct_exact_smt": {
            "orbits": sorted(direct_orbits),
            "status": "UNKNOWN",
            "alive_count": 0,
        },
        "bare_all_center": {
            "n10_status": bare_n10.get("status"),
            "n11_status": bare_n11.get("status"),
        },
    }
    return ExternalExactSixFrontierAudit(
        checkout=str(checkout),
        commit=commit,
        normalized_lf_sha256=normalized_hashes,
        missing_source_markers=missing_markers,
        artifact_summary=artifact_summary,
        validation_issues=tuple(issues),
        expected_snapshot_match=expected_match,
    )
