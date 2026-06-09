# Bootstrap/T12 full-row anti-activation negative control

Status: `EXACT_NEGATIVE_CONTROL` / `PROVENANCE`. No general proof of Erdos
Problem #97 is claimed. No counterexample is claimed.

This note isolates the full selected-row anti-activation control that is also
summarized in `docs/closure-activation-negative-controls.md`. Its purpose is
to block one overstrong bridge move:

```text
closure exposure of center 7 with witnesses 0,1,4
    => selected row 7 -> {0,1,4,6} is forced.
```

The checked artifact is:

```text
data/certificates/bootstrap_t12_anti_activation_negative_control.json
```

Run the checker with:

```bash
python scripts/check_bootstrap_t12_anti_activation_negative_control.py --check --assert-expected --json
```

Regenerate the artifact after an intentional source change with:

```bash
python scripts/check_bootstrap_t12_anti_activation_negative_control.py --write
```

## Control

The control is a full abstract selected-row incidence system on cyclic order
`0,1,2,3,4,5,6,7,8,9`.

Starting from seed `{0,1,4}`, rich-triple closure adds center `7` and then
stops:

```text
cl({0,1,4}) = {0,1,4,7}
```

The activated row at center `7` is:

```text
7 -> {0,1,3,4}
```

It contains the three core witnesses `{0,1,4}`, but its fourth witness is `3`,
not the target private witness `6`. Thus the target row
`7 -> {0,1,4,6}` is not active at the target center.

## Checked Conditions

The checker verifies:

- every row has four distinct witnesses;
- no row contains its own center;
- every vertex appears in at least one selected row;
- all row-pair intersections have size at most two;
- every two-overlap pair satisfies the supplied cyclic crossing check;
- adjacent selected rows intersect in at most one witness;
- the closure and anti-activation row match the stored certificate.

Current compact summary:

| Quantity | Value |
|---|---:|
| closure result | `{0,1,4,7}` |
| activated row at center `7` | `{0,1,3,4}` |
| target row active at center `7` | `false` |
| two-overlap row pairs | `18` |

## Bridge Lesson

This control shows that even a full selected-row incidence system can expose a
center through the desired three core witnesses while switching the fourth
witness. A future bootstrap/T12 bridge lemma therefore needs an additional
condition that pins the fourth witness, such as activation provenance,
critical-row uniqueness, radius ordering, or an all-fourth obstruction check.

## Nonclaims

This is not a Euclidean realization certificate, not a counterexample, not a
proof that closure activation fails for genuine minimal counterexamples, and
not a check against all vertex-circle, Kalmanson, row-Ptolemy, or algebraic
obstruction templates.
