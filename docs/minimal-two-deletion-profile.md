# Minimal two-deletion profile lemma

Status: `LEMMA` / full-rich-class minimality consequence. No general proof of
Erdos Problem #97 and no counterexample are claimed.

This note strengthens the singleton fragile-cover consequence in
`docs/minimal-fragile-cover-bridge.md`. Deleting two vertices restricts the
*entire* rich-class profile of at least one surviving center, rather than only
selecting one exact four-tie.

## Definitions

Let `P` be a counterexample with the minimum possible number `n` of vertices,
assuming a counterexample exists. For a center `y` and radius `r>0`, write

```text
C_y(r) = {v in V(P) \ {y} : |p_y p_v| = r}.
```

A class is **rich** when its size is at least four. Classes of size at most
three are called small. Distance classes at one center are pairwise disjoint.

For an unordered deletion pair `A={x,z}`, say that a surviving center
`y notin A` **certifies** `A` when `y` is good in `P-A`; equivalently, every
distance class at `y` has at most three surviving members.

## Two-deletion profile lemma

For every unordered pair `A={x,z}` of vertices, there is a certifying center
`y notin A`. At every such certifying center, the full family of rich classes
in the original polygon has exactly one of the following forms:

1. `T4`: one class `C` of size four, with `C cap A` nonempty;
2. `T5`: one class `C` of size five, with `A subset C`;
3. `T44`: two classes `C_1,C_2`, both of size four, with the two seeds split
   between them: after possibly exchanging the names of the seeds,
   `x in C_1` and `z in C_2`.

In the third case disjointness also gives `x notin C_2` and `z notin C_1`.
There are no other rich classes at `y`. Small classes are unrestricted and
irrelevant to the assertion.

Conversely, a surviving center with one of these three profiles and the stated
incidence with `A` certifies `A`.

### Proof

Deleting two vertices from a strictly convex polygon leaves a smaller set in
convex position. By cardinality-minimality it is not a counterexample, so it
has a good surviving center `y`. Thus a certifying center exists.

Let `C` be any rich class at `y` in the original polygon and put `s=|C|`.
Since at most three members of `C` survive, one must have

```text
|C cap A| >= s-3.                                    (1)
```

The left side is at most two, so `s<=5`. A size-four class consumes at least
one of the two deletion seeds; a size-five class consumes both. Since distinct
classes at `y` are disjoint, there can be at most two rich classes.

If there is one rich class, it has size four or five. Equation (1) gives the
incidence stated in `T4` or `T5`. If there are two, each must consume a
different seed, so both have size four and the seeds split between them. A
third rich class would require a third seed. Finally, `y` was bad in the
original counterexample, so there is at least one rich class. This proves that
the list is exhaustive.

The converse follows by deleting the stated seed or seeds from every listed
rich class. Each becomes a class of size at most three, and all originally
small classes already had size at most three. Hence `y` is good in `P-A`.

## Exact pair-coverage ledger

Fix a center `y` of one of the three types. Count unordered pairs
`A subset V(P)\{y}` that it certifies. The exact capacities are

```text
q_T4(n)  = binom(n-1,2) - binom(n-5,2) = 4n-14,
q_T5     = binom(5,2)                   = 10,
q_T44    = 4*4                          = 16.
```

The first count chooses every pair meeting the unique four-class. The second
chooses both seeds from the unique five-class. The third chooses one seed from
each disjoint four-class.

Let `a,b,c` be the numbers of centers of types `T4,T5,T44`, respectively.
Double-counting pairs together with a certifying center gives the necessary
inequality

```text
binom(n,2) <= (4n-14)a + 10b + 16c.                  (2)
```

The singleton-deletion lemma already implies that the `T4` classes cover all
vertices, hence `4a>=n`. This is stronger than what (2) alone asks when
`b=c=0`; therefore coarse averaging of (2) does **not** force a `T5` or `T44`
center. Any further use must control overlap among the `T4` pair-cover sets,
not only their total capacity.

## Exclusive mutual-pair corollary

For a vertex `x`, define its set of `T4` covering centers by

```text
Gamma(x) = {y : y has type T4 and x lies in its unique four-class F_y}.
```

Singleton minimality gives `Gamma(x)` nonempty for every `x`. Call
`{x,z}` an **exclusive mutual pair** when

