# Turn-Packing Bridge

Status: review-pending bridge packet; not a proof of Erdos Problem #97.

This note extracts the certificate principle behind
`docs/n9-turn-inequality-frontier.md`. It should be read together with
`docs/turn-inequality-lemma.md`.

## Setup

Let `P = (p_0,...,p_{n-1})` be a strictly convex polygon in cyclic order. Write
`tau_i > 0` for its exterior turns and normalize

```text
t_i = 2*tau_i/pi.
```

Then

```text
t_i > 0,
sum_i t_i = 4.
```

For a selected row at center `i`, every selected pair with offsets
`1 <= a < b <= n-1` and equal center distance gives the weak turn inequalities

```text
sum_{h=1}^{b-1} t_{i+h} >= 1
sum_{h=a+1}^{n-1} t_{i+h} >= 1,
```

with indices read modulo `n`. These are weaker than the strict inequalities
given by the geometric turn lemma.

## Certificate Lemma

Consider any selected-witness incidence system and cyclic order. Suppose there
is a multiset `I_1,...,I_m` of turn intervals forced by the selected equalities
and a positive integer `lambda` such that:

```text
m > 4*lambda,
each turn variable t_j lies in at most lambda of the intervals I_s.
```

Then no strictly convex realization can have those selected equal-distance
rows in that cyclic order.

Proof. Summing the forced weak inequalities gives

```text
sum_s sum_{j in I_s} t_j >= m > 4*lambda.
```

But each `t_j` appears at most `lambda` times, so nonnegativity and
`sum_j t_j = 4` give

```text
sum_s sum_{j in I_s} t_j <= lambda * sum_j t_j = 4*lambda,
```

a contradiction.

## Current Evidence

The replay command

```bash
python scripts/check_turn_inequality_indexing.py --check --assert-expected --summary-json
python scripts/check_n9_turn_inequality_frontier.py --check --assert-expected --summary-json
```

first checks the offset/indexing convention used to generate weak turn
intervals, then checks the stored `n=9` frontier artifact. Use `--json`
instead when the full certificate rows are needed. The frontier replay
regenerates the 184 complete selected-witness assignments surviving the
pair/crossing/count filters before vertex-circle pruning and verifies one
integer turn-packing certificate for each assignment. The replay is arithmetic
after the stored interval choices: 180 certificates use `lambda = 1` and five
intervals; 4 use `lambda = 2` and nine intervals.

This is review-pending finite-case evidence only. It does not promote the
repo source-of-truth status, and it does not imply a general theorem without a
bridge proving that arbitrary counterexamples reduce to turn-packing-obstructed
selected systems.

## Pivot crosswalk and exact boundary

The generated crosswalk

```bash
python scripts/check_n9_fragile_turn_pivot_crosswalk.py \
  --check --assert-expected --summary-json
```

shows that every one of the 184 frontier assignments has a Hamiltonian
row-to-witness matching compatible with a pivot-to-halo turn certificate.
For the separate inversion row-pivot notion, 182 stored certificates have
minimum cover size two. The two orientations of family `F15` have minimum
cover size three; every two-pivot restriction of their full weak-turn systems
is exactly feasible, while the full rows are vertex-circle obstructed.

This finite split is not a general three-pivot bridge. The exact abstract
guardrail

```bash
python scripts/check_fragile_turn_pivot_guardrail.py \
  --check --assert-expected --summary-json
```

has a marked three-cycle matching with three-witness halos and satisfies every
current weak turn inequality strictly, as well as the fragile-cover,
crossing, good-deletion, hinge-free, and vertex-circle conditions. An exact
two-row Kalmanson inverse rejects its fixed natural order. See
`docs/fragile-turn-pivot-bridge-audit.md`.

Thus the missing step is stronger convex metric information. Merely marking a
deletion witness as a pivot does not add a turn constraint, and that marked
witness need not be an endpoint of either inclusion-minimal turn interval.
