# Exact bounded obstruction for the real two-mode cyclic family

Status: **exact bounded restricted-family obstruction, review pending**.
This is a computer-assisted theorem about one finite-dimensional family.  It
is not a proof of Erdos Problem 97.

## Statement

Let

```text
z_i = w^i + t w^(ki),       w = exp(2 pi i/n),       t real.
```

For every integer `9 <= n <= 80`, every `2 <= k <= n-2`, and every real
`t`, the labelled configuration cannot simultaneously have all three
properties below:

1. the `n` labels give distinct points;
2. all points are vertices of a strictly convex polygon; and
3. from every point, some distance to the other labels occurs at least four
   times.

The exact replay covers all 2,988 pairs `(n,k)`.  Its retained output is
`data/certificates/two_mode_cyclic_exact_n80.json`.

## Exact distance algebra

Put

```text
S_m = 2 cos(2 pi m/n).
```

All calculations take place in the exact number field
`K = Q(S_1)`.  Direct expansion gives

```text
|z_(i+s)-z_i|^2 = A_s + B_(i,s) t + C_s t^2,

A_s     = 2-S_s,
C_s     = 2-S_(ks),
B_(i,s) = S_((k-1)(i+s)) - S_((k-1)i-s)
          - S_((k-1)i+ks) + S_((k-1)i).
```

Thus every equality between two distances in a fixed row is a polynomial
equation of degree at most two over `K`.

## Why the candidate list is complete

For row zero, the verifier first groups shifts whose squared-distance
polynomials are identically equal.  It proves in every one of the 2,988
cases that each such identity class has size at most two.

If four row-zero distances are equal at a real parameter `t`, those four
shifts therefore meet at least two distinct identity classes.  The difference
of the two class polynomials vanishes at `t`.  The verifier enumerates every
pair of distinct classes, so its root list contains every possible parameter
of a putative example.  The enumeration is intentionally redundant; the
reported root count is a count of pair-root occurrences, not necessarily of
distinct real parameters.

Exact degree and discriminant-zero tests are performed in `K`.  Under the
principal real embedding, python-flint/Arb supplies outward-rounded root
enclosures and proves every nonzero sign.  A sign that remains ambiguous is
reported as unresolved rather than guessed.

## Three rigorous terminal certificates

Every real root occurrence is closed in one of three ways.

### Row-value bands

For a row, Arb encloses all `n-1` squared distances.  A cut is accepted only
when the maximum upper endpoint on its left is strictly below the minimum
lower endpoint on its right.  Dynamic programming partitions the values
along such cuts into bands of size at most three.  Equal exact values cannot
cross a certified cut, so no distance in that row has multiplicity four.

Only `d=n/gcd(n,k-1)` row types need checking, because
`z_(i+d)=w^d z_i` rotates one row to the next equivalent row.

### Regular-orbit inradius

Let `g=gcd(n,k-1)` and `d=n/g`.  The points split into `d` regular `g`-gons
centered at the origin.  After a permutation of the orbit labels, their
squared radii are

```text
q_j = 1+t^2+t S_(gj),       0 <= j < d.
```

The permutation is valid because `(k-1)/g` is coprime to `d`.  If two
orbits `a,b` satisfy

```text
q_b > 0,
4 q_a - (2+S_d) q_b < 0,
```

then the entire `a` orbit lies strictly inside the regular polygon formed by
the `b` orbit, since `(2+S_d)/4 = cos^2(pi/g)`.  Hence not every point can be
extreme.  Arb must prove both strict inequalities.

### Exact duplicate

If neither preceding test closes a root, exact polynomial gcds test whether
some labelled separation has squared distance zero at that selected root.
A full common factor handles both branches at once; a linear common factor is
matched to exactly one separated Arb root enclosure.  A zero squared distance
means two distinct labels coincide, which rules out strict convexity.

## Retained replay

The canonical run and an independent replay under the lock both reported:

| Quantity | Exact count |
|---|---:|
| `(n,k)` parameter pairs | 2,988 |
| row-zero identity classes | 81,294 |
| class-pair collision polynomials | 1,186,326 |
| real pair-root occurrences | 1,865,543 |
| certified row failures | 1,469,483 |
| strict inradius obstructions | 395,893 |
| exact duplicates | 167 |
| unresolved occurrences | **0** |

The maximum row-zero identity-class size was exactly two.  The terminal counts
sum to the real-root occurrence count.  The canonical case digest is
`fb546261b6d17eb239ad18fb7ec39c15a5685b96cf7de9a8913d07eca1e2f48f`.

The closure gate is all-or-nothing: maximum row-zero identity-class size at
most two, every real root occurrence assigned one of the three terminals, and
`unresolved = 0`.  The case summaries and their witness digests are retained
in the JSON transcript.

Rows are tried in increasing canonical order.  The sign of the Arb parameter
ball chooses the canonical minimum- and maximum-cosine orbit phases.  Thus
binary floating point is absent even from witness selection; every decision
uses exact field arithmetic or outward-rounded Arb intervals.

## Reproduction

Use CPython 3.12 and the pinned exact-backend dependencies:

```bash
python3 -m venv .venv-two-mode
.venv-two-mode/bin/python -m pip install -e .[dev]
.venv-two-mode/bin/python -m pytest -q tests/test_two_mode_cyclic_exact.py
.venv-two-mode/bin/python scripts/check_two_mode_cyclic_exact.py \
  --min-n 9 --max-n 80 --jobs 4 --assert-closed \
  --check-artifact data/certificates/two_mode_cyclic_exact_n80.json
```

The retained JSON embeds its generator and replay commands.  Exact backend
versions are pinned in the repository dependency snapshot.

## External review checklist

An independent reviewer should check, in order:

1. the displayed squared-distance coefficient formula;
2. the implication from identity-class size at most two to complete row-zero
   candidate coverage;
3. exact degree/discriminant handling and Arb root-branch separation;
4. the certified band-cut implication for distance multiplicity;
5. the regular-orbit permutation and inradius inequality; and
6. the exact gcd argument for branch-specific duplicate labels.

They should then rerun the focused tests and retained full certificate.  The
repository's own construction and audits are not external or peer review; the
result remains explicitly review pending.

## Scope boundary

This result says nothing about arbitrary point configurations, unbounded
`n`, complex coefficients, or additional Fourier modes.  It converts the
+
the real two-mode family and finite range stated above.  Erdos Problem 97
remains open beyond the exact small-`n` and restricted-family results recorded
by the repository.
