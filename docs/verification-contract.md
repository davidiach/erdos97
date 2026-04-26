# Verification Contract

This repository treats numerical candidates as evidence, not as proofs.

## Numerical Candidate Requirements

A numerical candidate is not accepted unless it includes:

- `n`;
- coordinates;
- selected 4-sets `S_i`;
- independent verifier output;
- max selected-distance spread;
- RMS equality residual;
- convexity margin;
- minimum edge length;
- minimum pair distance;
- optimizer and seed;
- exactification plan.

Allowed numerical statuses:

- `failed`;
- `near-miss only`;
- `needs independent verification`;
- `exactification candidate`;
- `certified`.

The status `certified` must not be used for a floating-point-only artifact.

## Certified Counterexample Requirements

A certified counterexample must include:

- exact coordinates or an exact algebraic parameterization;
- exact verification that every selected 4-set has equal squared distance from
  its center;
- exact verification of strict convexity;
- a reproducible script that checks the certificate independently;
- a written explanation of the selected incidence pattern.

## Lemma Requirements

A lemma entry should include:

- formal statement;
- hypotheses;
- full proof;
- known counterexample attempts;
- whether it survives known 3-neighbor examples;
- consequence for search or exactification.

## Failed Approach Requirements

A failed approach entry should include:

- claim attempted;
- why it seemed plausible;
- counterexample or failure mode;
- whether a weaker version survives;
- current status.
