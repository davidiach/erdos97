# Run A: fragile-cover repair

Status: the fragile-cover lemma is proved from minimality. This does not prove
the original Erdos #97 statement.

## Lemma

Let P be a minimal bad polygon. Then every vertex v of P is contained in the
unique four-cohort of at least one fragile center u.

## Proof

For a center u and radius r, write

```text
C_P(u,r) = {w in P : w != u and |p_w-p_u| = r}.
```

Fix a vertex v. By minimality, P-v is not bad. Therefore there is some remaining
vertex u != v such that

```text
m_u(P-v) <= 3.
```

This is the only use of minimality.

Since P is bad, there exists at least one radius r with

```text
|C_P(u,r)| >= 4.
```

For any such rich radius r, compare the same radius after deleting v:

```text
|C_{P-v}(u,r)| = |C_P(u,r)| - 1_{v in C_P(u,r)}.
```

Because m_u(P-v) <= 3, the left side is at most 3. Since |C_P(u,r)| >= 4, the
only possibility is

```text
|C_P(u,r)| = 4
```

and

```text
v in C_P(u,r).
```

Thus every rich radius r for u in P contains v. But v has only one distance from
the fixed center u. Hence every rich radius r equals

```text
|p_v-p_u|.
```

So there is exactly one rich radius for u. Its cohort has exact size 4. Hence
m_u(P)=4, u is fragile, and v lies in the unique four-cohort of u.

This proves the fragile-cover lemma.

## Correction to the earlier pilot

The earlier local Prompt 3 output suggested the possible obstruction

```text
S_u(r) = {v,a,b,c},
S_u(s) = {v,d,e,f},
r != s.
```

This obstruction is impossible. If v belongs to both cohorts centered at u, then

```text
r = |p_v-p_u| = s.
```

So the two radii are not distinct.
