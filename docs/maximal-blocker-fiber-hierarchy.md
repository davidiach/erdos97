# Maximal blocker-fiber hierarchy

Status: `LEMMA` / proof-facing bridge.  This note does **not** prove Erdős
Problem #97 and does not claim a counterexample.  It strengthens the positive
minimality/fragile-cover information by choosing the blocker assignment
extremally.

## 1. Setting

Let `A` be the carrier of a vertex-minimal hypothetical counterexample.  A
center `p` is **unique-four** if it has exactly one rich positive radius and the
complete class at that radius has exactly four points.  Write that class as

```text
K_p,        |K_p| = 4.
```

The minimality cover says that every source `x in A` lies in `K_p` for at least
one unique-four center `p != x`.

Choose, for every `x in A`, one such center `f(x)`.  Thus

```text
x in K_{f(x)}.
```

For every carrier point `p`, put

```text
k_p = |f^{-1}(p)|.
```

A point which is not used as a blocker has `k_p=0`.  Since
`f^{-1}(p) subset K_p`, every fiber has size at most four.

Among all blocker assignments, choose `f` maximizing

```text
Phi(f) = sum_p k_p^2.
```

All conclusions below refer to such a maximizing assignment.

## 2. Exchange inequality

### Lemma 2.1

If `x in K_p` but `f(x)=q != p`, then

```text
k_q >= k_p + 1.                                      (2.1)
```

### Proof

Reassign only `x`, from `q` to `p`.  This is still a valid blocker assignment,
because `x in K_p`.  The change in `Phi` is

```text
(k_p+1)^2 - k_p^2 + (k_q-1)^2 - k_q^2
  = 2(k_p-k_q+1).
```

Maximality makes this nonpositive, proving (2.1).  ∎

## 3. A saturated four-source fiber

### Lemma 3.1

Some center `p_*` satisfies

```text
f^{-1}(p_*) = K_{p_*},       k_{p_*}=4.              (3.1)
```

### Proof

Take a used center `p_*` with maximum fiber size.  If some
`x in K_{p_*}` were not assigned to `p_*`, Lemma 2.1 would give

```text
k_{f(x)} >= k_{p_*}+1,
```

contradicting maximality of `k_{p_*}`.  Hence all four members of `K_{p_*}`
are assigned to `p_*`.  ∎

This is stronger than merely extracting a repeated blocker fiber: the complete
exact critical shell is the fiber.

## 4. Fiber-level bookkeeping

For `j=0,1,2,3,4`, let

```text
n_j = |{p in A : k_p=j}|.
```

Because the fibers partition `A`,

```text
sum_j n_j = |A|,
sum_j j n_j = |A|.
```

Subtracting gives the exact identity

```text
n_0 = n_2 + 2 n_3 + 3 n_4.                           (4.1)
```

Lemma 3.1 gives `n_4 >= 1`, hence

```text
n_0 >= 3.                                             (4.2)
```

More structure is available than (4.1).  Define the **high-source set**

```text
H = {x in A : k_{f(x)} >= 2},
h = |H|,
m = n_2+n_3+n_4,
ell = n_1,
z = n_0.
```

Then

```text
h = 2 n_2 + 3 n_3 + 4 n_4,
z = h-m,
|A| = h+ell.                                          (4.3)
```

### Lemma 4.2 — row shape relative to `H`

1. If `k_p>=2`, then `K_p subset H`.
2. If `k_p=1`, then `K_p` contains exactly three points of `H` and one point
   outside `H`.

### Proof

An assigned member of `K_p` belongs to `H` whenever `k_p>=2`.  Every unassigned
member `x in K_p` satisfies `k_{f(x)}>=k_p+1` by Lemma 2.1, hence also belongs
to `H`.  This proves the first statement.

If `k_p=1`, its unique assigned source is outside `H`, while each of the other
three class members is unassigned to `p` and therefore has blocker-fiber size
at least two.  ∎

## 5. Pair-capacity inequality

For a fixed unordered pair `{a,b}`, every center whose exact class contains
both points lies on the perpendicular bisector of `ab`.  A line meets the
boundary of a strictly convex polygon in at most two vertices.  Therefore an
unordered witness pair occurs together in at most two complete rich classes.

Count pair occurrences whose two endpoints lie in `H`.

- Every center with fiber at least two has all four class members in `H`, and
  contributes `binom(4,2)=6` pairs.
