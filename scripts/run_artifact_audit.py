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
            "collinearity, and Groebner-y2 certificates; repo-local exact "
            "obstruction audit pending external review, not a public theorem claim."
        ),
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
        claim_scope="Review-pending n=9 selected-witness finite-case checker; not an official/global status update.",
    ),
    AuditCommand(
        ident="n9_vertex_circle_minimal_cores",
        command=(
            "python",
            "scripts/n9_vertex_circle_minimal_cores.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Independent implementation-level minimal obstruction-core catalog "
            "for the 184 review-pending n=9 vertex-circle frontier systems; "
            "not a proof of n=9, completed independent review, or an "
            "official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_compact_brancher",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_compact_brancher.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Compact independent regeneration of the review-pending n=9 "
            "selected-witness frontier and vertex-circle quotient "
            "obstruction; audit/replay aid only, not completed independent "
            "review, not a proof of n=9, not a proof of Erdos Problem #97, "
            "and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="n9_kalmanson_selfedge",
        command=(
            "python",
            "scripts/check_n9_kalmanson_selfedge.py",
            "--verify-certificate",
            "data/certificates/n9_kalmanson_selfedge.json",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Review-pending n=9 selected-witness Kalmanson self-edge "
            "certificate replay only; not a proof of n=9, counterexample, "
            "independent review completion, or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_kalmanson_selfedge_independent_replay",
        command=(
            "python",
            "scripts/check_n9_kalmanson_selfedge_independent_replay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Independent stored-input replay for the review-pending n=9 "
            "Kalmanson self-edge certificate; checks row shape, incidence "
            "filters, selected-distance quotienting, stored self-edges, and "
            "digest agreement only. It is not brancher coverage, a proof of "
            "n=9, independent review completion, or an official/global status "
            "update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_obstruction_shapes",
        command=(
            "python",
            "scripts/analyze_n9_vertex_circle_obstruction_shapes.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Review-pending n=9 obstruction-shape diagnostic for the stored "
            "pre-vertex-circle frontier; not a proof of n=9, counterexample, "
            "independent review completion, or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_motif_families",
        command=(
            "python",
            "scripts/analyze_n9_vertex_circle_motif_families.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Review-pending n=9 motif-family diagnostic for the stored "
            "pre-vertex-circle frontier; not a proof of n=9, counterexample, "
            "independent review completion, or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_inversive_incidence_pilot",
        command=(
            "python",
            "scripts/check_n9_inversive_incidence_pilot.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Inversive point-line incidence diagnostic on the 184 regenerated "
            "n=9 pre-vertex-circle frontier assignments; not a proof of n=9, "
            "counterexample, independent review completion, or global status "
            "update."
        ),
    ),
    AuditCommand(
        ident="n9_turn_inequality_frontier",
        command=(
            "python",
            "scripts/check_n9_turn_inequality_frontier.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Review-pending n=9 turn-inequality frontier replay with stored "
            "integer dual certificates; not a proof of n=9, counterexample, "
            "geometric lemma review, or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_input_audit",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_input_audit.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Input-data audit for the review-pending n=9 vertex-circle "
            "artifact; checks stored row0 coverage and summary arithmetic "
            "only, not a brancher rerun, proof of n=9, counterexample, or "
            "official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_incidence_filters",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_incidence_filters.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Row-level incidence filter audit for n=9 two-overlap crossing, "
            "witness-pair cap, and selected-indegree cap; not brancher "
            "replay, strict-edge geometry, quotient soundness, proof of n=9, "
            "counterexample, or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_branch_options",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_branch_options.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Fixed-order branch-option predicate audit for n=9 helper "
            "options and maintained count arrays; not dynamic-MRO branch "
            "coverage, strict-edge geometry, proof of n=9, counterexample, "
            "or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_dynamic_mro_choices",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_dynamic_mro_choices.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Dynamic minimum-remaining-options choice audit for n=9 center "
            "selection and all remaining-center option counts; not filter "
            "soundness, strict-edge geometry, proof of n=9, counterexample, "
            "or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_mro_branching_replay",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_mro_branching_replay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Fixed-center-order replay audit for the review-pending n=9 "
            "vertex-circle artifact; checks dynamic-MRO branching agreement "
            "only, not filter soundness, proof of n=9, counterexample, or "
            "official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_frontier_coverage_crosswalk",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Dynamic no-vertex-circle frontier coverage crosswalk against "
            "the stored n=9 frontier motif-classification artifact; not "
            "filter soundness, strict-edge geometry, proof of n=9, "
            "counterexample, or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_strict_edge_geometry",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_strict_edge_geometry.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Strict-edge geometry rule audit for every candidate n=9 "
            "selected row; not row coverage, brancher coverage, quotient "
            "soundness, proof of n=9, counterexample, or official/global "
            "status update."
        ),
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
        ident="n9_vertex_circle_local_core_subset_audit",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_local_core_subset_audit.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Cross-artifact audit checking compact n=9 local cores are "
            "subsets of stored full motif representatives and obstruct by "
            "direct quotient replay; not frontier coverage, proof of n=9, "
            "counterexample, or official/global status update."
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
        ident="n9_high_risk_frontier_packet",
        command=(
            "python",
            "scripts/check_n9_high_risk_frontier_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Mutual-edge-triangle slice of the n=9 pre-vertex-circle "
            "frontier with fixed-row radius-blocker and vertex-circle replay; "
            "not a proof of n=9, counterexample, or independent review "
            "completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_dihedral_orbit_audit",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_dihedral_orbit_audit.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Second-source dihedral orbit bookkeeping audit for the stored "
            "n=9 motif-family and frontier-classification artifacts; not "
            "frontier coverage, filter soundness, proof of n=9, "
            "counterexample, or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_motif_obstruction_audit",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_motif_obstruction_audit.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Stored-certificate audit for the 16 n=9 motif representative "
            "self-edge paths and strict-cycle records; not frontier coverage, "
            "brancher soundness, proof of n=9, counterexample, or "
            "official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_frontier_comparison",
        command=(
            "python",
            "scripts/compare_n9_vertex_circle_frontier.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Comparison of exact n=9 local-core embeddings against recorded "
            "P18/C19 frontier patterns and vertex-circle behavior; not a "
            "proof of n=9, counterexample, transfer theorem, or "
            "official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_frontier_assignment_audit",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_frontier_assignment_audit.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Stored-frontier assignment audit for n=9 row shape, row-pair "
            "crossing, witness-pair capacity, and selected-indegree capacity; "
            "not frontier coverage, brancher soundness, strict-edge "
            "geometry, proof of n=9, counterexample, or official/global "
            "status update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_quotient_soundness",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_quotient_soundness.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Selected-distance quotient status agreement audit for stored "
            "n=9 local-core rows and frontier assignments; not row coverage, "
            "brancher coverage, strict-edge geometry, proof of n=9, "
            "counterexample, or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_closed_descent_packet",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_closed_descent_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Closed-descent reformulation of stored n=9 local-core quotient "
            "obstructions; not local-lemma completeness, brancher coverage, "
            "strict-edge geometry, proof of n=9, counterexample, bridge proof, "
            "or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_partial_pruning",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_partial_pruning.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Stored-frontier subset replay for n=9 vertex-circle partial "
            "pruning; checks monotone obstruction persistence and "
            "checker/replay status agreement only, not frontier coverage, "
            "brancher soundness, strict-edge geometry, proof of n=9, "
            "counterexample, or official/global status update."
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
        ident="n9_vertex_circle_local_lemmas",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_local_lemmas.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Proof-mining scan for reusable n-independent n=9 vertex-circle "
            "local lemmas; not a proof of n=9, counterexample, or "
            "independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_focused_packet_catalog_audit",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "JSON-only cross-artifact audit for the 12 focused n=9 "
            "local-lemma packets against the source template packets, "
            "template catalog, and aggregate focused-note crosschecks; not "
            "packet soundness, local-lemma completeness, frontier coverage, "
            "proof of n=9, counterexample, or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_focused_minireplay_crosswalk",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "JSON-only cross-artifact audit joining the 12 focused n=9 "
            "local-lemma packets to their mini-replay artifacts; not "
            "mini-replay soundness, packet soundness, local-lemma "
            "completeness, frontier coverage, proof of n=9, counterexample, "
            "or official/global status update."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_local_lemma_simple_replay",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_local_lemma_simple_replay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Second-source packet-level audit for aggregate n=9 vertex-circle "
            "local-lemma coverage; not a proof of n=9, counterexample, or "
            "independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_local_lemma_replay_crosswalk",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Cross-artifact audit joining the aggregate n=9 local-lemma scan "
            "to the simple packet replay; not a proof of n=9, counterexample, "
            "or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_exhaustive_local_lemma_crosswalk",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Cross-artifact audit joining the review-pending n=9 exhaustive "
            "count artifact to the local-lemma replay chain; not a proof of "
            "n=9, counterexample, or independent review completion."
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
        ident="n9_t01_self_edge_minireplay",
        command=(
            "python",
            "scripts/check_n9_t01_self_edge_minireplay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Minimal input-data replay of the focused T01/F09 self-edge "
            "local lemma packet; proof-mining scaffolding only, not a proof "
            "of n=9, counterexample, or independent review completion."
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
        ident="n9_t02_self_edge_minireplay",
        command=(
            "python",
            "scripts/check_n9_t02_self_edge_minireplay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Minimal input-data replay of the focused T02 multi-family "
            "self-edge local lemma packet; proof-mining scaffolding only, "
            "not a proof of n=9, counterexample, or independent review "
            "completion."
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
        ident="n9_t03_self_edge_minireplay",
        command=(
            "python",
            "scripts/check_n9_t03_self_edge_minireplay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Minimal input-data replay of the focused T03 multi-family "
            "self-edge local lemma packet; proof-mining scaffolding only, "
            "not a proof of n=9, counterexample, or independent review "
            "completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_t04_self_edge_lemma_packet",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_t04_self_edge_lemma_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Focused T04/F13 n=9 self-edge local lemma packet; "
            "proof-mining scaffolding only, not a proof of n=9, "
            "counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_t04_self_edge_minireplay",
        command=(
            "python",
            "scripts/check_n9_t04_self_edge_minireplay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Minimal input-data replay of the focused T04/F13 self-edge "
            "local lemma packet; proof-mining scaffolding only, not a proof "
            "of n=9, counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_t05_self_edge_lemma_packet",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_t05_self_edge_lemma_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Focused T05/F10 n=9 self-edge local lemma packet; "
            "proof-mining scaffolding only, not a proof of n=9, "
            "counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_t05_self_edge_minireplay",
        command=(
            "python",
            "scripts/check_n9_t05_self_edge_minireplay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Minimal input-data replay of the focused T05/F10 self-edge "
            "local lemma packet; proof-mining scaffolding only, not a proof "
            "of n=9, counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_t06_self_edge_lemma_packet",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_t06_self_edge_lemma_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Focused T06/F11 n=9 self-edge local lemma packet; "
            "proof-mining scaffolding only, not a proof of n=9, "
            "counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_t06_self_edge_minireplay",
        command=(
            "python",
            "scripts/check_n9_t06_self_edge_minireplay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Minimal input-data replay of the focused T06/F11 self-edge "
            "local lemma packet; proof-mining scaffolding only, not a proof "
            "of n=9, counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_t07_self_edge_lemma_packet",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_t07_self_edge_lemma_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Focused T07/F06 n=9 self-edge local lemma packet; "
            "proof-mining scaffolding only, not a proof of n=9, "
            "counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_t07_self_edge_minireplay",
        command=(
            "python",
            "scripts/check_n9_t07_self_edge_minireplay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Minimal input-data replay of the focused T07/F06 self-edge "
            "local lemma packet; proof-mining scaffolding only, not a proof "
            "of n=9, counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_t08_self_edge_lemma_packet",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_t08_self_edge_lemma_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Focused T08/F02 n=9 self-edge local lemma packet; "
            "proof-mining scaffolding only, not a proof of n=9, "
            "counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_t08_self_edge_minireplay",
        command=(
            "python",
            "scripts/check_n9_t08_self_edge_minireplay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Minimal input-data replay of the focused T08/F02 self-edge "
            "local lemma packet; proof-mining scaffolding only, not a proof "
            "of n=9, counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_t09_self_edge_lemma_packet",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_t09_self_edge_lemma_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Focused T09/F03 n=9 self-edge local lemma packet; "
            "proof-mining scaffolding only, not a proof of n=9, "
            "counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_t09_self_edge_minireplay",
        command=(
            "python",
            "scripts/check_n9_t09_self_edge_minireplay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Minimal input-data replay of the focused T09/F03 self-edge "
            "local lemma packet; proof-mining scaffolding only, not a proof "
            "of n=9, counterexample, or independent review completion."
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
        ident="n9_t10_strict_cycle_minireplay",
        command=(
            "python",
            "scripts/check_n9_t10_strict_cycle_minireplay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Minimal input-data replay of the focused T10/F12 strict-cycle "
            "local lemma packet; proof-mining scaffolding only, not a proof "
            "of n=9, counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_t10_paired_square_entry_audit",
        command=(
            "python",
            "scripts/check_n9_t10_paired_square_entry.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Paired-square entry audit for the focused T10/F12 strict-cycle "
            "assignments; proof-mining diagnostics only, not a proof of "
            "n=9, counterexample, or global status update."
        ),
    ),
    AuditCommand(
        ident="relation_skeleton_catalog",
        command=(
            "python",
            "scripts/check_relation_skeleton_catalog.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Sixteen-entry relation-skeleton catalog for focused n=9 "
            "vertex-circle quotient motifs; proof-mining scaffolding only, "
            "not a proof of n=9, counterexample, or independent review "
            "completion."
        ),
    ),
    AuditCommand(
        ident="n9_relation_skeleton_closed_descent_crosswalk",
        command=(
            "python",
            "scripts/check_n9_relation_skeleton_closed_descent_crosswalk.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Cross-artifact audit joining relation skeletons to the n=9 "
            "closed-descent packet; not local-lemma completeness, proof of "
            "n=9, counterexample, bridge proof, or official/global status "
            "update."
        ),
    ),
    AuditCommand(
        ident="relation_skeleton_local_lemma_crosswalk",
        command=(
            "python",
            "scripts/check_relation_skeleton_local_lemma_crosswalk.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Cross-artifact audit joining the relation-skeleton catalog to "
            "the aggregate n=9 local-lemma scan and simple replay; not a "
            "proof of n=9, counterexample, or independent review completion."
        ),
    ),
    AuditCommand(
        ident="n9_vertex_circle_local_lemma_audit_path",
        command=(
            "python",
            "scripts/check_n9_vertex_circle_local_lemma_audit_path.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Combined audit path for focused n=9 local-lemma packets, "
            "mini-replays, aggregate/simple replay, exhaustive/local-lemma "
            "counts, and relation skeletons; not packet soundness, proof of "
            "n=9, counterexample, or independent review completion."
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
        ident="n9_t11_strict_cycle_minireplay",
        command=(
            "python",
            "scripts/check_n9_t11_strict_cycle_minireplay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Minimal input-data replay of the focused T11/F07 strict-cycle "
            "local lemma packet; proof-mining scaffolding only, not a proof "
            "of n=9, counterexample, or independent review completion."
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
        ident="n9_t12_strict_cycle_minireplay",
        command=(
            "python",
            "scripts/check_n9_t12_strict_cycle_minireplay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Minimal input-data replay of the focused T12/F16 strict-cycle "
            "local lemma packet; proof-mining scaffolding only, not a proof "
            "of n=9, counterexample, or independent review completion."
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
        ident="n9_base_apex_d3_escape_frontier_packet",
        command=(
            "python",
            "scripts/check_n9_base_apex_d3_escape_frontier_packet.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Focused n=9 base-apex D=3,r=3 escape-frontier representative "
            "packet bookkeeping; not a proof of n=9, not a counterexample, "
            "not a geometric realizability test, and not a global status update."
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
        ident="n9_selected_baseline_d3_escape_class_crosswalk",
        command=(
            "python",
            "scripts/check_n9_selected_baseline_d3_escape_class_crosswalk.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Focused n=9 selected-baseline D=3 escape-class crosswalk "
            "bookkeeping; not a proof of n=9, not a counterexample, not an "
            "incidence-completeness result, not a geometric realizability "
            "test, and not a global status update."
        ),
    ),
    AuditCommand(
        ident="n9_selected_baseline_d3_vertex_circle_template_join",
        command=(
            "python",
            "scripts/check_n9_selected_baseline_d3_vertex_circle_template_join.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Selected-baseline D=3 escaping assignment/slot-choice landings "
            "joined to n=9 vertex-circle family/template diagnostics; not a "
            "proof of n=9, not a counterexample, not an "
            "incidence-completeness result, not a geometric realizability "
            "test, and not a global status update."
        ),
    ),
    AuditCommand(
        ident="n9_base_apex_d3_p19_incidence_capacity_pilot",
        command=(
            "python",
            "scripts/check_n9_base_apex_d3_p19_incidence_capacity_pilot.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Focused n=9 base-apex D=3 P19 incidence-capacity pilot ledger "
            "for rows R000..R007; not a proof of n=9, not a counterexample, "
            "not an incidence-completeness result, not a geometric "
            "realizability test, and not a global status update."
        ),
    ),
    AuditCommand(
        ident="n9_base_apex_d3_incidence_capacity_packet",
        command=(
            "python",
            "scripts/check_n9_base_apex_d3_incidence_capacity_packet.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Full n=9 base-apex D=3 incidence-capacity packet ledger for "
            "all 88 D=3 packet rows; not a proof of n=9, not a "
            "counterexample, not an incidence-completeness result, not a "
            "geometric realizability test, and not a global status update."
        ),
    ),
    AuditCommand(
        ident="n9_base_apex_d3_p19_degree_obstruction",
        command=(
            "python",
            "scripts/check_n9_base_apex_d3_p19_degree_obstruction.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Exact finite profile-capacity obstruction for the P19 rows "
            "R000..R007 of the n=9 base-apex D=3 incidence-capacity packet; "
            "not a proof of n=9, not a counterexample, not an "
            "incidence-completeness result, not a geometric realizability "
            "test, and not a global status update."
        ),
    ),
    AuditCommand(
        ident="n9_base_apex_d3_p20_residue_obstruction",
        command=(
            "python",
            "scripts/check_n9_base_apex_d3_p20_residue_obstruction.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Exact finite profile-capacity obstruction for the P20 rows "
            "R008..R015 of the n=9 base-apex D=3 incidence-capacity packet; "
            "not a proof of n=9, not a counterexample, not an "
            "incidence-completeness result, not a geometric realizability "
            "test, and not a global status update."
        ),
    ),
    AuditCommand(
        ident="n9_base_apex_d3_artifact_join",
        command=(
            "python",
            "scripts/check_n9_base_apex_d3_artifact_join.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Cross-artifact consistency checker for n=9 base-apex D=3 "
            "bookkeeping artifacts; not a proof of n=9, not a "
            "counterexample, not an incidence-completeness result, not a "
            "geometric realizability test, and not a global status update."
        ),
    ),
    AuditCommand(
        ident="n9_base_apex_audit_path",
        command=(
            "python",
            "scripts/check_n9_base_apex_audit_path.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Reviewer-facing audit path for n=9 base-apex low-excess and D=3 "
            "bookkeeping artifacts joined to the selected-baseline and "
            "review-pending vertex-circle frontier; not a proof of n=9, not "
            "a counterexample, not an incidence-completeness result, not a "
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
        ident="bridge_lemma_frontier",
        command=(
            "python",
            "scripts/check_bridge_lemma_frontier.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Finite n=8/n=9 ear-orderability and obstruction cross-tab for "
            "Bridge Lemma A' proof mining; not a proof of the bridge, not a "
            "proof of Erdos Problem #97, not a counterexample, and not an "
            "official/global status update."
        ),
    ),
    AuditCommand(
        ident="rich_support_counting_bound",
        command=(
            "python",
            "scripts/check_rich_support_counting_bound.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Proof-facing edge-sensitive rich-support pair-counting lemma "
            "and small-n consequences, including the n=9 profile-deficiency "
            "refinement; not a proof of n=9, not a proof of n=10, not a "
            "proof of n=11, not a proof of Erdos Problem #97, and not a "
            "counterexample."
        ),
    ),
    AuditCommand(
        ident="support_saturation_obstruction",
        command=(
            "python",
            "scripts/check_support_saturation_obstruction.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Proof-facing equality-wall obstruction for the edge-sensitive "
            "rich-support count; upgrades all-centers support-size thresholds "
            "by one for k >= 4, but is not a proof of n=9, not a proof of "
            "n=10, not a proof of n=11, not a proof of Erdos Problem #97, "
            "and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="n12_rich_support_determinant",
        command=(
            "python",
            "scripts/check_n12_rich_support_determinant.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Proof-facing determinant obstruction for the n=12 all-five-rich "
            "support-count equality wall; independently checks the same "
            "boundary closed by support saturation, but is not a proof of "
            "n=12, not a proof of Erdos Problem #97, and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="localized_rich_support_counting",
        command=(
            "python",
            "scripts/check_localized_rich_support_counting.py",
            "--check",
            "--json",
        ),
        claim_scope=(
            "Proof-facing localized rich-support occurrence-counting lemma "
            "and small-n consequences; reduces hypothetical 4-bad nonagons "
            "to all-exact-four support systems but is not a proof of n=9, "
            "not a proof of Erdos Problem #97, and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="radius_blocker_vertex_circle_pilot",
        command=(
            "python",
            "scripts/check_radius_blocker_vertex_circle_pilot.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Finite exact-four-row radius-blocker packet diagnostic; not a "
            "proof of the adaptive blocker bridge, not a proof of Erdos "
            "Problem #97, and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="n9_full_radius_blocker_vertex_circle_packet",
        command=(
            "python",
            "scripts/check_n9_full_radius_blocker_vertex_circle_packet.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Full exact-four row-option packet for n=9, natural cyclic order, "
            "and blocker {0,1,2,3}; all incidence survivors are vertex-circle "
            "obstructed, but this is not a proof of Erdos Problem #97 and not "
            "a counterexample."
        ),
    ),
    AuditCommand(
        ident="n9_radius_blocker_shape_sweep",
        command=(
            "python",
            "scripts/check_n9_radius_blocker_shape_sweep.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Natural-order n=9 exact-four row-option sweep over all 10 "
            "dihedral classes of four-vertex blockers; all incidence "
            "survivors are vertex-circle obstructed, but this is not a proof "
            "of Erdos Problem #97 and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="n9_radius_blocker_order_reduction_crosswalk",
        command=(
            "python",
            "scripts/check_n9_radius_blocker_order_reduction_crosswalk.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Order-reduction crosswalk for the n=9 exact-four radius-blocker "
            "shape sweep; arbitrary cyclic-order placements of a "
            "four-blocker reduce to the stored natural-order shape sweep, "
            "but this is not a proof of Erdos Problem #97 and not a "
            "counterexample."
        ),
    ),
    AuditCommand(
        ident="n9_radius_blocker_rich_projection_pilot",
        command=(
            "python",
            "scripts/check_n9_radius_blocker_rich_projection_pilot.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Bounded n=9 radius-blocker richer-class projection pilot; one "
            "synthetic size-five rich class at every center is expanded to "
            "exact four-subset selected-row options and checked by finite "
            "packet replay, but this is not full rich-class quotient replay, "
            "not a proof of Erdos Problem #97, and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="n9_radius_blocker_rich_quotient_pilot",
        command=(
            "python",
            "scripts/check_n9_radius_blocker_rich_quotient_pilot.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Full rich-class vertex-circle quotient replay for one bounded "
            "n=9 synthetic size-five radius-blocker family; checks the full "
            "class equalities and nested-chord inequalities without choosing "
            "exact four-subsets, but this is not a proof of Erdos Problem "
            "#97 and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="n9_radius_blocker_rich_quotient_sweep",
        command=(
            "python",
            "scripts/check_n9_radius_blocker_rich_quotient_sweep.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Generated full rich-class quotient replay for 20 synthetic "
            "size-five n=9 radius-blocker packets derived from stored "
            "shape-sweep obstruction examples; finite packet evidence only, "
            "not a proof of Erdos Problem #97 and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="n9_radius_blocker_rich_extension_neighborhood",
        command=(
            "python",
            "scripts/check_n9_radius_blocker_rich_extension_neighborhood.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Bounded n=9 rich-extension neighborhood replay for 5,996 "
            "Hamming-distance <= 2 size-five variants around the generated "
            "radius-blocker quotient-sweep packets; finite neighborhood "
            "evidence only, not a proof of Erdos Problem #97 and not a "
            "counterexample."
        ),
    ),
    AuditCommand(
        ident="n9_radius_blocker_rich_extension_product_pilot",
        command=(
            "python",
            "scripts/check_n9_radius_blocker_rich_extension_product_pilot.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "One-packet full rich-extension product replay for the first "
            "maximum-size generated n=9 radius-blocker packet; finite packet "
            "evidence only, not the full 20-packet product, not a proof of "
            "Erdos Problem #97, and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="n9_radius_blocker_rich_extension_product_sweep",
        command=(
            "python",
            "scripts/check_n9_radius_blocker_rich_extension_product_sweep.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "All-packet full rich-extension product replay over the 20 "
            "generated n=9 radius-blocker source packets; finite generated-"
            "packet evidence only, not arbitrary rich-class classification, "
            "not a proof of Erdos Problem #97, and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="n9_all_five_rich_support_obstruction",
        command=(
            "python",
            "scripts/check_n9_all_five_rich_support_obstruction.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Generator-independent n=9 all-five-rich support obstruction; "
            "finite support subcase only, not mixed exact-four/size-five "
            "catalogue coverage, not a proof of Erdos Problem #97, and not "
            "a counterexample."
        ),
    ),
    AuditCommand(
        ident="n9_mixed_rich_support_reduction",
        command=(
            "python",
            "scripts/check_n9_mixed_rich_support_reduction.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Generator-independent n=9 mixed four/five support reduction; "
            "finite support reduction only, not an independent proof of the "
            "exact-four vertex-circle exhaustive checker, not a proof of "
            "Erdos Problem #97, and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="n9_mixed_rich_frontier_crosswalk",
        command=(
            "python",
            "scripts/check_n9_mixed_rich_frontier_crosswalk.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Crosswalk from the n=9 mixed four/five support reduction to the "
            "stored exact-four vertex-circle frontier; support-to-frontier "
            "bookkeeping only, not an independent proof of the exact-four "
            "vertex-circle exhaustive checker, not a proof of Erdos Problem "
            "#97, and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_core_crosswalk",
        command=(
            "python",
            "scripts/check_bootstrap_core_crosswalk.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Bootstrap-core rank and private-halo capacity crosswalk for "
            "selected fixed-row frontier motifs; not a proof of the bridge, "
            "not a proof of Erdos Problem #97, not a counterexample, and not "
            "a global status update."
        ),
    ),
    AuditCommand(
        ident="bootstrap_vertex_circle_overlay",
        command=(
            "python",
            "scripts/check_bootstrap_vertex_circle_overlay.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Overlay of the two non-ear-orderable n=9 bootstrap-core rows "
            "with the review-pending vertex-circle strict-cycle chain; not a "
            "proof of n=9, the bridge, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_forcing_targets",
        command=(
            "python",
            "scripts/check_bootstrap_t12_forcing_targets.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "T12/F16 forcing-target ledger for the two tight n=9 "
            "bootstrap-core rows; not a proof that missing rows are forced, "
            "not a proof of n=9, the bridge, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_row_pressure",
        command=(
            "python",
            "scripts/check_bootstrap_t12_row_pressure.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Row-pressure diagnostic for the two tight n=9 bootstrap/T12 "
            "records; not a proof that missing rows are forced, not a proof "
            "of n=9, the bridge, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_closure_exposed",
        command=(
            "python",
            "scripts/check_bootstrap_t12_closure_exposed.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Closure-exposed-row packet for the two tight n=9 bootstrap/T12 "
            "records; not a proof that missing rows are forced, not a proof "
            "of n=9, the bridge, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_one_outside",
        command=(
            "python",
            "scripts/check_bootstrap_t12_one_outside.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "One-outside-label packet for the two tight n=9 bootstrap/T12 "
            "records; not a proof that missing rows are forced, not a proof "
            "of n=9, the bridge, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_outside_pair",
        command=(
            "python",
            "scripts/check_bootstrap_t12_outside_pair.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Outside-pair packet for the two tight n=9 bootstrap/T12 records; "
            "not a proof that the missing row is forced, not a proof of n=9, "
            "the bridge, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_activation_requirements",
        command=(
            "python",
            "scripts/check_bootstrap_t12_activation_requirements.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Role-sensitive T12/F16 activation-support requirement diagnostic "
            "for the two tight n=9 bootstrap-core rows; not a row-forcing, "
            "n=9, bridge, or counterexample claim."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_bridge_target_map",
        command=(
            "python",
            "scripts/check_bootstrap_t12_bridge_target_map.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Joined T12/F16 bridge-target map for the two tight n=9 "
            "bootstrap-core rows; not a proof that missing rows are forced, "
            "not a proof of n=9, the bridge, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_hard_strict_endpoints",
        command=(
            "python",
            "scripts/check_bootstrap_t12_hard_strict_endpoints.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Hard strict-endpoint diagnostic for the two tight n=9 "
            "bootstrap-core rows; not a proof that endpoints or missing rows "
            "are forced, not a proof of n=9, the bridge, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_open_connector_pair",
        command=(
            "python",
            "scripts/check_bootstrap_t12_open_connector_pair.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Open connector-pair diagnostic for the two tight n=9 "
            "bootstrap-core rows; not a proof that endpoints or missing rows "
            "are forced, not a proof of n=9, the bridge, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_relation_sufficient_rows",
        command=(
            "python",
            "scripts/check_bootstrap_t12_relation_sufficient_rows.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Relation-sufficient row diagnostic for the two tight n=9 "
            "bootstrap-core rows; not a proof that endpoints or missing rows "
            "are forced, not a proof of n=9, the bridge, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_151_6_outside_pair_connector_contract",
        command=(
            "python",
            "scripts/check_bootstrap_t12_151_6_outside_pair_connector_contract.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Focused 151:6 outside-pair connector contract diagnostic; proves "
            "only the local conditional from a genuine rich class containing "
            "witnesses 0 and 8, not support existence or row forcing."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_closure_target",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_closure_target.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Focused 81:3 full-row closure target diagnostic; not a proof "
            "that the row is forced, not a proof of n=9, the bridge, or a "
            "counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_rich_triple_contract",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_rich_triple_contract.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Focused 81:3 rich-triple connector contract diagnostic; proves "
            "only the local conditional from a genuine rich class containing "
            "witnesses 0 and 1, not rich-class existence or row forcing."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_order_escape",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_order_escape.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Focused 81:3 order-resolved fixed-row escape diagnostic; not "
            "genuine rich-class order, not row forcing, not a proof of n=9, "
            "the bridge, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_escape_candidates",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_escape_candidates.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Relaxed 81:3 escape-candidate scan preserving seven source-81 "
            "rows outside centers 3 and 6; not genuine rich-class order, row "
            "forcing, an n=9 proof, a bridge proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_escape_one_row_drop",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_escape_one_row_drop.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "One-row-drop relaxation of the 81:3 escape-candidate scan; not "
            "genuine rich-class order, row forcing, an n=9 proof, a bridge "
            "proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_escape_two_row_drop",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_escape_two_row_drop.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Two-row-drop relaxation of the 81:3 escape-candidate scan; not "
            "genuine rich-class order, row forcing, an n=9 proof, a bridge "
            "proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_escape_full_neighborhood",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_escape_full_neighborhood.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Full-neighborhood CSP relaxation of the 81:3 escape-candidate "
            "scan; not genuine rich-class order, row forcing, an n=9 proof, "
            "a bridge proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_escape_auxiliary_csp",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_escape_auxiliary_csp.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Auxiliary-rich-class CSP relaxation of the 81:3 escape scan; "
            "not genuine rich-class order, row forcing, an n=9 proof, a "
            "bridge proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_trigger_uniqueness",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_trigger_uniqueness.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Same-center disjointness audit for specified 81:3 supply and "
            "connector trigger families; not genuine rich-class order, row "
            "forcing, an n=9 proof, a bridge proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_escape_rich_support_csp",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_escape_rich_support_csp.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Rich-support auxiliary CSP for the 81:3 pre-3 label-6 escape; "
            "not support existence, row forcing, an n=9 proof, a bridge "
            "proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_first_supply_chains",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_first_supply_chains.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "First-step prefix CSP for the 81:3 pre-3 label-6 escape; "
            "finds three center-8 prefix survivors but no immediate label-6 "
            "supply extension, and is not row forcing, an n=9 proof, a "
            "bridge proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_second_supply_chains",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_second_supply_chains.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Second-supply-chain prefix CSP for the 81:3 pre-3 label-6 "
            "escape; leaves one second-step prefix survivor and no immediate "
            "center-6 label-6 extension, and is not support existence, row "
            "forcing, an n=9 proof, a bridge proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_second_step_chains",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_second_step_chains.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Distinct-intermediate continuation CSP for the 81:3 pre-3 "
            "label-6 escape after the center-8 prefix survivors; not support "
            "existence, row forcing, an n=9 proof, a bridge proof, or a "
            "counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_post8_supply_chains",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_post8_supply_chains.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Post-center-8 raw catalogue accounting for the 81:3 pre-3 "
            "label-6 escape chain model; not support existence, row forcing, "
            "an n=9 proof, a bridge proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_chain_closure_csp",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_chain_closure_csp.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Ordered chain-closure CSP for the 81:3 pre-3 label-6 escape; "
            "leaves four non-supply prefixes and no surviving prefix whose "
            "next activated center is 6, but is not support existence, row "
            "forcing, genuine rich-class order, an n=9 proof, a bridge proof, "
            "or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_repeated_support_catalogue_audit",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_repeated_support_catalogue_audit.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "One-layer repeated-support catalogue audit for the 81:3 pre-3 "
            "label-6 escape; not support existence, row forcing, genuine "
            "rich-class order, an n=9 proof, a bridge proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_two_repeated_support_catalogue_audit",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_two_repeated_support_catalogue_audit.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Two-repeated-support catalogue audit for the 81:3 pre-3 label-6 "
            "escape; not support existence, row forcing, genuine rich-class "
            "order, an n=9 proof, a bridge proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_3_repeated_support_saturation_audit",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_3_repeated_support_saturation_audit.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Repeated-support saturation audit for the 81:3 pre-3 label-6 "
            "escape; no three-repeated-support catalogue exists in the "
            "stored-prefix model, but this is not support existence, row "
            "forcing, genuine rich-class order, an n=9 proof, a bridge proof, "
            "or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_8_singleton_support_audit",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_8_singleton_support_audit.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Source-81 row-8 singleton-support activation-row audit; not "
            "singleton-support existence, row forcing, an n=9 proof, a bridge "
            "proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_8_singleton_support_two_row_drop",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_8_singleton_support_two_row_drop.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Source-81 row-8 singleton-support two-row-drop relaxation; not "
            "singleton-support existence, row forcing, an n=9 proof, a bridge "
            "proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_81_8_full_neighborhood_vertex_circle",
        command=(
            "python",
            "scripts/check_bootstrap_t12_81_8_full_neighborhood_vertex_circle.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Source-81 row-8 full-neighborhood vertex-circle diagnostic; "
            "not singleton-support existence, row forcing, an n=9 proof, "
            "a bridge proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_151_6_outside_pair_audit",
        command=(
            "python",
            "scripts/check_bootstrap_t12_151_6_outside_pair_audit.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Source-151 row-6 outside-pair activation-row audit; not "
            "outside-pair support existence, row forcing, an n=9 proof, a "
            "bridge proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_151_6_outside_pair_two_row_drop",
        command=(
            "python",
            "scripts/check_bootstrap_t12_151_6_outside_pair_two_row_drop.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Two-row-drop outside-pair stress test for source 151 row 6; "
            "not outside-pair support existence, row forcing, an n=9 proof, "
            "a bridge proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle",
        command=(
            "python",
            "scripts/check_bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Full-neighborhood vertex-circle diagnostic for source 151 row 6; "
            "not outside-pair support existence, row forcing, an n=9 proof, "
            "a bridge proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_151_singleton_support_audit",
        command=(
            "python",
            "scripts/check_bootstrap_t12_151_singleton_support_audit.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Source-151 singleton-support activation-row audit for rows 5 and "
            "8; not singleton-support existence, row forcing, an n=9 proof, "
            "a bridge proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_151_singleton_two_row_drop",
        command=(
            "python",
            "scripts/check_bootstrap_t12_151_singleton_two_row_drop.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Two-row-drop singleton-support stress test for source 151 rows "
            "5 and 8; not singleton-support existence, row forcing, an n=9 "
            "proof, a bridge proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_151_singleton_full_neighborhood_vertex_circle",
        command=(
            "python",
            "scripts/check_bootstrap_t12_151_singleton_full_neighborhood_vertex_circle.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Full-neighborhood vertex-circle diagnostic for source 151 rows "
            "5 and 8; not singleton-support existence, row forcing, an n=9 "
            "proof, a bridge proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_singleton_full_neighborhood_crosswalk",
        command=(
            "python",
            "scripts/check_bootstrap_t12_singleton_full_neighborhood_crosswalk.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Crosswalk for source-81 and source-151 singleton-support "
            "full-neighborhood diagnostics; not singleton-support existence, "
            "row forcing, an n=9 proof, a bridge proof, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="closure_activation_wrong_fourth_negative_control",
        command=(
            "python",
            "scripts/check_closure_activation_wrong_fourth_negative_control.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Wrong-fourth closure activation negative control only; not a "
            "Euclidean realization, not a proof of row forcing, not a proof "
            "of the bootstrap bridge, and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="closure_activation_negative_controls",
        command=(
            "python",
            "scripts/check_closure_activation_negative_controls.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Abstract rich-class closure activation negative controls only; "
            "not a Euclidean realization, not a proof of n=9, not a proof of "
            "the bootstrap bridge, and not a proof of Erdos Problem #97."
        ),
    ),
    AuditCommand(
        ident="bootstrap_t12_anti_activation_negative_control",
        command=(
            "python",
            "scripts/check_bootstrap_t12_anti_activation_negative_control.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Full selected-row anti-activation negative control only; not a "
            "Euclidean realization, not a proof of row forcing, not a proof "
            "of the bootstrap bridge, and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="closure_visibility_anti_activation_control",
        command=(
            "python",
            "scripts/check_closure_visibility_anti_activation_control.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Closure-visibility anti-activation negative control only; not a "
            "Euclidean realization, not a proof of row forcing, not a proof "
            "of the bootstrap bridge, and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="block6_fragile_vertex_circle_extension",
        command=(
            "python",
            "scripts/check_block6_fragile_vertex_circle_extension.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Two-block block-6 fragile-cover full-extension vertex-circle "
            "audit in the natural cyclic order; not a proof of the fragile "
            "bridge, Erdos Problem #97, or a counterexample."
        ),
    ),
    AuditCommand(
        ident="block6_fragile_sixth_row_survivors",
        command=(
            "python",
            "scripts/check_block6_fragile_sixth_row_survivors.py",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Block-6 row-depth survivor catalog for legal sixth rows after "
            "clean fifth-row states and low-support seventh/eighth-row "
            "continuations; bounded natural-order negative control only, not "
            "a fragile-bridge proof, not a proof of Erdos Problem #97, and "
            "not a counterexample."
        ),
    ),
    AuditCommand(
        ident="block6_terminal_crossing_vertex_circle_sample",
        command=(
            "python",
            "scripts/check_block6_terminal_crossing_vertex_circle_sample.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Two deterministic block-6 terminal-extension windows checked "
            "across crossing-compatible cyclic orders by the vertex-circle "
            "quotient filter; sample only, not all-extension or all-order "
            "closure, not a proof of Erdos Problem #97, and not a "
            "counterexample."
        ),
    ),
    AuditCommand(
        ident="block6_terminal_crossing_vertex_circle_full_sweep",
        command=(
            "python",
            "scripts/check_block6_terminal_crossing_vertex_circle_sample.py",
            "--full-sweep",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Full sweep over terminal full extensions generated by the "
            "natural-order two-block block-6 audit, across the "
            "crossing-compatible cyclic orders each admits; bounded "
            "diagnostic only, not row systems outside that terminal "
            "generator, not a fragile-bridge proof, not a proof of Erdos "
            "Problem #97, and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="block6_fixed_order_vertex_circle_probe",
        command=(
            "python",
            "scripts/check_block6_fixed_order_vertex_circle_probe.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Fixed-order probe for four block-6 cyclic orders, including "
            "three non-natural orders whose first terminal extensions are "
            "outside the natural-order generator; not all-order closure, not "
            "a fragile-bridge proof, not a proof of Erdos Problem #97, and "
            "not a counterexample."
        ),
    ),
    AuditCommand(
        ident="block6_shuffle_order_vertex_circle_sweep",
        command=(
            "python",
            "scripts/check_block6_shuffle_order_vertex_circle_sweep.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Fixed-order sweep over all block-preserving shuffle cyclic orders "
            "for the two-block block-6 fragile rows; bounded family "
            "diagnostic only, not all-order closure, not a fragile-bridge "
            "proof, not a proof of Erdos Problem #97, and not a "
            "counterexample."
        ),
    ),
    AuditCommand(
        ident="block6_reversed_block_shuffle_vertex_circle_escape",
        command=(
            "python",
            "scripts/check_block6_reversed_block_shuffle_vertex_circle_escape.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Reversed-second-block shuffle negative-control packet for the "
            "two-block block-6 fragile rows; records 16 vertex-circle-clean "
            "fixed-order abstract row systems, not Euclidean realizations, "
            "not counterexamples, not all-order closure, not a fragile-bridge "
            "proof, and not a proof of Erdos Problem #97."
        ),
    ),
    AuditCommand(
        ident="block6_reversed_block_clean_kalmanson",
        command=(
            "python",
            "scripts/check_block6_reversed_block_clean_kalmanson.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Exact fixed-order Kalmanson quotient-cone certificates for the "
            "16 reversed-block vertex-circle-clean escape rows; fixed-row "
            "and fixed-order only, not all-order closure, not a "
            "fragile-bridge proof, not a proof of Erdos Problem #97, and "
            "not a counterexample."
        ),
    ),
    AuditCommand(
        ident="block6_reversed_block_two_stage_closure",
        command=(
            "python",
            "scripts/check_block6_reversed_block_two_stage_closure.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Compact cross-artifact closure count for the reversed-block "
            "shuffle family: 446 vertex-circle closures plus 16 fixed-order "
            "Kalmanson closures. Bounded family only, not all-order closure, "
            "not a fragile-bridge proof, not a proof of Erdos Problem #97, "
            "and not a counterexample."
        ),
    ),
    AuditCommand(
        ident="block6_forward_block_two_orientation_closure",
        command=(
            "python",
            "scripts/check_block6_forward_block_two_orientation_closure.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Cross-artifact closure count for the first-block-forward "
            "two-orientation block-6 shuffle families: 462 forward-second-"
            "block vertex-circle closures plus the 462-order reversed-second-"
            "block two-stage packet. Bounded family only, not first-block-"
            "reversed orientations, not arbitrary cyclic orders, not a "
            "fragile-bridge proof, not a proof of Erdos Problem #97, and "
            "not a counterexample."
        ),
    ),
    AuditCommand(
        ident="block6_oriented_block_reversal_closure",
        command=(
            "python",
            "scripts/check_block6_oriented_block_reversal_closure.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Cross-artifact closure count for all four oriented-block block-6 "
            "shuffle families using direct first-block-forward closures plus "
            "cyclic reversal duality for first-block-reversed families. "
            "Bounded oriented-block shuffles only, not arbitrary cyclic "
            "orders, not all selected-row systems, not a fragile-bridge "
            "proof, not a proof of Erdos Problem #97, and not a "
            "counterexample."
        ),
    ),
    AuditCommand(
        ident="n10_mixed_rich_support_capacity",
        command=(
            "python",
            "scripts/check_n10_mixed_rich_support_capacity.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Generator-independent n=10 four/five support-capacity "
            "diagnostic under row-pair cap, two-overlap crossing, and "
            "witness-pair capacity filters; finite support reduction only, "
            "not a proof of n=10, not a proof of Erdos Problem #97, and "
            "not a counterexample."
        ),
    ),
    AuditCommand(
        ident="n10_q2_rich_vertex_circle",
        command=(
            "python",
            "scripts/check_n10_q2_rich_vertex_circle.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Generator-independent n=10 exactly-two-size-five rich-support "
            "diagnostic under row-pair cap, two-overlap crossing, "
            "witness-pair capacity, and rich vertex-circle quotient filters; "
            "finite support-plus-quotient reduction only, not a proof of "
            "n=10, not a proof of Erdos Problem #97, and not a "
            "counterexample."
        ),
    ),
    AuditCommand(
        ident="n10_q1_rich_vertex_circle",
        command=(
            "python",
            "scripts/check_n10_q1_rich_vertex_circle.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Generator-independent n=10 exactly-one-size-five rich-support "
            "diagnostic under row-pair cap, two-overlap crossing, "
            "witness-pair capacity, and rich vertex-circle quotient filters; "
            "finite support-plus-quotient reduction only, not a proof of "
            "n=10, not a proof of Erdos Problem #97, and not a "
            "counterexample."
        ),
    ),
    AuditCommand(
        ident="n10_turn_row0_pilot",
        command=(
            "python",
            "scripts/check_n10_turn_row0_pilot.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Bounded n=10 row0-index-0 turn-frontier pilot; not a proof of "
            "n=10, not a complete n=10 search, not a counterexample, and "
            "not a global status update."
        ),
    ),
    AuditCommand(
        ident="n10_turn_row0_escape_self_edges",
        command=(
            "python",
            "scripts/check_n10_turn_row0_escape_self_edges.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Derived diagnostic for the four weak-turn SAT escapes in the "
            "bounded n=10 row0-index-0 pilot; records only their row0-local "
            "vertex-circle self-edge templates, not a proof of n=10, not a "
            "complete n=10 search, not a counterexample, and not a global "
            "status update."
        ),
    ),
    AuditCommand(
        ident="n10_turn_row0_combined_closure",
        command=(
            "python",
            "scripts/check_n10_turn_row0_combined_closure.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Crosswalk for the bounded n=10 row0-index-0 pilot: stored "
            "weak-turn Farkas certificates close 156 assignments and the "
            "four weak-turn SAT escapes are exactly the stored row0-local "
            "vertex-circle self-edge templates; finite bookkeeping only, "
            "not a proof of n=10, not a complete n=10 search, not a "
            "counterexample, and not a global status update."
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
        ident="n10_singleton_input_audit",
        command=(
            "python",
            "scripts/check_n10_singleton_input_audit.py",
            "--check",
            "--assert-expected",
            "--json",
        ),
        claim_scope=(
            "Input-data audit for all 126 draft n=10 singleton slices; checks "
            "stored row0 coverage and aggregate arithmetic only, not a search "
            "rerun, proof of n=10, counterexample, or official/global status update."
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


def _command_list_rows(commands: Sequence[AuditCommand]) -> list[dict[str, str]]:
    return [
        {
            "id": command.ident,
            "command": command_text(command.command),
            "claim_scope": command.claim_scope,
        }
        for command in commands
    ]


def list_commands_payload(
    commands: Sequence[AuditCommand],
    *,
    preflight_commands: Sequence[AuditCommand] = AUDIT_PREFLIGHT_COMMANDS,
) -> dict[str, Any]:
    listed_commands = (*preflight_commands, *commands)
    return {
        "type": "erdos97_artifact_audit_command_list_v1",
        "claim_scope": (
            "Registered artifact audit command list only; printing this list "
            "does not run checks, prove Erdos Problem #97, or change any "
            "repository claim."
        ),
        "preflight_command_count": len(preflight_commands),
        "audit_command_count": len(commands),
        "command_count": len(listed_commands),
        "commands": _command_list_rows(listed_commands),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--list-commands",
        action="store_true",
        help="Print the registered audit command list as JSON without running it.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifact-audit-results"),
        help="Directory for summary.json and per-command stdout/stderr files.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.list_commands:
        print(json.dumps(list_commands_payload(AUDIT_COMMANDS), indent=2, sort_keys=True))
        return 0

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
