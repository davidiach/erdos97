# Fragile-cycle halo endpoint-reuse negative control

Status: exact bounded one-row negative control. This note assumes the fixed
`23=27` core and its four retained critical rows. It does not force that core,
construct a full selected-row extension, certify a Euclidean realization,
prove `n=11`, `n=12`, or Erdos Problem #97, or give a counterexample.

## Question

The deletion-profile crosswalk finds 310,320 four/five-halo covers with one
retained-exclusive mutual pair. In a full rich-class system, that pair is
either broken by another T4 class containing an endpoint or remains globally
exclusive and receives a T5/T44 deletion certifier.

Can the currently isolated exact necessary conditions eliminate the first
branch and thereby force the richer profile?

## Candidate contract

For each triggered retained cover, the checker tries one additional selected
four-witness row whose center is outside the four retained centers and whose
row contains at least one exclusive-pair endpoint. It requires:

- self-exclusion;
- pairwise row intersection at most two;
- crossing of the center chord and common-witness chord at every two-overlap;
- witness-pair multiplicity at most two; and
- no strict self-edge or strict cycle in the natural-order vertex-circle
  quotient of the resulting five-row partial system.

Selected indegree is automatic here. Five partial rows can give indegree at
most five, below the cap six for `n=11` and seven for `n=12`.

For a deterministic compressed witness, the checker first tries center `2`
for pairs `{1,3}` and `{1,6}`, and center `0` for pair `{3,6}`. If that center
fails, it tries the remaining outside centers in cyclic order. Within one
center it selects the lexicographically first surviving four-set.

## Exact census

| Halos | Triggered covers | Vertex-circle-feasible reuse row | Preferred center | Alternate center | No survivor |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 144,000 | 144,000 | 136,043 | 7,957 | 0 |
| 5 | 166,320 | 166,320 | 165,012 | 1,308 | 0 |
| Total | 310,320 | 310,320 | 301,055 | 9,265 | 0 |

Every triggered retained cover therefore has a compatible one-row escape.
Because the extended five-row quotient is vertex-circle feasible, the retained
four-row subsystem is feasible as well.

## What this proves—and does not

This is a decisive negative control for the proposed short bridge. Retained
exclusivity, pair capacity, crossing, and the natural-order vertex-circle
quotient do **not** force the T5/T44 side of the deletion-profile dichotomy.

The surviving selected row is only a necessary combinatorial shadow of an
exact T4 rich class. The packet neither proves that such a rich class exists
nor extends the five rows to a full selected system. It therefore is not an
abstract full-extension example and not a Euclidean configuration.

The 731,700 pair-free covers from the source crosswalk are outside this
triggered-branch packet. They remain a separate deletion-coverage negative
control.

## Next bridge target

The large-halo route now needs information not present in this one-row layer:

```text
triggered covers:
    use exact rich-class type, simultaneous full extension, critical radii,
    or ordinary-distance geometry to eliminate endpoint reuse or exploit it;

pair-free covers:
    use full-extension or metric geometry beyond deletion coverage.
```

Repeating another independent candidate-row filter would not close either
branch unless it uses a genuinely stronger hypothesis.

## Replay

```bash
python scripts/check_fragile_cycle_halo_endpoint_reuse.py \
  --check --assert-expected --summary-json

python -m pytest -q tests/test_fragile_cycle_halo_endpoint_reuse.py
```

The generated artifact is
`data/certificates/fragile_cycle_halo_endpoint_reuse.json`; do not edit it
directly.
