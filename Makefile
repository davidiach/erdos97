PYTHON ?= python

.PHONY: verify-lint verify-fast verify-n8 verify-kalmanson verify-n9-review verify-n10-review verify-artifacts audit-artifacts verify-all

verify-lint:
	$(PYTHON) scripts/check_text_clean.py
	$(PYTHON) scripts/check_status_consistency.py
	$(PYTHON) scripts/check_artifact_provenance.py
	git diff --check
	$(PYTHON) -m ruff check .

verify-fast: verify-lint
	$(PYTHON) -m pytest -q

verify-n8:
	$(PYTHON) scripts/independent_check_n8_artifacts.py --check --json
	$(PYTHON) scripts/enumerate_n8_incidence.py --summary
	$(PYTHON) scripts/analyze_n8_exact_survivors.py --check --json

verify-kalmanson:
	$(PYTHON) scripts/check_round2_certificates.py
	$(PYTHON) scripts/check_kalmanson_certificate.py data/certificates/round2/c19_kalmanson_known_order_two_unsat.json --summary-json
	$(PYTHON) scripts/check_kalmanson_certificate.py data/certificates/c13_sidon_order_survivor_kalmanson_two_unsat.json --summary-json
	$(PYTHON) scripts/check_kalmanson_two_order_search.py --name C13_sidon_1_2_4_10 --n 13 --offsets 1,2,4,10 --assert-obstructed --assert-c13-expected --json
	$(PYTHON) scripts/check_kalmanson_two_order_z3.py --certificate data/certificates/c19_skew_all_orders_kalmanson_z3.json --assert-unsat

verify-n9-review:
	$(PYTHON) scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_local_core_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_core_templates.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_frontier_motif_classification.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_self_edge_path_join.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_self_edge_template_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_strict_cycle_path_join.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_strict_cycle_template_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t11_strict_cycle_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_row_ptolemy_product_cancellations.py --check --json
	$(PYTHON) scripts/check_n9_row_ptolemy_family_signatures.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_row_ptolemy_order_sensitivity.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_row_ptolemy_order_admissible_census.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_row_ptolemy_admissible_gap_replay.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_row_ptolemy_gap_self_edge_cores.py --check --assert-expected --json
	$(PYTHON) scripts/check_n9_base_apex_low_excess_ledgers.py --check --json
	$(PYTHON) scripts/check_n9_base_apex_escape_budget.py --check --json
	$(PYTHON) scripts/check_n9_selected_baseline_escape_budget_overlay.py --check --json
	$(PYTHON) scripts/check_n9_d3_escape_slice.py --check --json
	$(PYTHON) scripts/check_n9_base_apex_low_excess_escape_ladder.py --check --json

verify-n10-review:
	$(PYTHON) scripts/check_n10_vertex_circle_singletons.py --assert-expected --spot-check-row0 0 --spot-check-row0 63 --spot-check-row0 125
	$(PYTHON) scripts/check_n10_secondary_singleton_replay.py --check --assert-expected --json

verify-artifacts: verify-n8 verify-kalmanson verify-n9-review verify-n10-review

audit-artifacts:
	$(PYTHON) scripts/check_status_consistency.py --max-official-status-age-days 90
	$(PYTHON) scripts/check_artifact_provenance.py
	$(PYTHON) scripts/run_artifact_audit.py --output-dir artifact-audit-results

verify-all: verify-fast verify-artifacts
