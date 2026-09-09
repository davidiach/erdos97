# Mixed-witness closure for symmetric parabolic lenses

9 September 2026. **PAPER_PROOF_CANDIDATE / REVIEW_PENDING.**
No unrestricted solution of Erdős #97, accepted-bound promotion, published
novelty, external review, or Lean formalization is claimed.

## Main result

For every H>0 and every finite nonempty subset of the boundary

    x^2 <= y <= H-x^2,

there is a good vertex, without restrictions on which arc supplies its
witnesses. For H<=3/2 any maximum-|x| point has multiplicity at most two;
for H>=3/2 any minimum-|x| point has multiplicity at most three.
[proof.md](proof.md) gives the complete elementary proof, including equalities,
arc junctions, the switch height, and c=0 and endpoint centers.

This closes the mixed-witness version of the specified symmetric lens family.
It does not require the sample to be symmetric. It does not cover arbitrary
convex polygons or points outside the bounded lens. Similarities give the
corresponding result for y=k+a(x-h)^2 and y=k+H-a(x-h)^2, a>0, with switch
parameter aH=3/2.

## Exact evidence and controls

`verify.py` is a standard-library rational polynomial/Sturm checker. It checks
1,825 finite level-count cases (not the all-size proof), exact switch-height
and tangent/junction cases, and two algebraic five-point mixed-row controls.
Both controls have maximum multiplicities (4,1,1,1,1), and each receives all
15 supporting-half-plane checks. They show why a single extremal selector
cannot be used indiscriminately at every height.

`oracle.py` imports none of the primary arithmetic or geometry code. It uses
SymPy's exact polynomial routines, independent formula reconstruction, and
Bernstein coefficient bounds for algebraic signs. It checks all 1,825 levels,
both controls, and 15 universal symbolic identities used in the proof. This
second implementation is not external independent mathematical review.

`select_good.py` applies the constructive theorem to exact rational boundary
samples, validates their membership, and reports the selected vertex's exact
distance multiplicities. The proof itself allows arbitrary real coordinates.

## Two-free fixed-seed branch

`cap_pair_probe.py` reuses the prior hash-bound exact geometry to examine 4,500
support/cell cases with two internally supported new vertices. Its coarse
necessary graphs reject 1,824 and retain 2,676. It does not enforce all common
radii or simultaneous convex geometry. No survivor is a certified geometric
candidate and no full two-free exclusion is claimed. See [frontier.md](frontier.md).

## Replay

Python 3.10+; SymPy is required for `oracle.py` and the oracle tests. The exact
primary checker and cap probe otherwise use the standard library. From this
packet directory:

```sh
python verify.py --check
python oracle.py --check
python cap_pair_probe.py --check
python -m unittest -v test_mixed_lens.py
python check_manifest.py
```

`--write` regenerates each deterministic report. The final validation record
lists the commands actually run and the observed environment. No repository-
wide CI or inherited full test suite is claimed. No GitHub write or PR was made.

The inherited internal-support archive and prior parabola proof are preserved
byte-for-byte in `inputs/`; they are not silently rewritten by this packet.
