# Prompt 3b local summary, 2026-04-28

Status: research artifact only. This is not an independent API batch run and
does not prove the global Erdos #97 statement.

## Main result

The fragile-cover lemma is valid. The earlier local Prompt 3 pilot incorrectly
identified a "multi-rich through v" obstruction. That obstruction is impossible:
if two rich cohorts centered at the same u both contain the same deleted vertex
v, then their radii both equal |p_v-p_u|, so they are the same radius.

## Exact lemma proved

In a minimal bad polygon, every vertex v is contained in the unique four-cohort
of at least one fragile center u.

Minimality is used exactly once: after deleting v, choose a remaining center u
with m_u(P-v) <= 3. Comparing every rich radius of u in P with the same radius
in P-v forces each rich radius to have exact size 4 and to contain v. Since v
has only one distance from u, there is only one rich radius.

## Consequence

The minimal-counterexample route is alive again. A minimal bad polygon gives a
covering pointed 4-uniform hypergraph of fragile cohorts satisfying:

- self-exclusion;
- cover;
- pairwise intersection at most two;
- the convex-position crossing rule for two-row overlaps.

The next meaningful task is not to repair fragile-cover, but to exploit the
second-stage hypergraph plus the deletion-critical witness map.
