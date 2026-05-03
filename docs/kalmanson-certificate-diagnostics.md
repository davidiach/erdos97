# Kalmanson Certificate Diagnostics

Status: `EXACT_CERTIFICATE_DIAGNOSTIC`.

This note records a deterministic support diagnostic for the checked
fixed-order Kalmanson/Farkas certificates. It does not add a general proof, a
counterexample, or an all-order obstruction for `C13_sidon_1_2_4_10` or
`C19_skew`.

## Artifact

```text
reports/kalmanson_certificate_diagnostics.json
```

Regenerate it with:

```bash
python scripts/analyze_kalmanson_certificates.py \
  --assert-expected \
  --out reports/kalmanson_certificate_diagnostics.json
```

Use `.venv/bin/python` in the current local checkout if the system `python`
does not have the repository dependencies installed.

## What the Script Checks

For each default certificate, the script first invokes the exact
Kalmanson/Farkas checker. It then reconstructs the integer inequality vectors
after quotienting ordinary distance variables by the selected-distance
equalities.

The report records:

- inequality counts by Kalmanson kind;
- exact weight statistics;
- support rank and nullity over three prime fields;
- cyclic gap patterns of supporting quadrilaterals;
- selected-distance class size histograms;
- the largest distance-class cancellations in the zero weighted sum.

The checked default certificates are:

| Pattern | Certificate | Inequalities | Distance classes | Fixed-order status |
|---|---|---:|---:|---|
| `C13_sidon_1_2_4_10` | `data/certificates/c13_sidon_order_survivor_kalmanson_unsat.json` | 34 | 39 | `EXACT_OBSTRUCTION` |
| `C19_skew` | `data/certificates/round2/c19_kalmanson_known_order_unsat.json` | 94 | 114 | `EXACT_OBSTRUCTION` |

For both supports, the rank over each checked prime field is one less than the
number of supporting inequalities, so the current support dependency is
one-dimensional over those fields. This is a structure diagnostic only: it
does not prove that no smaller support exists, and it does not say anything
about cyclic orders not encoded in the certificate.

## Interpretation

Safe claim:

```text
The report reproducibly summarizes the support structure of already checked
fixed-order Kalmanson/Farkas certificates.
```

Unsafe claim:

```text
The report kills all cyclic orders of C13_sidon_1_2_4_10 or C19_skew.
```

The next exact step is to use this kind of support data to guide a bounded C13
cyclic-order search, with every closed branch backed by its own checked
positive-integer certificate.
