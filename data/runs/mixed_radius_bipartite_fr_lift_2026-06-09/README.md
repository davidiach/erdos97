# Mixed-radius bipartite FR-lift homotopy imports

These JSON files are selected numerical artifacts from the 2026-06-09
mixed-radius bipartite Fishburn--Reeds-lift homotopy sessions.

They are failed-route diagnostics only. The scripts now use the repository
exactification gate from `docs/exactification-plan.md`; the checked-in JSONs
retain the original session output and should be interpreted under that
stricter repo gate.

Imported artifacts:

```text
mixed_radius_bipartite_fr_homotopy_seed20260609.json
mixed_radius_bipartite_polar_arc_fr_homotopy_seed20260609.json
mixed_radius_bipartite_arc_homotopy_summary_seed20260609.json
B20_FR_mixed_radius_bipartite_arc_homotopy_v1_aggregate.json
```

Reproduce fresh runs with:

```bash
python scripts/search_mixed_radius_bipartite_homotopy.py --out data/runs/mixed_radius_bipartite_fr_lift_2026-06-09/mixed_radius_bipartite_fr_homotopy_seed20260609.json
python scripts/search_mixed_radius_bipartite_arc_homotopy.py --out data/runs/mixed_radius_bipartite_fr_lift_2026-06-09/mixed_radius_bipartite_polar_arc_fr_homotopy_seed20260609.json
python scripts/homotopy_mixed_radius_bipartite_arc.py --out data/runs/mixed_radius_bipartite_fr_lift_2026-06-09/mixed_radius_bipartite_arc_homotopy_summary_seed20260609.json
```

The compact `B20_FR_mixed_radius_bipartite_arc_homotopy_v1_aggregate.json`
comes from the companion row-dependent fourth-witness packet and is retained as
summary-only corroborating provenance.
