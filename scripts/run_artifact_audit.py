#!/usr/bin/env python3
"""Run the slower artifact audit commands and record reproducibility metadata."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class AuditCommand:
    """One artifact-audit command and its claim scope."""

    ident: str
    command: tuple[str, ...]
    claim_scope: str


AUDIT_COMMANDS: tuple[AuditCommand, ...] = (
    AuditCommand(
        ident="n8_artifact_alignment",
        command=("python", "scripts/independent_check_n8_artifacts.py", "--check", "--json"),
        claim_scope="Repo-local n <= 8 artifact alignment and exact-obstruction audit; not a general proof.",
    ),
    AuditCommand(
        ident="n8_incidence_enumeration",
        command=("python", "scripts/enumerate_n8_incidence.py", "--summary"),
        claim_scope="Repo-local n=8 finite selected-witness incidence enumeration.",
    ),
    AuditCommand(
        ident="n8_exact_survivors",
        command=("python", "scripts/analyze_n8_exact_survivors.py", "--check", "--json"),
        claim_scope="Repo-local n=8 exact survivor obstruction audit pending external review.",
    ),
    AuditCommand(
        ident="round2_certificates",
        command=("python", "scripts/check_round2_certificates.py"),
        claim_scope="Fixed-pattern and fixed-order round-two certificate regression checks only.",
    ),
    AuditCommand(
        ident="c19_fixed_order_compact_kalmanson",
        command=(
            "python",
            "scripts/check_kalmanson_certificate.py",
            "data/certificates/round2/c19_kalmanson_known_order_two_unsat.json",
            "--summary-json",
        ),
        claim_scope="Exact obstruction for one fixed C19_skew cyclic order only.",
    ),
    AuditCommand(
        ident="c19_all_orders_kalmanson_z3",
        command=(
            "python",
            "scripts/check_kalmanson_two_order_z3.py",
            "--certificate",
            "data/certificates/c19_skew_all_orders_kalmanson_z3.json",
            "--assert-unsat",
        ),
        claim_scope="All-order obstruction for one fixed abstract C19_skew selected-witness pattern only.",
    ),
    AuditCommand(
        ident="c19_z3_clause_diagnostic",
        command=(
            "python",
            "scripts/analyze_kalmanson_z3_clauses.py",
            "--assert-expected",
            "--check-artifact",
            "reports/c19_kalmanson_z3_clause_diagnostics.json",
        ),
        claim_scope="Structural diagnostic for the C19_skew all-order Z3 clauses only.",
    ),
    AuditCommand(
        ident="c13_fixed_order_compact_kalmanson",
        command=(
            "python",
            "scripts/check_kalmanson_certificate.py",
            "data/certificates/c13_sidon_order_survivor_kalmanson_two_unsat.json",
            "--summary-json",
        ),
        claim_scope="Exact obstruction for one fixed C13 selected-witness cyclic order only.",
    ),
    AuditCommand(
        ident="c13_all_orders_fixed_pattern",
        command=(
            "python",
            "scripts/check_kalmanson_two_order_search.py",
            "--name",
            "C13_sidon_1_2_4_10",
            "--n",
            "13",
            "--offsets",
            "1,2,4,10",
            "--assert-obstructed",
            "--assert-c13-expected",
            "--json",
        ),
        claim_scope="All-order obstruction for one fixed abstract C13 selected-witness pattern only.",
    ),
    AuditCommand(
        ident="n9_vertex_circle_review_pending",
        command=("python", "scripts/check_n9_vertex_circle_exhaustive.py", "--assert-expected", "--json"),
        claim_scope="Review-pending n=9 selected-witness finite-case checker; not an official/global status update.",
    ),
    AuditCommand(
        ident="n9_vertex_circle_local_core_packet",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_local_core_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Compact replay packet for n=9 vertex-circle local-core motif "
            "representatives; not a proof of n=9 or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_core_templates",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_core_templates.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Template diagnostic for n=9 vertex-circle local-core motif "
            "representatives; not a proof of n=9 or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_frontier_motif_classification",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_frontier_motif_classification.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Classification of the 184 n=9 pre-vertex-circle assignments by "
            "motif family and local-core template; not a proof of n=9 or "
            "independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_self_edge_path_join",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_self_edge_path_join.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Assignment-level join for the 158 n=9 self-edge frontier "
            "assignments and transformed equality paths; not a proof of n=9 "
            "or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_self_edge_template_packet",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_self_edge_template_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Template-level packet for the 9 n=9 self-edge local-core "
            "templates and their canonical family certificates; not a proof "
            "of n=9 or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_strict_cycle_path_join",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_strict_cycle_path_join.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Assignment-level join for the 26 n=9 strict-cycle frontier "
            "assignments and transformed local-core quotient cycles; not a "
            "proof of n=9 or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_strict_cycle_template_packet",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_strict_cycle_template_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Template-level packet for the 3 n=9 strict-cycle local-core "
            "templates; not a proof of n=9, counterexample, or independent "
            "review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_template_lemma_catalog",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_template_lemma_catalog.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Derived lemma-candidate catalog for the 12 n=9 vertex-circle "
            "local-core templates; not a proof of n=9, counterexample, "
            "or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_t01_self_edge_lemma_packet",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Focused T01/F09 n=9 self-edge local lemma packet; proof-mining "
            "scaffolding only, not a proof of n=9, counterexample, or "
            "independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_t02_self_edge_lemma_packet",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Focused T02 multi-family n=9 self-edge local lemma packet; "
            "proof-mining scaffolding only, not a proof of n=9, "
            "counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_t03_self_edge_lemma_packet",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Focused T03 multi-family n=9 self-edge local lemma packet; "
            "proof-mining scaffolding only, not a proof of n=9, "
            "counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_t10_strict_cycle_lemma_packet",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Focused T10/F12 n=9 strict-cycle local lemma packet; "
            "proof-mining scaffolding only, not a proof of n=9, "
            "counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_t11_strict_cycle_lemma_packet",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_t11_strict_cycle_lemma_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Focused T11/F07 n=9 strict-cycle local lemma packet; "
            "proof-mining scaffolding only, not a proof of n=9, "
            "counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_t12_strict_cycle_lemma_packet",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Focused T12/F16 n=9 strict-cycle local lemma packet; "
            "proof-mining scaffolding only, not a proof of n=9, "
            "counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_base_apex_low_excess_ledgers",
        command=("python", "scripts/check_n9_base_apex_low_excess_ledgers.py", "--check", "--json"),
        claim_scope=(
            "Focused n=9 base-apex low-excess bookkeeping; "
            "not a proof of n=9, not a counterexample, "
            "and not a global status update."
        ),
    ),
    AuditCommand(
        ident="n9_base_apex_escape_budget",
        command=("python", "scripts/check_n9_base_apex_escape_budget.py", "--check", "--json"),
        claim_scope=(
            "Focused n=9 base-apex escape-budget bookkeeping; "
            "not a proof of n=9, not a counterexample, and not a global status update."
        ),
    ),
    AuditCommand(
        ident="n9_selected_baseline_escape_budget_overlay",
        command=(
            "python",
            "scripts/check_n9_selected_baseline_escape_budget_overlay.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Focused n=9 selected-baseline escape-budget overlay bookkeeping; "
            "not a proof of n=9, not a counterexample, not a geometric "
            "realizability test, and not a global status update."
        ),
    ),
    AuditCommand(
        ident="n9_base_apex_d3_escape_slice",
        command=("python", "scripts/check_n9_d3_escape_slice.py", "--check", "--json"),
        claim_scope=(
            "Focused n=9 base-apex D=3,r=3 coupled escape-slice bookkeeping; "
            "not a proof of n=9, not a counterexample, not a geometric "
            "realizability test, and not a global status update."
        ),
    ),
    AuditCommand(
        ident="n9_base_apex_low_excess_escape_ladder",
        command=(
            "python",
            "scripts/check_n9_base_apex_low_excess_escape_ladder.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Focused n=9 base-apex low-excess minimal escape-slice ladder "
            "bookkeeping; not a proof of n=9, not a counterexample, not a "
            "geometric realizability test, and not a global status update."
        ),
    ),
    AuditCommand(
        ident="n9_base_apex_low_excess_escape_crosswalk",
        command=(
            "python",
            "scripts/check_n9_base_apex_low_excess_escape_crosswalk.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Focused n=9 base-apex low-excess profile/escape crosswalk "
            "bookkeeping; not a proof of n=9, not a counterexample, not a "
            "geometric realizability test, and not a global status update."
        ),
    ),
    AuditCommand(
        ident="n9_row_ptolemy_product_cancellations",
        command=(
            "python",
            "scripts/check_n9_row_ptolemy_product_cancellations.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Focused n=9 row-Ptolemy product-cancellation bookkeeping for "
            "fixed row order; not a proof of n=9, counterexample, geometric "
            "realizability test, or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_row_ptolemy_family_signatures",
        command=(
            "python",
            "scripts/check_n9_row_ptolemy_family_signatures.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Derived n=9 row-Ptolemy family-signature and local-core shape "
            "crosswalk diagnostic for fixed row order; not a proof of n=9, "
            "counterexample, orderless obstruction, or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_row_ptolemy_order_sensitivity",
        command=(
            "python",
            "scripts/check_n9_row_ptolemy_order_sensitivity.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Derived n=9 row-Ptolemy order-sensitivity diagnostic for sampled "
            "representatives; not a proof of n=9, counterexample, all-order "
            "obstruction, orderless obstruction, or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_row_ptolemy_order_admissible_census",
        command=(
            "python",
            "scripts/check_n9_row_ptolemy_order_admissible_census.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Derived n=9 row-Ptolemy admissible-order census for existing "
            "fixed-order hit assignments; not a proof of n=9, counterexample, "
            "all-order obstruction, orderless obstruction, geometric "
            "realizability count, or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_row_ptolemy_admissible_gap_replay",
        command=(
            "python",
            "scripts/check_n9_row_ptolemy_admissible_gap_replay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Replay of the two zero-certificate n=9 row-Ptolemy admissible "
            "assignment-order records; not a proof of n=9, counterexample, "
            "all-order obstruction, orderless obstruction, geometric "
            "realizability count, or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_row_ptolemy_gap_self_edge_cores",
        command=(
            "python",
            "scripts/check_n9_row_ptolemy_gap_self_edge_cores.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Compact self-edge core certificates for the two zero-certificate "
            "n=9 row-Ptolemy admissible assignment-order records; not a proof "
            "of n=9, counterexample, all-order obstruction, orderless "
            "obstruction, geometric realizability count, or official/global "
            "status update."
        ),
    ),
    AuditCommand(
        ident="n10_vertex_circle_singleton_draft",
        command=(
            "python",
            "scripts/check_n10_vertex_circle_singletons.py",
            "--assert-expected",
            "--spot-check-row0",
            "0",
            "--spot-check-row0",
            "63",
            "--spot-check-row0",
            "125",
        ),
        claim_scope=(
            "Draft review-pending n=10 singleton-slice artifact selected spot-checks; "
            "not a source-of-truth finite-case result or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n10_secondary_singleton_replay",
        command=(
            "python",
            "scripts/check_n10_secondary_singleton_replay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Secondary first-five n=10 singleton replay cross-check with an additional "
            "triple-intersection filter; not a proof of n=10, a source-of-truth "
            "finite-case result, or an official/global status update."
        ),
    ),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_git(args: Sequence[str]) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def command_text(command: Sequence[str]) -> str:
    return " ".join(command)


def run_audit_command(command: AuditCommand, output_dir: Path) -> dict[str, Any]:
    command_dir = output_dir / "commands"
    command_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = command_dir / f"{command.ident}.stdout"
    stderr_path = command_dir / f"{command.ident}.stderr"

    started_at = utc_now()
    start = time.perf_counter()
    result = subprocess.run(
        command.command,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    elapsed_seconds = time.perf_counter() - start
    finished_at = utc_now()

    stdout_path.write_bytes(result.stdout)
    stderr_path.write_bytes(result.stderr)
    combined_output = result.stdout + result.stderr

    return {
        "id": command.ident,
        "command": command_text(command.command),
        "claim_scope": command.claim_scope,
        "started_at_utc": started_at,
        "finished_at_utc": finished_at,
        "elapsed_seconds": round(elapsed_seconds, 6),
        "exit_code": result.returncode,
        "stdout_path": stdout_path.relative_to(output_dir).as_posix(),
        "stderr_path": stderr_path.relative_to(output_dir).as_posix(),
        "stdout_sha256": sha256_bytes(result.stdout),
        "stderr_sha256": sha256_bytes(result.stderr),
        "combined_output_sha256": sha256_bytes(combined_output),
        "stdout_bytes": len(result.stdout),
        "stderr_bytes": len(result.stderr),
    }


def build_summary(output_dir: Path, commands: Sequence[AuditCommand]) -> dict[str, Any]:
    started_at = utc_now()
    command_results = [run_audit_command(command, output_dir) for command in commands]
    finished_at = utc_now()
    dependency_snapshot = REPO_ROOT / "requirements-lock.txt"

    return {
        "type": "erdos97_artifact_audit_run_v1",
        "claim_scope": (
            "Artifact audit for repo-local finite-case and fixed-pattern/fixed-order "
            "certificates; passing does not prove Erdos Problem #97."
        ),
        "does_not_claim": [
            "general proof of Erdos Problem #97",
            "counterexample to Erdos Problem #97",
            "official/global status change",
            "independent external mathematical review",
        ],
        "started_at_utc": started_at,
        "finished_at_utc": finished_at,
        "verified": all(record["exit_code"] == 0 for record in command_results),
        "repo": {
            "commit": run_git(("rev-parse", "HEAD")),
            "status_porcelain": run_git(("status", "--porcelain")),
        },
        "python": {
            "executable": sys.executable,
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "dependency_snapshot": {
            "path": dependency_snapshot.relative_to(REPO_ROOT).as_posix(),
            "sha256": sha256_file(dependency_snapshot),
        },
        "commands": command_results,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifact-audit-results"),
        help="Directory for summary.json and per-command stdout/stderr files.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = REPO_ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = build_summary(output_dir, AUDIT_COMMANDS)
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
