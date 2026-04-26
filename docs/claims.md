# Claims ledger

This file separates proved statements from heuristics and numerical evidence.

## Theorems / lemmas currently considered valid

### Lemma 1: pairwise circle-intersection cap

In any true counterexample, for distinct centers `a,b`,

```text
|S_a ∩ S_b| <= 2.
```

Proof: if three selected vertices were common to `S_a` and `S_b`, then two distinct Euclidean circles centered at `p_a` and `p_b` would share at least three points. Two distinct circles intersect in at most two points.

### Lemma 2: incidence counting implies n >= 7

Let `d_j = #{ i : j in S_i }`. Since every center selects four vertices,

```text
sum_j d_j = 4n.
```

The pairwise cap gives

```text
sum_j binom(d_j, 2) <= 2 binom(n, 2).
```

By convexity of `binom(d,2)` and average indegree 4,

```text
sum_j binom(d_j, 2) >= n binom(4,2) = 6n.
```

Hence `6n <= n(n-1)`, so `n >= 7`.

### Lemma 3: n=7 equality case

For `n=7`, equality must hold in the counting argument. Thus every indegree is 4 and every pair of selected 4-sets intersects in exactly 2 points. The complements `T_i = V \ S_i` form a Fano-plane-like family of 3-sets with pairwise intersection 1. If `S_i ∩ S_j = {a,b}`, then the chord `p_a p_b` is the radical axis of the two selected circles and is perpendicular to `p_i p_j`.

## Heuristics

- Balanced selected vertices around the polygon often search better than clustered selected vertices.
- Highly symmetric incidence can help reduce pattern space but full coordinate symmetry often forces regular-polygon degeneracy.
- The `B12_3x4_danzer_lift` pattern is useful as a degeneration test case, not currently as a candidate counterexample.

## Numerical evidence

The best saved `B12` run has max spread about `0.00680637` and convexity margin about `1e-6`. It is recorded as a near-miss degeneration.
