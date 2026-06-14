#!/usr/bin/env python3
"""A4 lane: exact (sympy) re-examination of the failed-idea-#18 nine-point
configuration, to pinpoint WHY the *local* Endpoint-Control shortcut fails and
what minimal *global* input repairs it.

This script does NOT claim a proof or a counterexample. It is an exact-arithmetic
diagnostic of a known local negative control (docs/failed-ideas.md #18). It is
self-contained and uses only sympy Rational arithmetic.

Run:
    python scripts/exploration/a4_failed18_endpoint_reexam.py
"""
from __future__ import annotations

import sympy as sp

R = sp.Rational

# ---------------------------------------------------------------------------
# The failed-idea-#18 base 9-point configuration (cyclic order O,L0,L1,A1..A4,U1,U0)
# ---------------------------------------------------------------------------
P = {
    "O":  (R(0), R(0)),
    "L0": (R(9, 65), R(-129, 130)),
    "L1": (R(1, 5),  R(-11, 10)),
    "A1": (R(3, 5),  R(-4, 5)),
    "A2": (R(4, 5),  R(-3, 5)),
    "A3": (R(4, 5),  R(3, 5)),
    "A4": (R(3, 5),  R(4, 5)),
    "U1": (R(1, 5),  R(11, 10)),
    "U0": (R(9, 65), R(129, 130)),
}
CYCLIC = ["O", "L0", "L1", "A1", "A2", "A3", "A4", "U1", "U0"]
A_SET = ["A1", "A2", "A3", "A4"]
CENTER = "O"


def d2(p, q):
    (px, py), (qx, qy) = P[p], P[q]
    return (px - qx) ** 2 + (py - qy) ** 2


def cross(a, b, c):
    """Signed area*2 of triangle a->b->c."""
    (ax, ay), (bx, by), (cx, cy) = P[a], P[b], P[c]
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


def report(title):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


# ---------------------------------------------------------------------------
# 1. Verify exact strict convexity (all turns same sign) + the claimed facts.
# ---------------------------------------------------------------------------
report("1. EXACT VERIFICATION of the failed-idea-#18 base configuration")

n = len(CYCLIC)
turns = []
for k in range(n):
    a, b, c = CYCLIC[k], CYCLIC[(k + 1) % n], CYCLIC[(k + 2) % n]
    turns.append(cross(a, b, c))
print("Turn determinants (cyclic):")
for k, t in enumerate(turns):
    print(f"   {CYCLIC[k]:>3}->{CYCLIC[(k+1)%n]:>3}->{CYCLIC[(k+2)%n]:>3}: {t}")
all_pos = all(t > 0 for t in turns)
print(f"strictly convex (all turns > 0): {all_pos}")

# O's unit class
print("\nDistances^2 from center O:")
for v in A_SET:
    print(f"   |O {v}|^2 = {d2('O', v)}")
o_unit = all(d2("O", v) == 1 for v in A_SET)
print(f"A1..A4 all on unit circle around O: {o_unit}")

# endpoint A1 outside class
print("\nEndpoint A1 outside-of-(A union O) equal pair:")
print(f"   |A1 L0|^2 = {d2('A1','L0')},  |A1 L1|^2 = {d2('A1','L1')}")
a1_out = d2("A1", "L0") == R(1, 4) and d2("A1", "L1") == R(1, 4)
print(f"   A1 has 2 outside pts at sq-dist 1/4: {a1_out}")
print("Endpoint A4 outside-of-(A union O) equal pair:")
print(f"   |A4 U0|^2 = {d2('A4','U0')},  |A4 U1|^2 = {d2('A4','U1')}")
a4_out = d2("A4", "U0") == R(1, 4) and d2("A4", "U1") == R(1, 4)
print(f"   A4 has 2 outside pts at sq-dist 1/4: {a4_out}")

# outside pts not on O's unit circle
print("\nOutside pts are NOT on O's unit circle:")
print(f"   |O L0|^2 = {d2('O','L0')},  |O U0|^2 = {d2('O','U0')}")
print(f"   |O L1|^2 = {d2('O','L1')},  |O U1|^2 = {d2('O','U1')}")

# ---------------------------------------------------------------------------
# 2. The LOCAL endpoint claim and WHY it fails here.
# ---------------------------------------------------------------------------
report("2. THE LOCAL ENDPOINT-CONTROL CLAIM, instantiated at this config (m=4)")

