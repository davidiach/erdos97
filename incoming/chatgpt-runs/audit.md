# Audit of ChatGPT Runs on the A/B Matrix Argument

Status: draft audit note, not a theorem file.

This note reviews `run-01.md` through `run-20.md` against the original prompt.
It treats all LLM outputs as hypotheses until checked.

## Executive Summary

The stable, reusable result across the runs is:

> From facts (A) and (B) one gets
> \[
> \sum_i \binom{|S_i|}{2}\le n(n-2).
> \]
> Therefore minimum row size 4 implies \(n\ge 8\).

The full contradiction cannot follow from (A) and (B) alone. This was
computationally checked for the recurring circulant examples, and there are
stronger abstract examples with row sums growing like \(\sqrt n\) where (B) is
vacuous.

The best proof of the crossing lemma is the coordinate/extreme-point proof:
the radical-axis/reflection step shows the two shared vertices are symmetric
across \(p_ip_k\), and strict convexity is used to force the midpoint of
\(p_ap_b\) to lie in the open segment \(p_ip_k\). This avoids relying on a
hand-wavy half-plane chain statement.

## Safe Theorem Skeleton

Let \(M\) be a cyclically indexed zero-diagonal \(0\)-\(1\) matrix with row
sets \(R_i\), satisfying:

1. \(|R_i\cap R_k|\le 2\) for \(i\ne k\).
2. If \(R_i\cap R_k=\{a,b\}\), then \(\{i,k\}\) separates \(\{a,b\}\) in the
   cyclic order.

Then:

1. Noncrossing all-one \(2\times2\) submatrices are forbidden.
2. All-one \(2\times3\) submatrices are forbidden.
3. All-one \(3\times2\) submatrices are forbidden.
4. Adjacent column pairs occur together in at most one row.
5. Nonadjacent column pairs occur together in at most two rows.

Discharging row-pairs of ones to unordered column pairs gives
\[
\sum_i \binom{|R_i|}{2}
\le
n+2\left(\binom n2-n\right)
=n(n-2).
\]

If every \(|R_i|\ge 4\), then \(6n\le n(n-2)\), so \(n\ge 8\).

The total-incidence consequence is also valid:
\[
\sum_i |R_i|
\le
\frac n2\left(1+\sqrt{8n-15}\right).
\]

This is \(O(n^{3/2})\), so it cannot contradict \(\sum_i |R_i|\ge 4n\) for
large \(n\).

## Verified Matrix Survivors

I checked the recurring circulant claims with a small cyclic separator checker.
For a circulant row template \(D\subset \mathbb Z_n\), row \(i\) is \(i+D\).
For every shift \(t\), the checker tested:

1. \(|D\cap(t+D)|\le 2\).
2. If the intersection has size 2, its two columns lie on opposite cyclic arcs
   between \(0\) and \(t\).

Verified examples:

| Template | Range checked / claim | Result |
| --- | --- | --- |
| \(D=\{1,2,5,7\}\) | \(n=8\) | valid; equality example |
| \(D=\{1,2,4,8\}\) | all \(n\ge 9\) | valid; lists for \(9\le n\le14\) match |
| \(D=\{1,2,5,7\}\) | all \(n\ge 8\) | valid |
| \(D=\{-3,-1,1,2\}\) | all \(n\ge 8\) | valid |
| \(D=\{-1,1,2,4\}\) | all \(n\ge 9\) | valid |
| \(D=\{-2,-1,2,4\}\) | all \(n\ge 9\) | valid |

The sparse Sidon-type templates in the runs were also checked at their stated
sufficient thresholds. They are valid and usually conservative:

| Template | Stated sufficient range | Checked result |
| --- | --- | --- |
| \(\{1,3,7,15\}\) | \(n\ge29\) | valid, (B) vacuous |
| \(\{1,4,10,20\}\) | \(n\ge39\) | valid, (B) vacuous |
| \(\{2,5,9,14\}\) | \(n\ge25\) | valid, (B) vacuous |
| \(\{2,5,11,23\}\) | \(n\ge43\) | valid, (B) vacuous |
| \(\{1,4,10,18\}\) | \(n\ge35\) | valid, (B) vacuous |
| \(\{3,7,15,26\}\) | \(n\ge47\) | valid, (B) vacuous |
| \(\{1,3,7,12\}\) | \(n\ge23\) | valid, (B) vacuous |
| \(\{1,2,5,10\}\) | \(n\ge19\) | valid, (B) vacuous |

The explicit 13-row pattern in `run-16.md` was checked: every row has size 4,
the diagonal is zero, and every pair of rows intersects in exactly one column.
Thus (A) holds strongly and (B) is vacuous.

