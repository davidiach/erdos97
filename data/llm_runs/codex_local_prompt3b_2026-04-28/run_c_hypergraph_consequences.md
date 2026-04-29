# Run C: hypergraph consequences after fragile-cover

Status: second-stage setup only. No contradiction is proved here.

Once the fragile-cover lemma is established, any minimal bad polygon gives a
pointed four-uniform hypergraph.

## Construction

Let F be the set of fragile centers. For each u in F, let S_u be its unique
four-cohort. Then:

1. Self-exclusion: u not in S_u.
2. Uniformity: |S_u| = 4.
3. Cover: every vertex v belongs to S_u for at least one u in F.
4. Pairwise intersection: for u != w, |S_u cap S_w| <= 2.
5. Crossing rule: if S_u cap S_w = {a,b}, then {u,w} separates {a,b} in the
   cyclic order.

The cover property is exactly the fragile-cover lemma. Pairwise intersection
comes from two-circle intersection. The crossing rule comes from the
convex-position crossing lemma.

## Immediate counting consequences

Since the S_u cover n vertices and each has size 4,

```text
|F| >= ceil(n/4).
```

Pair-counting gives

```text
sum_{u in F} binom(|S_u|,2) = 6|F|
```

and every adjacent vertex-pair can appear in at most one cohort, while every
nonadjacent pair can appear in at most two cohorts. Therefore

```text
6|F| <= n + 2 (binom(n,2)-n) = n(n-2).
```

This is not strong enough to contradict large n.

## Stronger data retained from minimality

The proof gives more than bare cover. For each vertex v, there is at least one
witness center u such that:

```text
v in S_u,
u is fragile,
deleting v makes u non-bad.
```

Equivalently, every vertex is not just covered by fragile cohorts; it is covered
by a fragile cohort for which it is deletion-critical.

This suggests a sharper second-stage object: a covered pointed hypergraph
together with a witness map

```text
phi(v) = u, where v in S_u.
```

The map phi records which fragile center certifies failure after deleting v.
The next useful question is whether phi imposes additional cyclic or metric
constraints beyond ordinary cover.

## Next target

The next prompt or computation should test whether the following data can
exist:

1. a cyclic vertex set [n];
2. pointed four-sets (u;S_u) for a subset F of centers;
3. a witness map phi:[n] -> F with v in S_{phi(v)};
4. pairwise intersection and crossing constraints;
5. any additional metric constraints derived from "deleting v makes phi(v)
   non-bad."

This is now a valid continuation of the minimal-counterexample route.
