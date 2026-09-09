# Erdős97: internally supported cap and moving-seed continuation

8 September 2026. **Restricted research, independent mathematical review
pending. Not a solution to Erdős97.**

The primary result is a computer-assisted fixed-seed theorem: exactly one new
vertex whose every rich radius uses at most one old witness is impossible,
when all other new vertices are rich and can choose two-old-supported radii.
Together with the preceding zero-exception classification, any all-rich
strict convex extension of the fixed nine-point seed must contain at least
two such internally supported new vertices.

The packet also gives a symmetry-free two-copy witness-pool obstruction, the
necessary 2+1+1 saturation rule for three copies, a rational positive control
showing the one-free exclusion is seed-specific, and exact obstructions for
15 retained moving-seed patterns. No family-wide exclusion is inferred from
the bounded moving-coordinate search.

Start with [proofs.md](proofs.md) for the complete arguments and hypotheses,
[frontier.md](frontier.md) for what remains, and
[exploratory/RESULTS.md](exploratory/RESULTS.md) for the numerical experiments,
stronger-preflight correction, and failed discovery invocations.

## Reproduce

The exact new verifiers use the Python standard library. The tested version
is Python 3.13.5; other versions have not been certified by this session.
From this directory:

```
python replay.py
```

This checks the manifest, runs all 40 new tests (including full primary and
second-representation one-free replay), and checks the rational control and
all retained strict-quadrilateral certificates in isolated processes.
It checks that source/certificate bytes remain unchanged.

To replay the inherited packets as well:

```
python replay.py --with-inherited --output /tmp/erdos97-internal-support-replay.json
```

`--manifest-only` checks bytes but no mathematics. `--checks-only` checks the
new positive control and discrete pattern certificates but **does not** rerun
the full one-free theorem computation. Neither is equivalent to the full
replay. Reports requested with `--output` must be outside this directory.

The individual full theorem checks are:

```
python one_free.py
python audit_one_free.py
```

The inherited archive is SHA256-pinned before extraction and preserved
unchanged. The full inherited packet and its own earlier dependency are
included, so no GitHub or internet connection is needed for exact replay.

Numerical discovery additionally requires NumPy and SciPy. The recorded
versions and commands are in `exploratory/RESULTS.md`. Exploratory regeneration
should use fresh output paths outside the delivered packet; the original
reports retain their original bytes. Solver timeouts are not certificates.

## Evidence map

| File | Role |
|---|---|
| `proofs.md` | Geometric reduction, main theorem, elementary copy-budget argument, scope |
| `one_free.py` | Exact subdivision/range/graph certificate generation and comparison |
| `audit_one_free.py` | Separate radical representation, Minkowski-distance and graph checker |
| `data/one_free_certificate.json` | Complete 90-case, 360-node, 225-leaf certificate |
| `data/one_free_oracle.json` | Second-representation result |
| `controls.py` | Rational 14-point control and integer homogeneous-coordinate check |
| `kalmanson.py` | Positive integer convex-quadrilateral certificate checker; optional discovery |
| `combinatorics.py` | Separate equality-graph and resource audit of all retained patterns |
| `test_internal_support.py` | Full replay and malformed-evidence controls |
| `data/prior_replay_current.json` | Fresh replay of the two preceding delivered packets |
| `validation.json` | Executed checks and explicit limits of validation |
| `inputs/cap_closure.zip` | Unchanged preceding delivered archive, including its dependency |
| `exploratory/` | Bounded searches, all retained numerical reports, exact status corrections |

## Claim discipline

Two code implementations written in one session are not external independent
mathematical review. No Lean formalization, published novelty, repository-wide
CI pass, global status change, PR, or unrestricted resolution is claimed.
The fixed-seed theorem does not exclude two internally supported cap vertices,
and its old seed may not be moved while retaining its certificates.
