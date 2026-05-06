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

## C19 Compact vs Legacy Diagnostic

The C19 fixed-order certificate now has a compact two-inequality artifact:

```text
data/certificates/round2/c19_kalmanson_known_order_two_unsat.json
```

The earlier 94-inequality artifact is retained as provenance:

```text
data/certificates/round2/c19_kalmanson_known_order_unsat.json
```

Regenerate their comparison report with:

```bash
python scripts/analyze_kalmanson_certificates.py \
  --c19-compact-vs-legacy \
  --assert-expected \
  --out reports/c19_kalmanson_compact_vs_legacy.json
```

The report verifies both inputs as exact fixed-order certificates before
comparing them. It records that both certificates use the same `C19_skew`
selected-witness pattern, the same cyclic order, and the same 114
selected-distance quotient classes. The compact certificate has 2 inequalities,
weight sum 2, and max weight 1; the legacy artifact has 94 inequalities,
weight sum 6,283,316,065, and max weight 334,665,404.

The compact certificate support is not literally a subset of the legacy
support, and this report does not derive one certificate from the other. It is
only a fixed-order support diagnostic. The separate all-order `C19_skew` Z3
artifact remains separate, and no global Erdos Problem #97 status changes here.

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