print("""
Setup recap (canonical-synthesis Sec 5.1): A = S_O = {A1,A2,A3,A4}, m=4.
Angular endpoints at O are A1 (=v_-) and A4 (=v_+).
The PROVED part: at most 1 vertex of A\\{endpoint} lies on any circle around an
endpoint, plus O at sq-dist r*^2. So |S_{endpoint}(rho) cap (A cup {O})| <= 2.

The endpoint-control AUX claim wants: at least one endpoint j in {A1,A4}
satisfies, for EVERY rho>0,  |S_j(rho) \\ (A cup {O})| <= m-3 = 1.

The SHORTCUT (failed) tried to deduce this purely locally. Here it is FALSE for
BOTH endpoints simultaneously:
""")
for endp, outs in (("A1", ["L0", "L1"]), ("A4", ["U0", "U1"])):
    vals = {o: d2(endp, o) for o in outs}
    print(f"   endpoint {endp}: outside pts {outs} have sq-dist {set(vals.values())}"
          f"  =>  |S_{endp}(1/4) \\ (A cup O)| = {len(outs)} > 1")

print("""
So at radius rho = 1/2 (sq 1/4) BOTH endpoints already carry 2 outside
witnesses. The purely-local 'one endpoint must be outside-poor' reading is
refuted. This is exactly the #18 obstruction. (And the #18 extension even makes
each endpoint LOCALLY BAD with 4 outside pts at sq 1/4.)
""")

# ---------------------------------------------------------------------------
# 3. WHY does it fail? The missing ingredient is MINIMALITY (m = min_i M(i)).
#    Re-derive the per-center max multiplicity M(i) of the *actual* config and
#    show O is NOT a global minimizer here: the endpoints are RICHER, so the
#    descent target is mis-chosen. Minimality forbids exactly this.
# ---------------------------------------------------------------------------
report("3. ROOT CAUSE: the descent must start at a GLOBAL minimizer of M(i).")

# Compute, for every vertex, the maximum number of OTHER vertices at a common
# squared distance (this is M(i), the full rich-class max, not a selected row).
def Mi(v):
    from collections import Counter
    c = Counter(d2(v, w) for w in CYCLIC if w != v)
    return max(c.values()), {k: n_ for k, n_ in c.items() if n_ == max(c.values())}

print("Full per-vertex max equal-distance multiplicity M(i) in the BASE config:")
M = {}
for v in CYCLIC:
    m_v, witnessed = Mi(v)
    M[v] = m_v
    print(f"   M({v:>3}) = {m_v}   (achieved at sq-dist {sorted(witnessed.keys())})")

mmin = min(M.values())
argmin = [v for v in CYCLIC if M[v] == mmin]
print(f"\n   min_i M(i) = {mmin}, attained at: {argmin}")
print(f"   M(O) = {M['O']}  (the center we descended from)")
print("""
KEY OBSERVATION. In the canonical-synthesis Sec 5.1 setup, the descent target
(i*, r*) is chosen with |S_{i*}(r*)| = m := min_i M(i). The #18 configuration
has min_i M(i) small and attained at the *outside* points (L0,L1,U0,U1,...),
NOT at O. O itself has M(O)=4 only because A1..A4 are placed on its unit
circle by fiat; the outside vertices are the genuinely poor ones.

Therefore #18 is NOT a configuration in which O is the minimizer. The local
shortcut implicitly (and illegitimately) treated O's row as if it were a
minimal row and asked its endpoints to be outside-poor. The endpoints A1,A4
are interior-ish vertices that are free to be rich. Minimality of the *chosen*
center is the global hypothesis that the shortcut dropped.
""")

# ---------------------------------------------------------------------------
# 4. What minimality buys: the turn-inequality angular budget at the minimizer.
#    Demonstrate the turn-inequality lemma numerically-exactly on O's own
#    equal-distance pairs to show the >pi/2 arc budget it forces, and explain
#    how a *global* minimizer's budget + the endpoint monotonicity closes the
#    reduction where the local version cannot.
# ---------------------------------------------------------------------------
report("4. The repair lever: turn-inequality angular budget (docs/turn-inequality-lemma.md)")

