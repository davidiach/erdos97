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
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.ci_sharding import (  # noqa: E402
    SHARD_ALGORITHM,
    select_shard,
    validate_shard,
)


@dataclass(frozen=True)
class AuditCommand:
    """One artifact-audit command and its claim scope."""

    ident: str
    command: tuple[str, ...]
    claim_scope: str


AUDIT_PREFLIGHT_COMMANDS: tuple[AuditCommand, ...] = (
    AuditCommand(
        ident="official_status_freshness",
        command=(
            "python",
            "scripts/check_status_consistency.py",
            "--max-official-status-age-days",
            "90",
        ),
        claim_scope=(
            "Dated official-status consistency preflight for scheduled/manual "
            "artifact audits; does not update the official/global status."
        ),
    ),
    AuditCommand(
        ident="artifact_provenance_manifest",
        command=("python", "scripts/check_artifact_provenance.py"),
        claim_scope=(
            "Generated-artifact provenance manifest preflight; validates "
            "artifact metadata and does not prove Erdos Problem #97."
        ),
    ),
)


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
        ident="n8_independent_obstruction_recheck",
        command=(
            "python",
            "scripts/independent_n8_obstruction_recheck.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "SymPy-free independent cross-check for n=8 cyclic-order counts "
            "and 11 of 15 survivor-class obstructions; repo-local audit "
            "pending external review, not a public theorem claim."
        ),
    ),
    AuditCommand(
        ident="n8_class14_certificate_audit",
        command=(
            "python",
            "scripts/check_n8_class14_certificate.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Focused audit of the n=8 class 14 PB+ED Groebner basis and "
            "strict-interior certificate; repo-local exact obstruction audit "
            "pending external review, not a public theorem claim."
        ),
    ),
    AuditCommand(
        ident="n8_residual_certificate_audit",
        command=(
            "python",
            "scripts/check_n8_residual_certificates.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Focused audit of the n=8 class 3, 4, and 5 duplicate, "
            "collinearity, saturated substitution, and full-PB unit-ideal "
            "certificates; repo-local exact obstruction audit pending external "
            "review, not a public theorem claim."
        ),
    ),
    AuditCommand(
        ident="round2_certificates",
        command=("python", "scripts/check_round2_certificates.py"),
        claim_scope="Fixed-pattern and fixed-order round-two certificate regression checks only.",
    ),
    # Keep promoted replays as separate shardable commands. Nine are low-cost
    # (under roughly five seconds on the reference audit host); the C19
    # catalogue prefilter below is a high-cost full sweep (over two minutes).
    AuditCommand(
        ident="c13_legacy_fixed_order_kalmanson",
        command=(
            "python",
            "scripts/check_kalmanson_certificate.py",
            "data/certificates/c13_sidon_order_survivor_kalmanson_unsat.json",
        ),
        claim_scope=(
            "Exact replay of the legacy C13 certificate for one stored "
            "selected-witness pattern and one fixed cyclic order only; not an "
            "all-order obstruction or proof of Erdos Problem #97."
        ),
    ),
    AuditCommand(
        ident="c19_legacy_fixed_order_kalmanson",
        command=(
            "python",
            "scripts/check_kalmanson_certificate.py",
            "data/certificates/round2/c19_kalmanson_known_order_unsat.json",
        ),
        claim_scope=(
            "Exact replay of the legacy C19 certificate for one fixed "
            "selected-witness cyclic order only; not an all-order obstruction "
            "or proof of Erdos Problem #97."
        ),
    ),
    AuditCommand(
        ident="c19_catalog_prefilter_sweep_288_479",
        command=(
            "python",
            "scripts/sweep_c19_kalmanson_prefix_windows_catalog_prefilter.py",
            "--json",
            "--assert-expected",
        ),
        claim_scope=(
            "Exact prefix-window catalogue prefilter accounting for the stored "
            "C19 index window 288..479; route pruning only, not an all-order "
            "obstruction or proof of Erdos Problem #97."
        ),
    ),
    AuditCommand(
        ident="c19_row_circle_ptolemy_active_set",
        command=(
            "python",
            "scripts/reduce_row_circle_multipliers.py",
            "--snapshot",
            "data/certificates/c19_row_circle_ptolemy_active_set.json",
            "--out",
            "/tmp/c19_multiplier_reduction.json",
            "--assert-expected",
        ),
        claim_scope=(
            "Numerical multiplier reduction for the stored C19 row-circle "
            "Ptolemy active-set snapshot; optimizer diagnostic only, not an "
            "exact obstruction or proof of Erdos Problem #97."
        ),
    ),
    AuditCommand(
        ident="c25_c29_sparse_frontier_probe",
        command=(
            "python",
            "scripts/check_sparse_frontier_kalmanson_escapes.py",
            "--source-artifact",
            "data/certificates/c25_c29_sparse_frontier_probe.json",
            "--check",
            "--assert-expected",
        ),
        claim_scope=(
            "Replay of the fixed-order C25/C29 sparse-frontier probe and input "
            "provenance for the escape audit; diagnostic only, not all-order "
            "evidence, a proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="n9_incidence_frontier_bounded",
        command=(
            "python",
            "scripts/check_n9_incidence_frontier.py",
            "--json",
            "--assert-expected",
        ),
        claim_scope=(
            "Bounded n=9 incidence CSP scan over its configured search limits; "
            "not an unrestricted completeness result, proof of n=9, or proof "
            "of Erdos Problem #97."
        ),
    ),
    AuditCommand(
        ident="n9_phi4_rectangle_trap_legacy",
        command=(
            "python",
            "scripts/check_phi4_rectangle_trap.py",
            "--json",
            "--assert-expected",
        ),
        claim_scope=(
            "Exact rectangle-trap replay for one stored n=9 selected-witness "
            "assignment and cyclic order only; not a proof of n=9 or Erdos "
            "Problem #97."
        ),
    ),
    AuditCommand(
        ident="p18_vertex_circle_order_unsat",
        command=(
            "python",
            "scripts/check_vertex_circle_order_filter.py",
            "--pattern",
            "P18_parity_balanced",
            "--search",
            "--assert-obstructed",
            "--json",
        ),
        claim_scope=(
            "Exact vertex-circle cyclic-order obstruction for the built-in "
            "P18_parity_balanced pattern only; not a transfer to arbitrary "
            "selected-witness patterns or proof of Erdos Problem #97."
        ),
    ),
    AuditCommand(
        ident="p24_cyclic_crossing_unsat",
        command=(
            "python",
            "scripts/check_cyclic_crossing_csp.py",
            "--pattern",
            "P24_parity_balanced",
            "--assert-unsat",
            "--json",
        ),
        claim_scope=(
            "Exact cyclic-crossing CSP obstruction for the built-in "
            "P24_parity_balanced pattern only; not a transfer to arbitrary "
            "selected-witness patterns or proof of Erdos Problem #97."
        ),
    ),
    AuditCommand(
        ident="phi4_frontier_scan",
        command=(
            "python",
            "scripts/check_phi4_frontier_scan.py",
            "--json",
            "--assert-expected",
        ),
        claim_scope=(
            "Exact phi4 filter scan over the enumerated stored frontier cases; "
            "diagnostic coverage only, not frontier completeness, proof of n=9, "
            "or proof of Erdos Problem #97."
        ),
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
        ident="c19_order_cnf_summary",
        command=(
            "python",
            "scripts/export_c19_kalmanson_order_cnf.py",
            "--assert-expected",
            "--check-artifact",
            "reports/c19_kalmanson_order_cnf_summary.json",
        ),
        claim_scope=(
            "Z3-independent DIMACS encoding summary for the stored C19_skew "
            "order clauses; replay target only, not a solver-independent "
            "UNSAT proof or proof of Erdos Problem #97."
        ),
    ),
    AuditCommand(
        ident="c19_compact_vs_legacy_diagnostic",
        command=(
            "python",
            "scripts/analyze_kalmanson_certificates.py",
            "--c19-compact-vs-legacy",
            "--assert-expected",
            "--check-artifact",
            "reports/c19_kalmanson_compact_vs_legacy.json",
        ),
        claim_scope=(
            "Fixed-order C19_skew compact-vs-legacy certificate support "
            "diagnostic only; not an all-order obstruction or proof of "
            "Erdos Problem #97."
        ),
    ),
    AuditCommand(
        ident="c19_proof_tooling_preflight",
        command=(
            "python",
            "scripts/probe_c19_proof_tooling.py",
            "--check-c19-cnf-summary",
            "--json",
        ),
        claim_scope=(
            "Environment and CNF-summary preflight for future C19 "
            "solver-independent proof replay; not proof evidence, not an "
            "UNSAT proof, and not a proof of Erdos Problem #97."
        ),
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
        ident="kalmanson_inverse_pair_templates",
        command=(
            "python",
            "scripts/analyze_kalmanson_inverse_pair_templates.py",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Coefficient-template diagnostic for checked C13/C19 all-order "
            "Kalmanson inverse-pair pilots; not a proof of Erdos Problem #97, "
            "counterexample, or transfer to other selected-witness patterns."
        ),
    ),
    AuditCommand(
        ident="kalmanson_sparse_frontier_templates",
        command=(
            "python",
            "scripts/analyze_kalmanson_sparse_frontier_templates.py",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Coefficient-template availability diagnostic for registered "
            "C25/C29 sparse-frontier patterns; not a cyclic-order search, "
            "proof of Erdos Problem #97, counterexample, or all-order "
            "obstruction."
        ),
    ),
    AuditCommand(
        ident="sparse_frontier_kalmanson_escape_audit",
        command=(
            "python",
            "scripts/check_sparse_frontier_kalmanson_escapes.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Fixed-order C25/C29 negative-control audit for the direct "
            "two-inequality Kalmanson inverse-pair filter; not an all-order "
            "obstruction, geometric realization, proof of Erdos Problem #97, "
            "or counterexample."
        ),
    ),
    AuditCommand(
        ident="speculative_circulant_frontier_obstructions",
        command=(
            "python",
            "scripts/check_speculative_circulant_frontier_obstructions.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Exact cleanup for selected speculative circulant patterns: C45 "
            "is killed as a fixed abstract selected-witness incidence pattern "
            "by the two-circle cap, while C41, C43, C49, and R44 are "
            "fixed-natural-order diagnostics only. No general proof of Erdos "
            "Problem #97 and no counterexample are claimed."
        ),
    ),
    AuditCommand(
        ident="two_parabola_lens_grid_search",
        command=(
            "python",
            "scripts/check_two_parabola_lens_closure_grid.py",
            "--artifact",
            "data/certificates/two_parabola_lens_grid_search.json",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Bounded rational-grid negative control for the opposite-chain "
            "two-parabola lens closure ansatz only; not a proof, not a "
            "counterexample, and not a search over arbitrary real parameters."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_review_pending",
        command=("python", "scripts/check_n9_vertex_circle_exhaustive.py", "--assert-expected", "--json"),
        claim_scope="Review-pending n=9 selected-witness finite-case checker; not an offici