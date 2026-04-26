# Dropped kernels log

This file records high-relevance material that was intentionally not routed into proof-facing docs or STATE.md.

- Duplicate copies inside nested archive containers were deduplicated to one canonical kernel per claim; duplicate file paths remain visible in `inventory.json`.
- Prompt-engineering and selection-manifest files were classified as SCRATCH because they contain no durable trust-labelled research claim.
- Abandoned proof claims for n=8, n<=12, generic rank obstruction, and circumcenter-inside-witness-hull were retained only as `FAILED_APPROACH` kernels and routed to `docs/failed-ideas.md`.
- `docs/claims.md` contains no `NUMERICAL_EVIDENCE` claims after routing, so no numerical item is proof-facing.
- `erdos97-search --verify data/runs/best_B12_slsqp_m1e-6.json --tol 1e-6` reports `ok_at_tol=false`; it remains only the dashboard near-miss.
- `erdos97-search --verify data/runs/archive_C12_offsets_4_5_8_11_near_convex.json --tol 1e-6` reports `ok_at_tol=false` with max selected-distance spread about `1.85e-6`; it is excluded from `STATE.md`.
- `erdos97-search --verify data/runs/archive_C12_offsets_2_3_4_10_degenerate.json --tol 1e-6` reports `ok_at_tol=false` because convexity/minimum-distance diagnostics collapse; it is excluded from `STATE.md`.