```text
Gamma(x) = {z}  and  Gamma(z) = {x}.
```

Then the deletion pair `{x,z}` has no `T4` certifier. Consequently its
two-deletion certifier is a `T5` or `T44` center outside `{x,z}`.

Proof. A `T4` center `y` certifies `{x,z}` exactly when

```text
y in (Gamma(x) union Gamma(z)) \ {x,z}.
```

For an exclusive mutual pair this set is empty. The profile lemma supplies a
certifier and leaves only types `T5` and `T44`.

The converse obstruction is also exact: if a pair has no `T4` certifier, then
`Gamma(x) union Gamma(z)` is contained in `{x,z}`. A center never belongs to
its own distance class, while both covering sets are nonempty. Therefore
`Gamma(x)={z}` and `Gamma(z)={x}`.

Exclusive mutual pairs are vertex-disjoint, so if `e` is their number then

```text
e <= floor(n/2),
e <= 2b + 4c.                                        (3)
```

For the second bound, charge each exclusive pair to one richer certifier. A
fixed `T5` center can receive at most two charged pairs, because their endpoints
form a matching inside its five-class. A fixed `T44` center can receive at
most four, because their endpoints form a matching between its two disjoint
four-classes. This matching refinement is stronger than the raw capacities
`10` and `16`. It only forces a richer profile when `e>0`; the current bridge
does not force an exclusive mutual pair.

The companion `docs/all-rich-class-pair-budget.md` counts every rich class at
every center simultaneously.  Before using its bounds, there is another
constraint hidden in the definition.  Both endpoints of an exclusive mutual
pair are themselves `T4` centers: from `Gamma(x)={z}` and
`Gamma(z)={x}`, center `z` has type `T4`, as does center `x`.  If `a` is the
number of `T4` centers, disjointness of the pairs gives

```text
a >= 2e,
2e + b + c <= n.                                    (4)
```

Together with (3), this already yields

```text
e <= 4(b+c),
e <= floor(4n/9).                                   (5)
```

The endpoint classes carry still more incidence structure.  Let `E` be the
`2e` exclusive endpoints and `N=V\E`.  For an endpoint `x` with mate `z`,

```text
F_x = {z} union B_x,  B_x subset N,  |B_x|=3.       (6)
```

Indeed, if `F_x` contained an endpoint of another exclusive pair, then `x`
would be a second member of that endpoint's `Gamma` set.  Thus the `2e`
endpoint rows contribute `6e` incidences and `6e` unordered witness-pair
occurrences inside `N`.  The companion all-rich-class budget combines these
facts with localized and edge-sensitive capacities.  In particular, at
`n=9` every center is forced to be `T4`, so `e=0`; for larger `n` the
resulting upper bounds are stricter than the raw matching bound but still do
not force `e>0` or give a contradiction.

## General deficit form

The same proof gives a useful formulation for a deletion seed `A` of any
size. A center `y notin A` is good after deleting `A` exactly when every rich
class `C` at `y` satisfies

```text
|C cap A| >= |C|-3.
```

Because the rich classes at one center are disjoint, their demands consume
disjoint seed vertices. In particular,

```text
sum_{C rich at y} (|C|-3) <= |A|.
```

For `|A|=1` this is the fragile exact-four lemma; for `|A|=2` it gives the
complete profile classification above. This deficit inequality is necessary,
but without the class-by-class incidence requirements it is not sufficient.

## Verification

The arithmetic and finite-set ledger can be replayed with

```bash
python scripts/check_minimal_two_deletion_profile.py --check --json
python -m pytest -q tests/test_minimal_two_deletion_profile.py
```

The checker verifies capacities, the averaging comparison, an abstract
exclusive-mutual fixture, and the forced `2e` endpoint-center floor.  The
companion all-rich checker replays the endpoint incidence and pair bounds.  It
does not verify minimality, enumerate the profile classification, establish
incidence-system attainability, verify Euclidean geometry, or assume a
counterexample exists.

## Scope

This lemma is a stronger bridge constraint, not a contradiction. Abstract
singleton-rich systems may have no exclusive mutual pair, and inequality (2)
allows the `T4` profiles already required by singleton deletion to cover all
deletion pairs. A global proof still needs a geometric reason for excessive
`T4` overlap, an exclusive mutual pair, or another forbidden rich-profile
configuration.
