# Codex-local pilot summary, 2026-04-28

Status: research artifact only. This is not a fresh-chat API batch and not a
GPT-5.5 Pro reproducibility run.

## Prompt 0

No proof or counterexample was obtained. The strongest useful output is a
self-contained reduction: any bad polygon yields a pointed selected-cohort
system satisfying self-exclusion, pairwise intersection at most two, and the
two-shared-cohort crossing rule. A local five-point convex fan shows that one
vertex can have four equidistant vertices, so any proof must be global.

## Prompt 1

The convex-position crossing lemma was proved in detail. The run derives useful
two-row consequences: adjacent centers cannot share two cohort vertices,
adjacent cohort vertices cannot be a shared pair for two rows, and any unordered
cohort-pair appears in at most two rows. The resulting pair-count inequality
rules out the selected-row axioms for n <= 7 and forces a very rigid extremal
profile at n = 8, but it does not prove the full problem.

## Prompt 2

No rank-rigidity proof was obtained. The useful reformulation is that an
extra kernel vector is exactly an exotic lifting h_j for which every selected
four-cohort is coplanar in the lifted point set (x_j,y_j,h_j). This identifies
the missing certificate as an affine-circuit rigidity check for the selected
four-uniform support pattern. The prompt's stated rank lemma needs additional
coverage/connectivity hypotheses before it can plausibly be true for arbitrary
chosen four-cohorts.

## Prompt 3

The fragile-cover lemma was not proved. Minimality gives a weaker but exact
lemma: for every deleted vertex v, there is some remaining center u such that
every rich radius of u in the original polygon contains v and has exact size
four. This does not imply u is fragile, because u may have two or more distinct
four-cohorts, all containing v. That is the first fatal gap in the proposed
fragile-cover route.

Erratum, superseded by `../codex_local_prompt3b_2026-04-28/summary.md`: the
last sentence is wrong. A fixed vertex v has only one distance from a fixed
center u, so two distinct radii centered at u cannot both contain v. The
fragile-cover lemma is valid.

## Recommended next action

Use Prompt 3's weaker deletion lemma to rewrite the fragility path. The next
prompt should ask whether the "multi-fragile through v" scenario can be ruled
out geometrically, or whether it produces a concrete obstruction pattern for
the finite-case enumerator.
