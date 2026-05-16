# Radius-blocker vertex-circle pilot

Status: `REVIEW_PENDING_DIAGNOSTIC` / bridge diagnostic. No general proof of
Erdos Problem #97 is claimed. No counterexample is claimed.

This note records a first exact-four-row pilot for the bridge direction

```text
minimal fragile cover + full badness + radius-blocker
    => vertex-circle self-edge or strict cycle.
```

It does not prove that implication. It supplies replayable tooling for finite
packets where each center has one or more exact four-rich row options, a
candidate radius-blocker subset, and a supplied cyclic order.

## What the checker does

The core module is `src/erdos97/radius_blocker_packets.py`. For a packet of
exact four-row options it checks:

- the supplied subset is a radius-blocker for the listed rich classes;
- selected row choices satisfy the row-pair cap and the two-overlap crossing
  rule in the supplied cyclic order;
- selected witness-pairs occur in at most two rows;
- selected indegrees satisfy the standard pair-cap upper bound;
- each incidence survivor is replayed through the selected-distance quotient
  and vertex-circle strict-edge check.

The checker intentionally rejects rich classes of size greater than four for
now. A larger rich class carries equality information for all vertices in that
class, not only for a chosen four-subset, so it needs a separate replay
semantics before it can be used soundly.

## Pilot artifact

The checked artifact is:

```text
data/certificates/radius_blocker_vertex_circle_pilot.json
```

Regenerate and verify it with:

```bash
python scripts/check_radius_blocker_vertex_circle_pilot.py --check --assert-expected
```

The current pilot covers three fixed exact-four row packets:

| Packet | blocker | incidence survivors | vertex-circle result |
| --- | --- | ---: | --- |
| `C13_sidon_fixed_rows_natural_order` | `[0,1,2,3]` | 1 | strict cycle |
| `two_block_no_forward_fixed_rows` | `[0,1,2,5]` | 1 | self-edge |
| `block6_two_copy_full_extension_fixed_rows` | `[0,1,2,5]` | 1 | self-edge |

These are stress controls, not new live counterexample candidates. The C13
fixed pattern is already retired by the stronger all-order Kalmanson/Farkas
certificate. The two-block packets are abstract bridge controls and are not
Euclidean realization certificates.

## Research use

The useful next step is to replace the fixed-row pilot cases with true
multi-option blocker packets mined from stuck-set or fragile-cover searches.
The hoped-for output is a small local lemma of the form:

```text
If a minimal counterexample has this radius-blocker/fragile-cover shape,
then every exact four-row selection compatible with it forces a
vertex-circle quotient self-edge or strict cycle.
```

That would strengthen the adaptive blocker bridge. Until such a lemma is
proved and independently reviewed, this pilot remains a finite diagnostic only.