- Every singleton-fiber center has exactly three class members in `H`, and
  contributes `binom(3,2)=3` pairs.
- Every pair of `H` has capacity at most two.

Consequently

```text
6m + 3ell <= 2 binom(h,2) = h(h-1).                  (5.1)
```

Using (4.3), this becomes

```text
3|A| <= h^2 - 4h + 6z.                               (5.2)
```

The saturated four-fiber improves the elementary bound `h<=2z`.  Indeed,

```text
z-m = n_3 + 2n_4 >= 2,
```

so

```text
m <= z-2,
h=z+m <= 2z-2.                                       (5.3)
```

Since `h^2-4h` is increasing for `h>=2`, (5.2)-(5.3) give the
cardinality-independent inequality

```text
3|A| <= 4z^2 - 10z + 12.                             (5.4)
```

Equivalently, any maximizing blocker assignment has at least the smallest
integer `z` satisfying (5.4) omitted blocker values.

## 6. Immediate consequences

### Corollary 6.1

For `|A|>=9`, one has

```text
n_0 >= 4.
```

For `z=3`, (5.4) gives `3|A|<=18`, hence `|A|<=6`.

### Corollary 6.2

For `|A|>=13`, and in particular on the current all-large-caps branch
`|A|>=15`, one has

```text
n_0 >= 5.                                             (6.1)
```

For `z=4`, (5.4) gives `3|A|<=36`, hence `|A|<=12`.

### Corollary 6.3 — stronger multiplicity packet at `|A|>=15`

A maximizing critical assignment has

1. one saturated four-source fiber; and
2. after that fiber's excess `4-1=3` is removed, at least two further units of
   fiber excess.

Thus one has one of the following:

```text
- a second four-source fiber;
- a three-source fiber;
- at least two additional two-source fibers.
```

This is stronger than the generic two-omission conclusion “two nontrivial
fibers or one fiber of size at least three.”  It also retains one complete
four-source shell exactly equal to its fiber.

## 7. Exact low-`z` profiles

The proof identifies the first two omitted-value profiles completely.

### `z=3`

Equation (4.1) forces

```text
n_4=1, n_2=n_3=0.
```

There is one saturated four-fiber `Q`; every other used center has fiber one,
and its other three witnesses all lie in `Q`.

### `z=4`

Equation (4.1) forces

```text
n_4=1, n_2=1, n_3=0.
```

Let `Q` be the four-source fiber and `R` the two-source fiber.  The latter
center's other two witnesses lie in `Q`.  If

```text
H = Q union R,       |H|=6,
```

then every remaining used center has one assigned source outside `H` and three
witnesses in `H`.  Counting `H`-pairs gives directly

```text
6 + 6 + 3n_1 <= 2 binom(6,2)=30,
```

hence `n_1<=6` and `|A|=4+1+1+n_1<=12`, matching Corollary 6.2.

## 8. Relationship to the live formal proof

The current formal spine already provides:

- the minimal unique-four cover;
- critical-system rebasing, so a favorable blocker selector may be chosen
  late; and
- the all-large-caps lower bound `|A|>=15`.

The useful Lean-facing target is therefore:

```text
D.Minimal
  -> exists Hmax : CriticalShellSystem D.A,
       exists saturated four-source fiber in Hmax
       and at least two further units of blocker-fiber excess.
```

The pair-capacity part then packages the selected supports into the small
high-source set `H`.  At the rigid base `|A|=15`, the first possible profiles
have `z>=5`:

```text
z=5:
  (n_4,n_3,n_2) = (1,1,0),  |H|=7,
  or
  (n_4,n_3,n_2) = (1,0,2),  |H|=8.
```

These are substantially smaller finite geometric surfaces than an arbitrary
15-row selected system.

## 9. Scope boundary

The lemma does not close either remaining global terminal.

- An omitted blocker value need not be deletion-robust; it may be an unused
  unique-four center.
- Inequality (5.4) forces only `z=Omega(sqrt(|A|))`, not a linear density of
  robust centers.
- The remaining step must use the geometry of the saturated shell together
  with the second high fiber, or prove that nonrobust omitted values can be
  eliminated by a source-valid matching/augmentation argument.

The clean next alternatives are:

1. turn the saturated fiber plus the next high fiber into one of the existing
   same-cap or ordered-cross-row contradiction cores; or
2. prove an SDR/augmentation lemma for the family of unique-four classes, so
   omitted blocker values are exactly the robust centers.
