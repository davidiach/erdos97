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
python scripts/check_n9_turn_inequality_frontier.py --check --assert-expected --json
```

checks the stored `n=9` frontier artifact. It regenerates the 184 complete
selected-witness assignments surviving the pair/crossing/count filters before
vertex-circle pruning and verifies one integer turn-packing certificate for
each assignment. The replay is arithmetic after the stored interval choices:
180 certificates use `lambda = 1` and five intervals; 4 use `lambda = 2` and
nine intervals.

This is review-pending finite-case evidence only. It does not promote the
repo source-of-truth status, and it does not imply a general theorem without a
bridge proving that arbitrary counterexamples reduce to turn-packing-obstructed
selected systems.
