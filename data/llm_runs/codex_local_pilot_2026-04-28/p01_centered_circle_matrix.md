# Prompt 1 local output: centered-circle incidence matrix

Status: partial progress only. No proof of the full theorem is claimed.

Let the cyclically ordered vertices be indexed modulo n. For each row i, let
S_i be the selected cohort and let s_i=|S_i|.

## Convex-position crossing lemma

Lemma. If i != k and S_i cap S_k contains distinct a,b, then {i,k} separates
{a,b} in the cyclic order.

Proof. The points p_a and p_b lie on both selected circles

```text
|x-p_i|=r_i,     |x-p_k|=r_k.
```

Subtracting the squared equations gives

```text
2 x dot (p_k-p_i) = |p_k|^2-|p_i|^2+r_i^2-r_k^2.
```

Thus p_a and p_b lie on the same radical axis, a line perpendicular to
p_k-p_i. In coordinates whose x-axis is the line p_i p_k, the two circle
intersections have the form (c,y) and (c,-y), with y != 0 because a and b are
distinct. Hence p_a and p_b lie on opposite sides of the line p_i p_k.

Strict convexity is now used. For the chord p_i p_k of a strictly convex
polygon, all vertices different from i,k lie strictly off the line p_i p_k.
Moreover the two cyclic arcs from i to k lie in the two opposite open halfplanes
bounded by that line. Since p_a and p_b are in opposite halfplanes, they lie on
opposite arcs. Equivalently, {i,k} separates {a,b}.

## Consequences for the cyclic matrix

Corollary 1. If i and k are adjacent cyclically, then |S_i cap S_k| <= 1.

If they shared a,b, the pair {i,k} would have to separate {a,b}. Adjacent
cyclic vertices leave one open arc empty, so no two other vertices can be
separated by {i,k}.

Corollary 2. If a and b are adjacent cyclically, then at most one row contains
both a and b.

If two rows i,k both contained a,b, then {i,k} would have to separate {a,b}.
Again an adjacent pair cannot be separated by any other pair.

Corollary 3. For every unordered pair {a,b}, at most two rows contain both
a and b.

If three rows i,k,l contained a,b, then each pair among i,k,l would have to be
separated by {a,b}. But the two arcs cut by a,b give only two sides. Two of
i,k,l lie on the same arc, and that pair is not separated by {a,b}.

Combining Corollaries 2 and 3 gives a pair-count inequality. Let t_ab be the
number of selected rows containing both a and b. Then

```text
sum_i binom(s_i,2) = sum_{a<b} t_ab
                  <= n + 2 (binom(n,2)-n)
                  = n(n-2),
```

where the n adjacent cyclic pairs have t_ab <= 1 and the nonadjacent pairs have
t_ab <= 2.

If every selected row has size at least four, then

```text
6n <= sum_i binom(s_i,2) <= n(n-2).
```

Therefore the axioms alone already rule out such a selected system for n <= 7.

## Exact theorem proved

The theorem proved here is:

Given only the circle-intersection constraint and the convex-position crossing
lemma, no cyclic selected-cohort matrix with all row sums at least four exists
for n <= 7. For n = 8, any surviving matrix must have all row sums exactly four,
every adjacent column-pair appearing in exactly one row, and every nonadjacent
column-pair appearing in exactly two rows.

The n = 8 conclusion follows because equality must hold throughout

```text
6n <= sum_i binom(s_i,2) <= n(n-2).
```

At n=8, both sides are 48, so no row can have size greater than four and every
allowed pair-count bound must be saturated.

## Remaining unresolved patterns

The unresolved n=8 pattern class is exact:

1. M is an 8-by-8 zero-diagonal 0-1 matrix.
2. Every row has sum 4.
3. Every adjacent column-pair occurs together in exactly one row.
4. Every nonadjacent column-pair occurs together in exactly two rows.
5. Adjacent rows have intersection size at most 1.
6. Whenever rows i,k share exactly columns a,b, the pairs {i,k} and {a,b}
   alternate in cyclic order.

This is a strong finite combinatorial target, but it is not yet a contradiction.
It also does not address metric realizability of any surviving matrix.