The finite-field affine-line construction in `run-19.md` is valid over actual
finite fields. I checked the prime cases \(q=5,7\) directly over \(\mathbb F_q\):
diagonal zero, all rows have size \(q\), and row intersections are at most one.
This shows A/B allow row sums of order \(\sqrt n\), so no constant upper bound
on row sums can follow from A/B alone.

## Extra Geometry Claims

These claims use information beyond (A) and (B). They should not be folded into
the matrix-only theorem.

### Geometric impossibility for n = 8

The `n=8` matrix equality structure is valid:

1. Every row has size 4.
2. Every column has size 4.
3. Adjacent row pairs meet in exactly one column.
4. Nonadjacent row pairs meet in exactly two columns.
5. Every row contains its two cyclic neighbors.

The strongest additional geometric argument appears in `run-20.md`:

1. For every side \(\{j,j+1\}\), one of rows \(j-1\) or \(j+2\) contains both
   endpoints of that side.
2. If row \(j-1\) contains \(j,j+1\), then triangle
   \(p_{j-1}p_jp_{j+1}\) is isosceles with base \(p_jp_{j+1}\), so the
   polygon angle at \(p_j\) is acute.
3. Similarly, if row \(j+2\) contains \(j,j+1\), the angle at \(p_{j+1}\) is
   acute.
4. Hence every side has at least one acute endpoint, so no two non-acute angles
   are adjacent. In an 8-cycle, at most four angles are non-acute.
5. The angle sum is then strictly less than
   \(4\cdot90^\circ+4\cdot180^\circ=1080^\circ\), contradicting the octagon
   angle sum.

This looks valid, but it is not an A/B-only consequence.

The spectral argument in `run-05.md` for excluding the symmetric `n=8`
geometric equality case also appears internally consistent, but it is more
fragile and less direct than the angle proof.

### Acute-angle obstruction for simple circulants

For templates containing \(i+1,i+2\in R_i\) for every \(i\), a geometric
realization would force
\[
|p_i-p_{i+1}|=|p_i-p_{i+2}|.
\]
In triangle \(p_ip_{i+1}p_{i+2}\), this implies the polygon interior angle at
\(p_{i+1}\) is acute. If this holds for every \(i\), all angles are acute,
which is impossible for any convex \(n\)-gon with \(n\ge4\).

This correctly rules out several simple circulant survivors geometrically, but
not the sparse Sidon-type survivors.

### Row-sum 5 sharpening

The row-sum-at-least-5 aside in `run-13.md` checks out as a matrix-level
claim:

1. The same counting gives \(n\ge12\).
2. The equality case \(n=12\) would force the Gram matrix
   \(G=2J+3I-A(C_{12})\).
3. Its determinant is \(2^8 3^4 5^3\), not a square.
4. Since \(G=MM^T\) for an integer matrix \(M\), this is impossible.

The row-sum-5 circulant \(D=\{1,2,5,10,12\}\) modulo 13 was also checked and
satisfies A/B, so the threshold \(n\ge13\) is sharp for that matrix statement.

This is interesting but secondary to the original row-sum-4 prompt.

## Claims to Soften or Avoid

1. Do not say the pair-count theorem is the "strongest possible" without
   qualification. It is the strongest theorem proved in these runs, and the
   \(n\ge8\) threshold is sharp, but "strongest possible" is too broad unless
   formalized.
2. Do not present any circulant survivor as geometrically realizable. The runs
   mostly avoid this, but the distinction should stay explicit.
3. Do not use the `q=4` finite-field example with ordinary arithmetic modulo
   4. It requires the actual field \(\mathbb F_4\). Prime cases such as
   \(q=5,7\) are straightforward.
4. The half-plane proof of the crossing lemma is acceptable only if it clearly
   justifies why the line through two vertices separates the two boundary
   chains into opposite open half-planes. The coordinate/extreme-point proof is
   cleaner and safer.

## Suggested Repo Use

If promoting any of this into main documentation, the safest additions are:

1. A lemma file or note with the coordinate proof of the crossing lemma.
2. A matrix-only theorem stating the discharging bound and \(n\ge8\).
3. A clearly labeled section of abstract A/B countermodels, especially
   \(C_8(\{1,2,5,7\})\), \(C_n(\{1,2,4,8\})\) for \(n\ge9\), and the
   finite-field linear construction.
4. A separate "extra geometry beyond A/B" note for the \(n=8\) angle
   contradiction.

None of these should be stated as solving Erdos Problem #97.