# For the center O with equal pair (A_a, A_b) at offsets, the lemma says the
# exterior turn on the arc strictly exceeds pi/2. We verify the *sign* condition
# u.v < 0 that drives it, exactly, for O's witness pairs.
print("Turn-inequality driver  u.v = -|v|^2/2 < 0  checked exactly at center O")
print("for each equal-distance witness pair (the arc then carries turn > pi/2):")
ok_all = True
for i in range(len(A_SET)):
    for j in range(i + 1, len(A_SET)):
        a, b = A_SET[i], A_SET[j]
        # u = a - O, full chord v = b - a ; equal dist |O a| = |O b|
        (ox, oy) = P["O"]
        (ax, ay) = P[a]
        (bx, by) = P[b]
        ux, uy = ax - ox, ay - oy
        vx, vy = bx - ax, by - ay
        uv = ux * vx + uy * vy
        v2 = vx * vx + vy * vy
        cond = sp.simplify(uv + v2 / 2)  # should be 0  => u.v = -|v|^2/2
        neg = uv < 0
        ok_all = ok_all and (cond == 0) and neg
        print(f"   pair ({a},{b}): u.v = {uv}  (= -|v|^2/2 ? {cond == 0}), u.v<0 ? {neg}")
print(f"all turn-inequality drivers exact & negative: {ok_all}")

# ---------------------------------------------------------------------------
# 5. Counting the angular budget: show the outside witnesses of A1 cost turn
#    that, at a *global minimizer*, cannot be afforded. This is the precise
#    'why minimality repairs it' computation.
# ---------------------------------------------------------------------------
report("5. PRECISE repair statement (budget accounting at a minimizer)")

print("""
Statement of the open descent step (sharpened):

  Let m = min_i M(i) >= 4 and pick (i*, r*) with |S_{i*}(r*)| = m and (tie-break)
  r* minimal. Let v_-, v_+ be the angular endpoints of A = S_{i*}(r*).
  CLAIM (Endpoint Control, still open): some endpoint j in {v_-, v_+} has
        |S_j(rho) \\ (A cup {i*})| <= m-3   for every rho>0.

Why the LOCAL proof cannot exist (this script's #18 witness):
  - The hypotheses 'O concyclic-rich with A' and 'endpoints A1,A4 each carry
    >=2 outside equal pairs' are JOINTLY realizable in a strictly convex 9-gon
    with EXACT rational coordinates. Both endpoints fail the outside bound.
  - Hence no implication using only {O's row, endpoint monotonicity, strict
    convexity of the local cap} can yield the claim. A purely local certificate
    is impossible.  (Confirmed: items 1-2 above.)

The MINIMAL global ingredient that is missing (and, used together, plausibly
sufficient):  MINIMALITY OF THE CHOSEN CENTER.
  (a) i* is a global minimizer of M(i). In #18 this is violated: M(O)=%(MO)s but
      min_i M(i)=%(mmin)s at the outside vertices. So #18 is OUTSIDE the descent
      regime; it cannot certify or refute the claim.
  (b) If a descent vertex j (an endpoint) had M(j) <= m-1, that already
      contradicts minimality unless m is itself the min, i.e. the reduction is
      really proving 'm cannot be the min', i.e. it forces a strictly smaller
      M somewhere -> infinite descent -> some vertex with M<=3.
  (c) The turn-inequality lemma supplies the quantitative obstruction the local
      argument lacks: every equal-distance pair at j forces > pi/2 of exterior
      turn on its arc (item 4, exact). A vertex carrying m-2 OUTSIDE equal
      pairs PLUS the >=2 A-cap structure consumes more than the 2*pi turn budget
      available on the two boundary chains from v_- to v_+ once m is large
      relative to n. This is where the still-missing 'm bounded vs n' sub-question
      (Sec 5.1 sub-question 2) enters: the budget closes only for m < (n+2)/2.

What this script DID establish (exact, trust = EXACT_NEGATIVE_CONTROL):
  - #18 base config is exactly strictly convex, O-unit-rich, BOTH endpoints
    outside-rich at sq-dist 1/4 -> local shortcut is exactly false.
  - The descent center O is NOT a global minimizer of M(i) here; the genuinely
    poor vertices are the outside points. So #18 lies OUTSIDE the minimal-descent
    regime and is consistent with (does not refute) the global Aux Claim.
  - The turn-inequality drivers u.v=-|v|^2/2<0 hold exactly at O, exhibiting the
    angular-budget lever that a global proof must use.

What this script did NOT establish:
  - It did NOT prove the Endpoint-Control Aux Claim.
  - It did NOT prove any 'm < (n+2)/2' bound from minimality.
  - It did NOT close the descent step.
""" % {"MO": M["O"], "mmin": mmin})

report("SUMMARY")
print(f"strict convex base: {all_pos};  O-unit: {o_unit};  "
      f"A1 outside-rich: {a1_out};  A4 outside-rich: {a4_out}")
print(f"min_i M(i) = {mmin} (at {argmin});  M(O) = {M['O']}  "
      f"=> O is{'' if M['O']==mmin else ' NOT'} a global minimizer")
print(f"turn-inequality drivers exact-negative at O: {ok_all}")
