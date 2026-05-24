# C19 Order-CNF Proof Tooling Probe

Status: `TOOLING_BLOCKER_DIAGNOSTIC`.

This note records the local tooling state for turning the checked
`C19_skew` order-CNF export into a solver-independent proof replay. It is an
environment and workflow note only. It does not add a mathematical
obstruction, does not prove Erdos Problem #97, and does not claim a
counterexample.

## Scope

The relevant checked inputs are:

- `data/certificates/c19_skew_all_orders_kalmanson_z3.json`
- `reports/c19_kalmanson_order_cnf_summary.json`
- `scripts/export_c19_kalmanson_order_cnf.py`

The exporter can write and byte-check the DIMACS target:

```bash
python scripts/export_c19_kalmanson_order_cnf.py \
  --write-cnf reports/c19_kalmanson_order.cnf

python scripts/export_c19_kalmanson_order_cnf.py \
  --check-cnf reports/c19_kalmanson_order.cnf
```

The generated CNF is only a proof target. A solver-independent claim still
requires a checked proof object such as DRAT, LRAT, or an equivalent finite
replay certificate.

## Local Tooling Probe

The reusable local probe is:

```bash
python scripts/probe_c19_proof_tooling.py --json
```

It reports executable availability, Python module availability, and whether
the local environment has at least one supported SAT solver plus one supported
proof checker for a solver-independent C19 CNF replay. This is still an
environment diagnostic only.

The local Windows checkout currently has no command-line SAT proof toolchain
available on `PATH` for this step:

```text
where.exe kissat     -> not found
where.exe cadical    -> not found
where.exe drat-trim  -> not found
where.exe lrat-check -> not found
```

The Python package probe found:

```text
pysat False
z3 True
```

Thus the current local environment can replay the stored Z3 certificate, but
it cannot yet generate and independently check a DRAT/LRAT proof for the
exported CNF.

## Next Step

The next reproducible proof-tooling increment should add one of:

- a checked external SAT proof workflow, for example a pinned `kissat` or
  `cadical` command plus a pinned DRAT/LRAT checker;
- a checked proof artifact for `reports/c19_kalmanson_order.cnf`, with the CNF
  regenerated and byte-checked before proof validation;
- a pure finite-order proof checker for the stored forbidden clauses that does
  not call Z3.

Until one of those exists, the C19 all-order obstruction remains a checked Z3
certificate with a standard CNF replay target, not a solver-independent proof.
