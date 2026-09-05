# Research-engine audit fixes (2026-09-05)

These are software and workflow changes, not a stronger mathematical claim.
The accepted finite bound, official status, and all existing certificates stay
unchanged. In particular, the radius-window theorem's long-radius gap and the
orbit66 construction's residual deficit are not resolved here.

## Exact preflight and explicit search inputs

The old default `C12_pm_2_5` is impossible in its default boundary order:
centers 0 and 3 share witnesses 5 and 10, but chords 03 and 5--10 do not cross.
The CLI now requires an explicit `--pattern` or `--pattern-json` rather than
silently spending numerical restarts on that obsolete smoke pattern.

`search_preflight.py` recomputes necessary two-circle, crossing-bisector,
base-pair-capacity, and strict ordinary-distance Kalmanson zero/inverse tests.
It does not use names, prose statuses, symmetry, reciprocity, or local side
bounds as pruning rules. Relabeling by a supplied cyclic order happens first.
All 14 built-in patterns are rejected in their natural orders by these checks;
this does not assert an all-order obstruction for every abstract pattern.

Passing preflight means only `not_obstructed_by_preflight`, never realizable.
The scalable 47-label abstract negative control is a positive test of that
remaining distinction. Preflight is not an exhaustive realization procedure.

```sh
python -m erdos97.search --pattern C12_pm_2_5 --preflight-only
python -m erdos97.search --pattern-json candidate.json --preflight-only
python -m erdos97.search --pattern-json candidate.json --optimizer slsqp --out run.json
```

A supplied JSON object needs `n` and `S`, with optional `name`. Rows must be
four distinct other labels in range, in the declared boundary order.
`--cyclic-order` can relabel an abstract input first. Both the CLI and public
search entry points preflight before invoking an optimizer. Malformed input
cannot be bypassed. An explicit `--allow-obstructed` emits a warning and sets
`benchmark_only=true` in the result, while retaining the obstruction evidence.

For an intentionally impossible legacy benchmark:

```sh
python -m erdos97.search --pattern C12_pm_2_5 --allow-obstructed \
  --penalty legacy-softplus --restarts 1 --max-nfev 10 --out benchmark.json
```

The old Boolean generator's balanced-indegree and anchored-row restrictions
are now opt-in. It remains an incidence abstraction, not a realization test.

## Equality-preserving feasible-region objective

The default geometric penalties now use `max(violation, 0)` instead of
softplus. At a point satisfying the requested margins they vanish exactly.
Thus an exact equality configuration inside that feasible region has zero
combined default objective, rather than a nonzero geometry-penalty gradient.
This does not guarantee global convergence or remove floating-point error.
Optional nonzero shape-prior weights still deliberately restrict the search.

The historical formula is available as `--penalty legacy-softplus` for
comparisons. Restart selection now prefers independently measured feasible
coordinates and then relative/absolute equality error, rather than the combined
objective alone. It rejects nonfinite results. The SLSQP path rechecks margins
and recomputes equality loss instead of trusting the optimizer's cached score.
`success` remains an optimizer/termination diagnostic, not proof or equality
certification; `feasible_at_margin`, `objective`, `benchmark_only`, and
`preflight` make the distinctions explicit in result JSON.

The regression uses the exact three-orbit, **three-witness** seed from
`docs/orbit66-exact-partial-construction.md`. At its floating evaluation, every
feasibility penalty is zero and the squared equality loss is below `1e-25`.
The old smooth objective is above `0.03`. This is a positive-control test of
the objective, not a four-witness construction or an exact arithmetic proof.

A fixed margin is not a completeness claim. Run independent, separately saved
margin stages, for example:

```sh
for margin in 1e-3 1e-5 1e-7; do
  python -m erdos97.search --pattern-json candidate.json --margin "$margin" \
    --optimizer slsqp --out "candidate-${margin}.json"
done
```

This finite schedule is not exhaustive either. Near machine precision, use
an appropriate higher-precision search/exactification method, not tolerance
inflation. The fixed-normal support parameterization is a restricted family
and does not itself guarantee convexity.

## What remains mathematical work

Do not turn the side-cap theorem into an unrestricted preflight predicate.
Long-radius witnesses remain a genuine proof obligation. In the orbit lane,
ordinary two-constraint growth preserves the explicitly supplied arrow deficit;
track deficit-reducing exact identities rather than treating the percentage of
four-bad vertices as percentage completion. Neither gap is a software switch.

## Tests

```sh
python -m pytest -q tests/test_search_audit_fixes.py tests/test_status_transitions.py
```

These tests cover preflight rejection before optimization, order semantics,
a surviving abstraction, explicit benchmark provenance, malformed input,
zero feasible-region penalties, feasible-first restart selection, and
reviewed status transitions. Repository-wide CI is a separate validation tier.
