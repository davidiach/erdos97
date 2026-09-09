# Provenance and claim boundary

The connected GitHub branch lookup in this turn resolved `main` to
`047d05149382e48b602b292df4b8fc9e2da560bb`. The inspected repository has not advanced beyond
merged PR #942. No GitHub branch, file, PR, or accepted claim was changed.

The uploaded previous research packet is preserved byte-for-byte as
`inputs/previous_packet.zip`, SHA256:

```
bd71f647f395a42ecf704e9ae6b750ed5cdbfb35b2e125ba3af0744e7d76b240
```

The primary field implementation and its simple real quadratic extension
were copied unchanged to `prior_math/`. Their hashes are in `provenance.json`.
They remain inherited code, not a new independent implementation. The
84-triple circumcenter ceiling and its certificate also come from that
packet. Both new checkers replay it; the full replay extracts and runs the
old verifiers and 31 tests in a temporary directory without changing inputs.

The new mathematical contribution is the unrestricted-in-cap-size slot
reduction and the classification of caps whose every vertex has a rich
radius using two old witnesses. The next recurrence triangle itself is old.
The core reduction, concentricity argument, and identification of the unique
admissible quadratic root are written in `proofs.md`.

The new oracle was written in this same session. It is independent of the
primary implementation in its arithmetic representation, slot construction,
polynomial coefficient recovery, and graph deletion order. It is not
external independent mathematical review. No Lean proof is provided.

The one-free-vertex script is an exact but coarse exploratory relaxation;
it is not checked by the new independent oracle and has no geometric
feasibility or infeasibility conclusion.

Repository-wide `make verify-fast`, `make verify-artifacts`, and
`make verify-lean` were not run. This is a standalone packet, not a changed
repository checkout, and packet validation must not be described as those
repository-wide gates. No status metadata or accepted finite bound changed.

The official external problem page was not successfully refreshed in this
turn (the web fetch returned HTTP 403). No claim about a newly verified
public global status is made. This packet itself contains neither an
unrestricted solution nor a counterexample.
