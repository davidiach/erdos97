# Erdős #97: convex-chain, ellipse, and escape-tail obstructions

Research date: **6 September 2026**.

**Restricted all-size paper-proof candidates, with exact regression checks. Not a solution of unrestricted Erdős #97. External review pending.**

## Main results

1. A finite subset of a convex or concave graph has a vertex with maximum equal-distance multiplicity at most **two**. The sampled minimum/maximum-height point supplies it. One arbitrary additional point raises that bound to at most three.
2. The same conclusion holds on an open convex chain of total turn at most pi, including vertical end edges. A counterexample polygon would consequently need every three consecutive exterior turns to sum to **strictly less than pi**.
3. A finite subset of a Euclidean ellipse has a vertex with multiplicity at most **two**, strengthening the repository's prior three-multiplicity result. Thus an ellipse plus one arbitrary point is also excluded.
4. An escape-tail argument handles a finite set on **both branches of a hyperbola**, without convexity. Every finite nonempty subset of a real conic contains a vertex with multiplicity at most three.
5. Convexity strengthens the last result to multiplicity **two**: a convexly independent set meeting both hyperbola branches has at most four points. Therefore a strictly convex polygon with all but at most one vertex on **any real conic** satisfies Erdős #97.

The convex-graph theorem closes the globally convex quartic-graph construction family at every size and for arbitrary parameter spacing. It does not cover arbitrary convexly independent samples occupying multiple graph branches, general implicit quartics, or arbitrary polynomial parametrizations.

Read **[proofs.md](proofs.md)** for complete proofs, endpoint cases, controls, and the unresolved global gap.

## Reproduce

Full exact checks use Python 3 and SymPy. The saved run used SymPy 1.14.0.

```sh
python verify.py --output fresh-verification.json
```

The finite rational geometry regressions can also run without third-party packages:

```sh
python verify.py --skip-symbolic --output rational-only.json
```

The latter deliberately skips the symbolic identities, exact quartic root counts, and conic-rank control. It is not a replacement for the full run.

`verification.json` records the completed full run. It is regression evidence, not a computational proof covering all real configurations. No source-of-truth repository file was changed and no PR was created in this session.

## Files

- `proofs.md`: complete mathematical arguments and scope.
- `verify.py`: exact rational regressions and symbolic checks.
- `verification.json`: actual completed full-check report.
- `provenance.md`: relationship to the repository results inspected.
- `manifest.json`: SHA-256 inventory of the delivered substantive files.

No published novelty, outside review, formal proof, unrestricted counterexample, or higher accepted finite bound is claimed.
