# Prompt 3b: fragile-cover repair audit

This is a focused follow-up to the minimal-counterexample fragility prompt.
Work self-contained. Do not search the internet.

Let P be a strictly convex n-gon. For a vertex u, let

```text
m_u(P) = max_r #{w != u : |p_w-p_u| = r}.
```

Call P bad if m_u(P) >= 4 for every vertex u. Call P minimal bad if P is bad
but deleting any vertex gives a polygon that is not bad.

For a fixed deleted vertex v, minimality gives a remaining center u such that
m_u(P-v) <= 3. Since P is bad, u has at least one rich radius in P.

Question. Prove or disprove the following stronger conclusion:

```text
u is fragile: m_u(P)=4 and there is a unique radius r_u whose cohort has size
exactly four. Moreover v belongs to this unique four-cohort.
```

The apparent obstruction is that u might have multiple rich radii in P, all
reduced below 4 after deleting v. Check this scenario carefully. In particular,
track the fact that a fixed vertex v has only one distance from the fixed center
u.

Output:

1. A rigorous proof of the fragile-cover lemma, or the exact first fatal gap.
2. If the proof succeeds, state precisely where minimality is used.
3. If the proof succeeds, restate the hypergraph consequences available for the
   second stage.
