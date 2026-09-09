# Erdős97: exact rigidity of two-old-supported rich caps

8 September 2026. **Restricted written proof / exact-certificate candidate;
review pending. No unrestricted solution or counterexample.**

## Main result

Fix the earlier exact nine-point seed P. Let Q be **any nonempty finite** set
of new points such that P union Q is strictly convex. Suppose every q in Q
has a radius with at least four witnesses, including at least two in P.

Then Q is uniquely forced: it is exactly the three-point next triangle of
the original recurrence. No cap symmetry, carrier, common radius, chosen
witness assignment, or cap-size cutoff is assumed. Those geometric features
are consequences of the argument. All six old exceptions remain good.

**Necessary escape:** any actual all-rich convex extension of the fixed seed
must contain a new vertex whose every rich radius uses at least three new
witnesses and at most one old witness. Moving old coordinates is a separate,
unrestricted way to escape the theorem's hypotheses.

The advance is the classification, not discovery of the next recurrence
triangle. That triangle was already known.

[Complete argument](proofs.md) · [Resulting frontier](frontier.md) ·
[Exact report](data/verification.json) · [Provenance](PROVENANCE.md)

## Why a finite computation covers arbitrary cap sizes

Every new point with two old witnesses lies on an old-pair perpendicular
bisector. Strict convexity permits at most one new point on each admissible
ray of each bisector. The seed has exactly 42 admissible open line intervals.

An exact necessary-dependency graph over these intervals has 123 edges,
computed by 1,722 directed polynomial-range checks. Every occupied interval
needs two occupied outgoing neighbors. Deleting intervals with fewer than
two available neighbors leaves just three, forcing an equilateral cap.
An elementary equal-distance argument forces its center to be the old
rotation center. A quadratic has exactly one root inside the remaining slot.

The unique twelve-point extension has maxima

```
2 2 2 3 3 3 4 4 4 4 4 4
```

This is not an all-rich polygon.

## Reproduce

Python 3.10+; standard library only for the exact results and all tests.

```sh
python verify.py
python oracle.py
python -m unittest -v test_closure.py
python exploratory/one_free_relaxation.py
python replay.py
```

`replay.py` runs the packet checks, the inherited packet's 31 tests and
replays in an isolated temporary extraction, and verifies manifests before
and after. It does not run repository-wide CI.

Regenerate the exact reports from maintained source:

```sh
python verify.py --write
python oracle.py --write
python exploratory/one_free_relaxation.py --write
```

The primary algebra is inherited verbatim in `prior_math/`. The separate
oracle uses flattened radical coefficients and rational square-root
intervals, imports none of the primary implementation, and reconstructs
slots by first/second ray exit times rather than cell clipping.

## Limits

The previous old-coordinate repair is not converted to a counterexample.
Caps with one or zero old witnesses at a rich radius are not excluded.
The coarse one-free-vertex relaxation retains abstract survivors in all
nine location cells; no geometric realization is certified by that result.
No new global variable-radius descent argument was obtained.

No external mathematical review, Lean formalization, literature novelty,
accepted finite-bound promotion, repository-wide CI pass, or PR is claimed.
