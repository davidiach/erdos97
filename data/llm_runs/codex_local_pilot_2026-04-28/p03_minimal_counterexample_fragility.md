# Prompt 3 local output: minimal-counterexample fragility

Status: fragile-cover lemma not proved. The first gap is identified precisely.

Let

```text
m_u(P)=max_r #{v != u : |p_v-p_u|=r}.
```

Assume P is a minimal bad polygon: m_u(P) >= 4 for every vertex u, but P-v is
not bad for every deleted vertex v.

## What minimality actually proves

Lemma, weak deletion cover. For every vertex v, there exists a remaining center
u != v such that:

1. m_u(P-v) <= 3;
2. every radius r with #{w != u : |p_w-p_u|=r} >= 4 in P has exact count 4;
3. every such rich radius contains v in its cohort.

Proof. Since P-v is not bad, some remaining center u has m_u(P-v) <= 3. Since P
is bad, u has at least one rich radius in P. Let r be any radius for u whose
cohort in P has size at least 4. After deleting v, the same radius has cohort
size either unchanged or reduced by one. Since m_u(P-v) <= 3, this reduced size
is at most 3. Therefore the original size was exactly 4 and v belonged to that
cohort. This holds for every rich radius r of u.

This is the exact place where minimality is used.

## Why this does not imply fragility

Fragility requires that u have a unique radius r_u whose cohort has exact size
four. The weak deletion cover only says that all rich radii of u are exact
four-cohorts and all contain the deleted vertex v. It does not say there is only
one such radius.

The deletion scenario not excluded by minimality is:

```text
S_u(r) = {v,a,b,c},
S_u(s) = {v,d,e,f},
r != s,
```

with no radius for u having five or more vertices, and with every rich radius of
u containing v. Then deleting v drops all rich cohorts of u from size 4 to size
3, so u certifies that P-v is not bad. But u is not fragile, because there are
two distinct exact four-cohorts.

Minimality does not rule this out. It only requires that after deleting v at
least one remaining center becomes non-bad. It does not require that this center
had a unique maximum radius before deletion.

## Consequence for the proposed fragile-cover lemma

The proposed lemma says:

```text
Every vertex v is contained in the unique four-cohort of at least one fragile
center u.
```

The proof attempt breaks exactly at "unique". A correct lemma currently
available from minimality is:

```text
Every vertex v is contained in every rich cohort of at least one center u whose
rich cohorts all have exact size four.
```

Call such a center v-pinned rather than fragile.

## Stage two under the original fragile-cover assumption

If the fragile-cover lemma were assumed, one obtains a pointed 4-uniform
hypergraph on the cyclic vertex set: each fragile center u contributes its
unique cohort S_u. This hypergraph satisfies:

1. cover: every vertex lies in at least one S_u;
2. self-exclusion: u not in S_u;
3. pairwise intersection: |S_u cap S_w| <= 2;
4. crossing: if S_u cap S_w = {a,b}, then {u,w} separates {a,b}.

This alone gives only weak counting. If F is the set of fragile centers, then
4|F| cohort incidences cover n vertices, so |F| >= ceil(n/4). Pair-counting also
gives

```text
6|F| <= n(n-2),
```

using the same adjacent/nonadjacent pair bounds as in the centered-matrix
route. Neither inequality contradicts large n.

## Strongest conclusion

The fragile-cover route should be rewritten around the weaker deletion-cover
lemma. The key new subproblem is:

Can the multi-rich-radius scenario

```text
S_u(r_1), S_u(r_2), ..., all exact four-cohorts, all containing v
```

be ruled out by strict convexity, or does it create a finite obstruction pattern
for enumeration?

Until that question is answered, the fragile-cover lemma is not justified.
