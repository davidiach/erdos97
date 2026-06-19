# Quarter-cell derivative certificate for the three-orbit `C_m` family

Trust label: `REPO_LOCAL_INTERVAL_DERIVATIVE_CERTIFICATE`.

This note is a drop-in follow-up to the repo notes
`docs/quarter-cell-closure.md` and
`docs/quarter-cell-signed-band-preflight.md`.  It closes the named
quarter-cell subcases for

```text
m = 8, 12, 16
```

in the repo-local interval-arithmetic sense, subject to the usual trust in the
checker.  It does **not** prove Erdos Problem #97, does **not** give a
counterexample, and does **not** settle arbitrary three-orbit `m`, non-cyclic
families, partial orbits, or the non-quarter cells whose current repo status is
still screen-grade unless independently hardened.

## Setup

Use the notation of the existing quarter-cell notes.  Let

```text
T = 2*pi/m,        P(r) = (r^2 - 1)/(2r),
A_k = exp(ikT),    B_k = y exp(i(beta + kT)),
C_k = z exp(i(gamma + kT)).
```

The A-row reduction says that the remaining quarter-cell witness locus is
confined to boundary bands.  In each cell write

```text
P(y) = +/- sin(d),       P(z) = +/- sin(e),       0 <= d,e <= delta_m,
delta_m = asin(P(sec(pi/m))).
```

The three band orders are

```text
LL: beta=d,     gamma=e,     0 < d < e,
LH: beta=d,     gamma=T-e,   d,e>0 and d+e<T,
HH: beta=T-d,   gamma=T-e,   0 < e < d.
```

For a positive radius satisfying `P(r)=s sin(u)`, the checker uses the explicit
root

```text
r_s(u) = s sin(u) + sqrt(1 + sin(u)^2),       s in {+1,-1}.
```

## Turns

The angular-order polygon is

```text
..., C_{-1}, A_0, B_0, C_0, A_1, B_1, C_1, ...
```

and strict convexity requires all three per-period turns to be positive.
The checker uses

```text
tau_A = orient(C_0, A_1, B_1)
tau_B = orient(A_0, B_0, C_0)
tau_C = orient(B_0, C_0, A_1)
```

These correspond to killer turns `1,2,3`, respectively, in
`quarter-cell-signed-band-preflight.md`.

For polar points `(r_i, theta_i)`, the orientation identity is

```text
orient(1,2,3)
  = r1*r2*sin(theta2-theta1)
  + r2*r3*sin(theta3-theta2)
  + r3*r1*sin(theta1-theta3).
```

Thus the checker evaluates

```text
tau_B = y*sin(beta) + y*z*sin(gamma-beta) - z*sin(gamma)
tau_C = y*z*sin(gamma-beta) + z*sin(T-gamma) - y*sin(T-beta)
tau_A = z*sin(T-gamma) + y*sin(beta) - y*z*sin(T+beta-gamma)
```

with interval arithmetic.

## New monotonicity certificate

The preflight note recorded a fixed killer turn for each of the 12 signed cells
and observed a negative leading boundary term.  The new observation is that for
`m = 8, 12, 16`, each fixed killer turn is not merely locally negative near the
degenerate boundary: a simple derivative sign holds on the entire square

```text
0 <= d,e <= upper(delta_m),
```

which contains each open cell after imposing its order inequalities.

The derivative signs are:

| cell | killer turn | certified derivative sign | boundary identity used |
| --- | --- | --- | --- |
| `LL_y+_z+` | `tau_A` | `d/d d < 0` | `F(0,e)=0` |
| `LL_y+_z-` | `tau_A` | `d/d d < 0` | `F(0,e)=0` |
| `LL_y-_z+` | `tau_B` | `F_de < 0` | `F(d,0)=F(0,e)=0` |
| `LL_y-_z-` | `tau_C` | `d/d e < 0` | `F(d,d)=0`, integrate over `e>d` |
| `LH_y+_z+` | `tau_A` | `F_de < 0` | `F(d,0)=F(0,e)=0` |
| `LH_y+_z-` | `tau_C` | `d/d e < 0` | `F(d,0)=0` |
| `LH_y-_z+` | `tau_B` | `d/d d < 0` | `F(0,e)=0` |
| `LH_y-_z-` | `tau_B` | `d/d d < 0` | `F(0,e)=0` |
| `HH_y+_z+` | `tau_A` | `d/d e < 0` | `F(d,0)=0` |
| `HH_y+_z-` | `tau_C` | `F_de < 0` | `F(d,0)=F(0,e)=0` |
| `HH_y-_z+` | `tau_A` | `d/d e < 0` | `F(d,0)=0` |
| `HH_y-_z-` | `tau_B` | `d/d e > 0` | `F(d,d)=0`, integrate backward over `e<d` |

Every row gives `F<0` in the strict cell.  Therefore every strict cell has a
non-positive per-period turn, contradicting strict convexity.

## Interval trust boundary

The checker uses `mpmath.iv` interval arithmetic for the turn expressions and
their first/mixed derivatives. The interval context has `sin`, `cos`, and
`sqrt`, but not `asin`; for

```text
delta_m = asin(P(sec(pi/m)))
```

the checker computes a high-precision scalar center and pads it by a
precision-relative interval. The certified derivative intervals have margins
far larger than that padding for `m = 8, 12, 16`, but this is still a
repo-local machine interval certificate rather than a proof-assistant theorem.

## Reproduce

Check the checked-in artifact:

```bash
python scripts/check_quarter_cell_derivative_certificate.py --check --assert-expected --json
```

Regenerate it with:

```bash
python scripts/check_quarter_cell_derivative_certificate.py \
  --m-values 8,12,16 \
  --assert-expected \
  --write data/certificates/quarter_cell_derivative_certificate.json
```

The generated JSON records 36 derivative interval enclosures: 12 signed cells
for each of `m=8,12,16`.  In the included run, all 36 cells certify.

## Non-claims

- This is not a global proof of Erdos Problem #97.
- This is not a counterexample.
- This only addresses the A-row-reduced quarter-cell witness locus for
  `m = 8, 12, 16` in the three-orbit `C_m` family.
- It does not upgrade unrelated screen-grade branches to exact certificates.
- It is an interval-arithmetic certificate, not a Lean/formal proof-assistant
  certificate.
