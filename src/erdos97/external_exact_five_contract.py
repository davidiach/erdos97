"""Fail-closed audit of the external exact-five occurrence contract.

This module checks source provenance and named contract fields only. It does
not build Lean or validate the external mathematics.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from erdos97.external_frontier_audit import _git_commit


EXPECTED_COMMIT = "5e43baeb6fb5f5c51745e05696a7f1b29bf52b0a"

PARENT_SOURCE = Path(
    "lean/Erdos9796Proof/P97/ATail/LargeOppositeCapsBiApexSurface.lean"
)
ROLE_SOURCE = Path(
    "lean/Erdos9796Proof/P97/ATail/FirstApexShellRole.lean"
)
TRANSITION_SOURCE = Path(
    "lean/Erdos9796Proof/P97/ATail/"
    "LargeCapUniqueFivePhysicalOmissionTransitionGlobal.lean"
)
ASSEMBLER_SOURCE = Path(
    "lean/Erdos9796Proof/P97/ATail/ParentExactFiveAssembler.lean"
)

EXPECTED_SOURCE_SHA256 = {
    PARENT_SOURCE: (
        "40dffe39fa980b23baeca91809d32f5f2ae3d6faa7fded1a1a9c1f096f8d331b"
    ),
    ROLE_SOURCE: (
        "b2ac9b20c6ef1db57c3dcdcea9289cf1b3a6074eb325297c398c411d555fff03"
    ),
    TRANSITION_SOURCE: (
        "7651c4312bda034174a461960da50b25270abe1509931f33822c11e50b12babc"
    ),
    ASSEMBLER_SOURCE: (
        "0082e83a319af8b5e8484967c1a88eadf63bc4a0a7876e571855b60762c683ff"
    ),
}

EXPECTED_MARKERS = {
    PARENT_SOURCE: (
        "structure FrontierLargeOppositeCapsBiApexRobustResidual",
        "firstOppCap_card_ge_six",
        "secondOppCap_card_ge_six",
        "carrier_card_ge_fourteen",
    ),
    ROLE_SOURCE: (
        "structure FirstApexShellRolePacket",
        "sameRadius_six",
        "distinctRadius_disjoint",
        "firstApex_double_survives",
        "secondApex_double_survives",
    ),
    TRANSITION_SOURCE: (
        "def transitionReverseOutsidePair",
        "theorem transitionReverseOutsidePair_card_eq_two",
        "theorem transitionReverseOutsidePair_subset_complement",
        "theorem false_of_transitionReverseOutsidePair_coRadial_firstApex",
    ),
    ASSEMBLER_SOURCE: (
        "structure FullParentExactFiveAllReverseData",
        "firstApexRoles : FirstApexShellRolePacket",
        "allReverse :",
        "cycle_period : cycle.period = 3",
        "sharedOrder :",
        "abbrev FirstApexCoRadialTransitionReversePairOccurrence",
        "dist S.oppApex1 a = dist S.oppApex1 b",
        "theorem false_of_fullParentExactFiveAllReverseData_of_firstApexOccurrence",
        "theorem false_of_fullParentExactFive_of_relationConsumers",
    ),
}


@dataclass(frozen=True)
class ExternalExactFiveContractAudit:
    checkout: str
    commit: str | None
    source_sha256: dict[str, str]
    missing_markers: dict[str, tuple[str, ...]]
    expected_snapshot_match: bool

    def to_json(self) -> dict[str, object]:
        return {
            "type": "external_exact_five_occurrence_contract_audit",
            "trust": "EXTERNAL_PROVENANCE_AUDIT_ONLY",
            "checkout": self.checkout,
            "commit": self.commit,
            "source_sha256": dict(sorted(self.source_sha256.items())),
            "missing_markers": {
                path: list(markers)
                for path, markers in sorted(self.missing_markers.items())
            },
            "expected_snapshot": {
                "commit": EXPECTED_COMMIT,
                "source_sha256": {
                    path.as_posix(): digest
                    for path, digest in EXPECTED_SOURCE_SHA256.items()
                },
            },
            "expected_snapshot_match": self.expected_snapshot_match,
            "contract": {
                "parent": (
                    "FrontierLargeOppositeCapsBiApexRobustResidual"
                ),
                "all_reverse_packet": "FullParentExactFiveAllReverseData",
                "period": 3,
                "reverse_pair_cardinality": 2,
                "target": (
                    "FirstApexCoRadialTransitionReversePairOccurrence"
                ),
                "proved_consumer": (
                    "false_of_fullParentExactFiveAllReverseData_"
                    "of_firstApexOccurrence"
                ),
            },
            "claims": {
                "external_lean_build_checked": False,
                "external_mathematics_checked": False,
                "proves_occurrence": False,
                "proves_erdos97": False,
                "changes_local_strongest_result": False,
            },
        }


def _missing_markers(source: str, markers: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(marker for marker in markers if marker not in source)


def audit_external_exact_five_contract(
    checkout: Path,
) -> ExternalExactFiveContractAudit:
    checkout = checkout.resolve()
    commit = _git_commit(checkout)
    source_hashes: dict[str, str] = {}
    missing_by_path: dict[str, tuple[str, ...]] = {}

    for relative_path, expected_digest in EXPECTED_SOURCE_SHA256.items():
        source_path = checkout / relative_path
        if not source_path.is_file():
            raise FileNotFoundError(
                f"missing external contract source: {source_path}"
            )
        source_bytes = source_path.read_bytes()
        source = source_bytes.decode("utf-8")
        path_key = relative_path.as_posix()
        source_hashes[path_key] = sha256(source_bytes).hexdigest()
        missing = _missing_markers(source, EXPECTED_MARKERS[relative_path])
        if missing:
            missing_by_path[path_key] = missing

    expected_match = (
        commit == EXPECTED_COMMIT
        and not missing_by_path
        and all(
            source_hashes[path.as_posix()] == expected_digest
            for path, expected_digest in EXPECTED_SOURCE_SHA256.items()
        )
    )
    return ExternalExactFiveContractAudit(
        checkout=str(checkout),
        commit=commit,
        source_sha256=source_hashes,
        missing_markers=missing_by_path,
        expected_snapshot_match=expected_match,
    )
