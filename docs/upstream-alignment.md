# Upstream alignment with `teorth/erdosproblems`

## Purpose

This repository is a deep, single-problem reproducibility workspace for Erdos
Problem #97. It is not a replacement for the public Erdos problem database.

## Official/global status

- Official page: <https://www.erdosproblems.com/97>
- Status: falsifiable/open
- Status checked: 2026-04-30
- Page last edited: 2025-10-27
- Comment solution claims: none partial or complete
- Prize: $100
- Tags: geometry, distances, convex
- Formalised statement: yes, but not a formal proof

## Formalization note

The Google DeepMind Formal Conjectures entry
`FormalConjectures/ErdosProblems/97.lean` is useful for statement alignment:
it encodes the variable-radius `HasNEquidistantProperty 4` statement and marks
`erdos_97` as `research open`. The theorem body uses `sorry`, and the nearby
Danzer and Fishburn--Reeds `k=3` variants also use `sorry`; do not cite those
Lean entries as proof certificates.

## Local repository status

- No general proof and no counterexample are claimed.
- Strongest local result: selected-witness finite-case obstruction rules out
  `n <= 8` in a repo-local, machine-checked sense.
- External review is recommended before public theorem-style claims.

## What should go upstream

Appropriate upstream contributions:

- corrections to metadata fields in `teorth/erdosproblems/data/problems.yaml`;
- relevant OEIS links, once independently verified;
- formalization status notes, if accepted by upstream conventions;
- short comments or links when they add clear value.

Usually not appropriate as an upstream PR:

- long proof sketches;
- raw search logs;
- numerical near-misses;
- claims that require substantial mathematical review.

Mathematical discussion should normally go on the official #97 page or in a
clearly scoped issue.

## Conservative problem-page comment template

> I have started a reproducibility workspace for Erdos Problem #97:
> `https://github.com/davidiach/erdos97`.
> It claims no general proof and no counterexample.
> The current strongest artifact is a repo-local machine-checked finite-case
> obstruction ruling out selected-witness counterexamples for `n <= 8`, with
> exact obstruction scripts for the surviving `n=8` incidence classes.
> Independent review is especially welcome for the `n=8`
> incidence-completeness checker and exact certificates.

## Do not overclaim

Do not describe this repo as solving #97 unless a complete proof or
counterexample has been independently checked and the official/global status is
updated accordingly.
