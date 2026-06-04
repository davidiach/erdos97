# Turn-Inequality Lemma

Status: proof-facing lemma note; independent review requested.

This note isolates the geometric lemma used by
`docs/n9-turn-inequality-frontier.md`. It does not prove Erdos Problem #97, does
not claim a counterexample, and does not promote any source-of-truth finite-case
status.

## Statement

Let

```text
p_0,p_1,...,p_{n-1}
```

be the vertices of a strictly convex polygon in counterclockwise cyclic order.
Let `tau_i > 0` be the exterior turn at vertex `p_i`, so
`sum_i tau_i = 2*pi`.

Fix a center `p_i`. Suppose two selected witnesses have cyclic offsets

```text
1 <= a < b <= n-1
```

and equal distance from the center:

```text
|p_{i+a} - p_i| = |p_{i+b} - p_i|.
```

Then

```text
tau_{i+1} + tau_{i+2} + ... + tau_{i+b-1} > pi/2
```

and

```text
tau_{i+a+1} + tau_{i+a+2} + ... + tau_{i+n-1} > pi/2,
```

with indices read modulo `n`.

Equivalently, after normalizing `t_i = 2*tau_i/pi`, the weak inequalities
used in the n=9 replay are

```text
sum_{h=1}^{b-1} t_{i+h} >= 1
sum_{h=a+1}^{n-1} t_{i+h} >= 1.
```

The actual geometry gives strict inequalities; the machine replay intentionally
uses the weaker closed halfspaces.

## Indexing Convention

The replay treats `t_j` as the exterior turn at vertex `p_j`, with indices
modulo `n`. For one center `i` and one selected offset pair `a < b`, the two
forced weak inequalities have this convention:

| orientation | geometric arc | cyclic support before sorting | weak inequality |
| --- | --- | --- | --- |
| `forward` | from `p_i` through `p_{i+b}` | `i+1, ..., i+b-1` | `sum_{h=1}^{b-1} t_{i+h} >= 1` |
| `reverse` | from `p_{i+a}` back to `p_i` | `i+a+1, ..., i+n-1` | `sum_{h=a+1}^{n-1} t_{i+h} >= 1` |

The stored replay sorts supports because the inequalities are sums of turn
variables. For example, in `n=9`, center `i=7`, and offsets `a=1`, `b=4`,
the forward cyclic support is `8,0,1`, stored as `[0,1,8]`; the reverse
support is `0,1,2,3,4,5,6`.

The indexing audit

```bash
python scripts/check_turn_inequality_indexing.py --check --assert-expected --summary-json
```

exhaustively checks this convention against the current term emitter for all
`70` row-offset subsets and `9` centers in `n=9`. It verifies `630` row
instances, `504` unique center/pair/orientation records, and `7560` emitted
term records. This is an indexing audit only; it does not prove the geometric
lemma.

## Proof Sketch

Let

```text
u = p_{i+a} - p_i,
v = p_{i+b} - p_{i+a}.
```

The equality of distances gives

```text
|u+v| = |u|.
```

After squaring and cancelling `|u|^2`,

```text
2 u.v + |v|^2 = 0,
```

so

```text
u.v = -|v|^2/2 < 0.
```

Now write `u` as the positive sum of edge vectors along the arc from `p_i` to
`p_{i+a}`, and write `v` as the positive sum of edge vectors along the arc from
`p_{i+a}` to `p_{i+b}`. If the total exterior turn from `p_i` through
`p_{i+b}` were at most `pi/2`, all those edge directions would lie in a closed
cone of angle at most `pi/2`. Every pairwise dot product between an edge vector
from the first sum and an edge vector from the second sum would then be
nonnegative, forcing `u.v >= 0`, contradiction.

Therefore the turn along that arc is strictly greater than `pi/2`, proving the
first inequality.

For the second inequality, apply the same dot-product argument to the
complementary arc from `p_{i+a}` back to `p_i`, using

```text
u' = p_{i+b} - p_{i+a},
v' = p_i - p_{i+b}.
```

Now `|v'| = |p_i - p_{i+b}| = |p_i - p_{i+a}| = |u' + v'|`. Squaring and
cancelling gives

```text
2 u'.v' + |u'|^2 = 0,
```

so `u'.v' < 0`. Here `u'` is the positive sum of edge vectors on the arc from
`p_{i+a}` to `p_{i+b}`, and `v'` is the positive sum of edge vectors on the arc
from `p_{i+b}` to `p_i`. If the complementary arc from `p_{i+a}` back to `p_i`
had total exterior turn at most `pi/2`, those edge directions would lie in a
closed cone of angle at most `pi/2`, again forcing all cross dot products
nonnegative. This contradiction proves the second inequality.

## Review Points

The lemma is short, but it is now the main bottleneck for the review-pending
n=9 turn-frontier artifact. Reviewers should check:

- the indexing of both arcs;
- the use of a closed cone when the turn is exactly `pi/2`;
- that strict convexity gives positive edge lengths and strictly positive
  exterior turns;
- that the normalized weak inequalities used by the checker are legitimate
  consequences of the strict geometric inequalities.
