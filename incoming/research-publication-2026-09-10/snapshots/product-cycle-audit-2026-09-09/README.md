# Erdős #97: product-cycle audit and overlapping-diamond phase obstruction

Research continuation, 9 September 2026.

**REVIEW-PENDING RESTRICTED MATHEMATICS. No unrestricted proof or counterexample,
no exhaustive nine-orbit exclusion, no accepted-status promotion, and no
independent external mathematical review.**

This packet contains a new gain-labelled phase obstruction derived from the
existing circle-completion identity, exact certificates and positive relaxation
controls, two new geometric constructions, and bounded construction searches.
All four exactly checked geometric examples still have good vertices.

## Principal result

For a gain-aligned own-side C3 diamond, circle completion and strict convexity
force a multiplicative identity. Choosing representatives in one strict
120-degree sector gives an exact phase equality with the rotational gain
retained. Two overlapping diamonds in three stored nine-orbit systems imply

```
z0*z6 = z1*z2
z2*z3 = omega^2*z6*z8
```

and hence `z0*z3 = omega^2*z1*z8`. Their sector order `0<1<3<8` makes this
impossible. Only seven arrows are needed. The proof is local and works at any
number of orbits when those hypotheses hold; it does not force those hypotheses
from an arbitrary all-rich polygon.

Read [the complete proof](proof_attempts/diamond_phase.md). The circle-completion
identity itself is credited to #942 rather than claimed as new.

These three systems have exact positive rational vectors for the preceding
full chord-angle relaxation and, separately, for the ordinary-distance cone
with all strict triangle and Kalmanson inequalities and the specified radius
orders. They are not geometric realizations. Their exact rejection by the
phase identity exposes a real missing constraint in the older search models.

## Exact evidence and scope

| Item | Result | Scope |
|---|---|---|
| Stored fixed systems | 333 independently replayed exact rejections: 330 base-angle, three diamond-phase | The stored systems in their stated sector order, not every nine-orbit system |
| Additional short phase certificates | 200 of those same 333 have one/two-diamond certificates (five single, 195 double) | Overlapping evidence, not 200 additional systems |
| Positive angle/distance controls | Three separate rational angle vectors and three rational distance vectors, all exactly checked | Necessary relaxations, not joint Euclidean coordinates |
| Supplier-arc lemma | Two specified arrows force strict radial lifting for every intervening orbit; a three-arrow corollary is impossible | All-size C3 own-side geometry with the stated sector order |
| Exact six-cycle | Upper-half-plane multipliers have product omega; six of 18 points on the hull and 12 strictly interior; all maxima exactly three | Exact nonconvex control, not a counterexample |
| Exact maximum-root neighborhood | Strictly convex 21 points; nine rich and 12 good; every root witness rich and no larger actual rich radius | Refutes a local C3 extremal-selection shortcut, not global all-rich descent |
| Convex positive controls | Two 12-point controls, 120 supporting inequalities each | Calibrate supplier lifting and show that a single product diamond is allowed |
| Abstract no-diamond graph | 60 states, outdegree two, no reciprocal pair, no directed diamond | Incidence only, no convex order or Euclidean realization |

See [claims.json](claims.json) for hypotheses, evidence levels, dependencies,
source commits, and verification commands. See [frontier.md](frontier.md) for
the exact missing implications and [research_log.md](research_log.md) for the
adaptive search record, timeouts, failures, and changes of hypotheses.

## Replay

Python 3.10+ and its standard library suffice for all exact replays and tests:

```sh
python -S replay.py --output /tmp/erdos97-product-cycle-replay.json
python -S package.py --check
```

The consolidated replay executes eleven command groups in a temporary copy,
checks all 333 certificates, the positive relaxations, all four geometric
controls, the abstract guardrail, and **50 distinct defensive tests** (38 full
packet plus 12 publication-core tests). It checks the immutable input bytes
before and after. It uses no optimizer or network. The packet core's additional
pytest run exercises the same 12 tests, not another 12 distinct tests.

[repro.md](repro.md) gives individual commands and optional discovery commands.
Do not use `-O`. The retained reports are under `reports/`; a report match alone
is not a substitute for replaying the geometric and arithmetic conditions.

## Bounded searches, not proofs of nonexistence

The improved nine-orbit searches add the supplier-arc relation and then an exact
one/two-diamond phase filter. The phase filter was checked against a separate
Python implementation on all 333 stored systems. A fresh 2,000,000-node guarded
run reached 15 terminal systems, all already exactly excluded in the corpus.
The 55,504 phase prunes are search diagnostics, not all-size coverage. A larger
run timed out before a final counter report; its zero saved complete rows do
not mean zero mathematical survivors.

Ninety coordinate attempts on the three positive-relaxation systems approached
coincidences and negative supporting margins. The later phase obstruction,
not the numerical failures, rules out their strictly convex realizations.
These are now intentionally obstructed benchmarks and must not be restarted
as live coordinate candidates.

The 7x7 and 9x9 integer-pool searches allowed arbitrary distance classes and
asymmetric subsets. Their solver infeasibility results are not exact finite
exclusion certificates. Grid membership remains a restrictive search domain.

## Repository publication

The mathematical core was published as **draft PR #944**:
`https://github.com/davidiach/erdos97/pull/944`.

- Base: `9b8b8f807ae8b21f10780a7d11f6c5cec65f26e7` (merged #943).
- Initial publication: `de2ce5a5e6a391103fa011b9697533d002ce8f00`.
- CI repair head: `832fe620583488b5c4a1169c75b486b2debf4bad`.
- Branch: `research/diamond-phase-obstruction-2026-09-09`.

The PR contains the five files mirrored in `publication_core/`, plus the required
navigation-only update to `incoming/README.md`. It does **not** contain this
entire broader archive. The initial five-file byte comparison is retained as
historical evidence; the verifier's subsequent local-variable rename is recorded
separately. No main ref, accepted mathematical status, existing certificate,
root workflow, secret, or permission was changed. No merge was requested.

Initial hosted CI identified two publication issues: Ruff E741 for the local
name `l`, and the missing incoming-index link. The repair changes that variable
to `tip` and adds the link/table count, without changing certificate logic.
It does not weaken or skip checks. See `reports/publication.json` for the
latest actually observed hosted-check state; no unobserved pass is inferred.

Repository-wide `make verify-fast`, `make verify-artifacts`, Ruff, and Python
3.10/3.11 compatibility collection were not run locally: this is a scoped
export rather than a complete checkout, and those local tools/interpreters
are absent. Hosted checks are recorded separately. No Lean source changed.
Mathematical expert review remains outstanding regardless of CI.

## Provenance

The five available earlier inputs under `inputs/` are immutable byte copies of
attachments. Their hashes and pinned repository reading anchors are listed in
[provenance.json](provenance.json). This is not a complete historical repository
snapshot. Search/verification modules described as adaptations are not falsely
labelled byte-identical imports. The older circumcenter attachment was only an
empty output list and is not promoted to a new exact enumeration in this packet.

The manifest covers every retained file except itself and disposable Python/test
caches. It is an integrity check, not a mathematical theorem. The archive is
read back and compared byte-for-byte by `package.py`.
