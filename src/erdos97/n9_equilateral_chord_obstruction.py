"""Exact obstruction for bad *equilateral* strictly convex nonagons.

A polygon is ``bad`` when every vertex has four other vertices at one common
distance from it.  ``docs/n8-geometric-proof.md`` rules out bad strictly
convex polygons with ``n <= 8``; ``n = 9`` is open.  This module closes the
sub-case in which the nonagon is additionally equilateral.

The argument, written out in ``docs/n9-equilateral-chord-obstruction.md``,
reduces a bad equilateral nonagon to a finite question about its
*unit-distance chord graph*

``H = {non-adjacent vertex pairs whose distance equals the side length}``

together with linear constraints on the normalized exterior turns
``x_j = tau_j / (2*pi)``.  The reduction gives

- every ``H``-degree is ``0`` or ``2``;
- ``a <= 2*m2``, where ``a`` is the number of ``H``-isolated vertices and
  ``m2`` the number of ``H``-chords of cyclic step ``2``;
- a chord of step ``2`` pins its single interior turn to ``1/3``;
- a chord of step ``3`` pins its two interior turns to sum to ``1/2``;
- a chord of step ``4`` forces its three interior turns to sum to at least
  ``2*arccos(1/4)/(2*pi) = 0.41956...``.

Each of the 8097 admissible chord graphs is then refuted by an explicit
integer multiplier vector (a Farkas-style certificate) that needs nothing
beyond ``sum_j x_j = 1`` and ``x_j > 0``.  The certificates are stored in
``data/certificates/n9_equilateral_chord_obstruction.json`` and are verified
by direct rational arithmetic, independent of how they were found.

Scope: this is a repo-local exact result about equilateral nonagons only.  It
is not a proof of Erdos Problem #97, it says nothing about non-equilateral
nonagons, and it is not a counterexample.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from typing import Any, Iterable, Sequence

N = 9
STEPS = (2, 3, 4)

#: Turn thresholds per chord step, as fractions of the total turn ``2*pi``.
#: Steps 2 and 3 are exact equalities; step 4 is a lower bound.  The exact
#: Machin/Taylor certificate below proves
#: ``4195/10000 < 2*arccos(1/4)/(2*pi)`` without floating-point arithmetic.
STEP2_TURN = Fraction(1, 3)
STEP3_TURN = Fraction(1, 2)
STEP4_TURN_LOWER_BOUND = Fraction(4195, 10000)
TURN_BOUND = {2: STEP2_TURN, 3: STEP3_TURN, 4: STEP4_TURN_LOWER_BOUND}

#: Chords of step 4 only ever give a lower bound, so their multiplier must be
#: non-negative; steps 2 and 3 are equalities and take either sign.
EQUALITY_STEPS = (2, 3)

MAX_ISOLATED = 4
MULTIPLIER_RANGE = (-1, 0, 1)

SCHEMA = "erdos97.n9_equilateral_chord_obstruction.v1"
STATUS = "NO_BAD_STRICTLY_CONVEX_EQUILATERAL_NONAGON"
TRUST = "EXACT_OBSTRUCTION"
CLAIM_SCOPE = (
    "Exact finite certificate that no bad strictly convex equilateral nonagon "
    "exists: every admissible unit-distance chord graph is refuted by an "
    "integer multiplier certificate on the exterior-turn constraints. This is "
    "an equilateral sub-case of n=9 only; it is not a proof of Erdos Problem "
    "#97, says nothing about non-equilateral nonagons, and is not a "
    "counterexample."
)
PROVENANCE = {
    "generator": "scripts/check_n9_equilateral_chord_obstruction.py",
    "command": (
        "python scripts/check_n9_equilateral_chord_obstruction.py "
        "--assert-expected --write"
    ),
}

EXPECTED_DEGREE_GRAPH_COUNT = 8712
EXPECTED_ADMISSIBLE_GRAPH_COUNT = 8097
EXPECTED_DIHEDRAL_CLASS_COUNT = 534
EXPECTED_SURVIVOR_COUNT = 0

Chord = tuple[int, int, int]
Graph = tuple[Chord, ...]


def _arctan_partial(argument: Fraction, last_index: int) -> Fraction:
    """Return the exact alternating arctangent partial sum through ``last_index``."""

    return sum(
        (
            (-1) ** index
            * argument ** (2 * index + 1)
            / Fraction(2 * index + 1)
            for index in range(last_index + 1)
        ),
        Fraction(0),
    )


def machin_pi_upper_bound() -> Fraction:
    """Return a certified rational upper bound for ``pi``.

    Machin's identity is

    ``pi = 16*atan(1/5) - 4*atan(1/239)``.

    The alternating arctangent series gives an upper bound when truncated
    after a positive term and a lower bound when truncated after a negative
    term.  Hence the five-term ``atan(1/5)`` sum and the two-term
    ``atan(1/239)`` sum give the returned upper bound.
    """

    atan_one_fifth_upper = _arctan_partial(Fraction(1, 5), 4)
    atan_one_239th_lower = _arctan_partial(Fraction(1, 239), 1)
    return 16 * atan_one_fifth_upper - 4 * atan_one_239th_lower


def cosine_lower_bound(argument: Fraction) -> Fraction:
    """Return the exact cosine lower bound through the negative degree-10 term."""

    if argument < 0 or argument * argument >= 2:
        raise ValueError("cosine certificate requires 0 <= argument^2 < 2")
    term = Fraction(1)
    total = term
    for index in range(1, 6):
        term *= argument * argument / Fraction((2 * index - 1) * (2 * index))
        total += term if index % 2 == 0 else -term
    return total


def step4_turn_lower_bound_is_certified() -> bool:
    """Prove the rational step-4 threshold is below the exact geometric one.

    Let ``p`` be the Machin upper bound for ``pi`` and put
    ``y = (839/2000)*p``.  Exact rational arithmetic verifies ``p < 355/113``,
    ``y < 4/3``, and that the alternating degree-10 cosine lower bound at
    ``y`` exceeds ``1/4``.  Since ``pi < p`` and cosine decreases on
    ``[0, pi]``, this proves

    ``cos((839/2000)*pi) > 1/4``,

    hence ``839/2000 < arccos(1/4)/pi``.
    """

    pi_upper = machin_pi_upper_bound()
    if pi_upper >= Fraction(355, 113):
        return False
    angle_upper = STEP4_TURN_LOWER_BOUND * pi_upper
    if angle_upper >= Fraction(4, 3):
        return False
    return cosine_lower_bound(angle_upper) > Fraction(1, 4)


def candidate_chords() -> tuple[Chord, ...]:
    """Return every non-adjacent vertex pair, tagged with its cyclic step."""

    chords: list[Chord] = []
    for start in range(N):
        for step in STEPS:
            end = (start + step) % N
            chord = (min(start, end), max(start, end), step)
            if chord not in chords:
                chords.append(chord)
    return tuple(sorted(chords))


CHORDS = candidate_chords()


def chord_span(chord: Chord) -> tuple[int, ...]:
    """Return the turn indices strictly inside the short arc of ``chord``."""

    low, high, step = chord
    start = (low + 1) % N if (high - low) % N == step else (high + 1) % N
    return tuple((start + offset) % N for offset in range(step - 1))


SPAN = {chord: chord_span(chord) for chord in CHORDS}


def chord_graphs(max_isolated: int = MAX_ISOLATED) -> list[Graph]:
    """Enumerate chord graphs whose every degree is ``0`` or ``2``.

    At most ``max_isolated`` vertices may have degree ``0``; the reduction in
    the companion note shows a bad equilateral nonagon admits no other degree
    sequence.
    """

    last_use = {
        vertex: max(
            index for index, chord in enumerate(CHORDS) if vertex in chord[:2]
        )
        for vertex in range(N)
    }
    graphs: list[Graph] = []
    degree = [0] * N
    chosen: list[Chord] = []

    def recurse(index: int, isolated: int) -> None:
        if isolated > max_isolated:
            return
        if index == len(CHORDS):
            graphs.append(tuple(chosen))
            return
        low, high, _step = CHORDS[index]
        for take in (False, True):
            if take and (degree[low] == 2 or degree[high] == 2):
                continue
            if take:
                degree[low] += 1
                degree[high] += 1
                chosen.append(CHORDS[index])
            settled_ok = True
            extra = 0
            for vertex in (low, high):
                if last_use[vertex] == index:
                    if degree[vertex] == 1:
                        settled_ok = False
                    elif degree[vertex] == 0:
                        extra += 1
            if settled_ok:
                recurse(index + 1, isolated + extra)
            if take:
                degree[low] -= 1
                degree[high] -= 1
                chosen.pop()

    recurse(0, 0)
    return graphs


def step_count(graph: Graph, step: int) -> int:
    """Return the number of chords of cyclic step ``step`` in ``graph``."""

    return sum(1 for chord in graph if chord[2] == step)


def isolated_count(graph: Graph) -> int:
    """Return the number of degree-``0`` vertices of ``graph``."""

    return N - len(graph)


def ledger_admissible(graph: Graph) -> bool:
    """Return whether ``graph`` satisfies the base-apex ledger bound.

    The ledger gives ``a <= E <= 2*|M|`` where ``a`` counts ``H``-isolated
    vertices, ``E`` is the total profile excess, and ``M`` is the set of turns
    equal to ``2*pi/3``, whose size is exactly the number of step-``2`` chords.
    """

    return isolated_count(graph) <= 2 * step_count(graph, 2)


def admissible_graphs() -> list[Graph]:
    """Return the chord graphs surviving the degree and ledger conditions."""

    return [graph for graph in chord_graphs() if ledger_admissible(graph)]


def certificate_data(
    graph: Graph, multipliers: Sequence[int]
) -> tuple[Fraction, list[int]]:
    """Return ``(sum lambda_e * w_e, [c_j])`` for a multiplier vector."""

    if len(multipliers) != len(graph):
        raise ValueError("multiplier vector length must match the chord count")
    total = Fraction(0)
    counts = [0] * N
    for chord, weight in zip(graph, multipliers):
        if weight == 0:
            continue
        total += weight * TURN_BOUND[chord[2]]
        for vertex in SPAN[chord]:
            counts[vertex] += weight
    return total, counts


def verify_certificate(graph: Graph, multipliers: Sequence[int]) -> bool:
    """Return whether ``multipliers`` refute ``graph``.

    With ``c_j = sum of multipliers of chords spanning j`` we always have
    ``sum_e lambda_e * w_e <= sum_j c_j * x_j <= max_j c_j`` for any admissible
    turn vector, the first step needing ``lambda_e >= 0`` on the step-``4``
    chords only.  So the multipliers refute ``graph`` when the total exceeds
    ``max_j c_j``, and also when the two are equal while some ``c_j`` is
    strictly smaller, since then ``x`` would have to vanish somewhere.
    """

    if any(
        weight < 0 and chord[2] not in EQUALITY_STEPS
        for chord, weight in zip(graph, multipliers)
    ):
        return False
    if all(weight == 0 for weight in multipliers):
        return False
    total, counts = certificate_data(graph, multipliers)
    high = max(counts)
    if total > high:
        return True
    return total == high and min(counts) < high


def find_certificate(graph: Graph) -> tuple[int, ...] | None:
    """Search for a small refuting multiplier vector, or return ``None``.

    Plain chord subsets are tried first because they carry the whole argument
    for all but a handful of graphs; the signed search is the fallback.
    """

    size = len(graph)
    for support in range(1, size + 1):
        for chosen in combinations(range(size), support):
            multipliers = [0] * size
            for index in chosen:
                multipliers[index] = 1
            if verify_certificate(graph, multipliers):
                return tuple(multipliers)
    options = [
        MULTIPLIER_RANGE
        if chord[2] in EQUALITY_STEPS
        else tuple(value for value in MULTIPLIER_RANGE if value >= 0)
        for chord in graph
    ]
    best: tuple[int, ...] | None = None
    best_support = size + 1
    for multipliers in product(*options):
        support = sum(1 for value in multipliers if value)
        if support >= best_support:
            continue
        if verify_certificate(graph, multipliers):
            best, best_support = multipliers, support
    return best


def dihedral_maps() -> tuple[tuple[int, ...], ...]:
    """Return the 18 dihedral relabellings of the cyclic vertex order."""

    maps = []
    for shift in range(N):
        maps.append(tuple((shift + j) % N for j in range(N)))
        maps.append(tuple((shift - j) % N for j in range(N)))
    return tuple(maps)


DIHEDRAL = dihedral_maps()


def apply_map(graph: Graph, relabel: Sequence[int]) -> Graph:
    """Return ``graph`` relabelled by ``relabel`` (a dihedral map)."""

    moved = []
    for low, high, step in graph:
        a, b = relabel[low], relabel[high]
        moved.append((min(a, b), max(a, b), step))
    return tuple(sorted(moved))


def canonical_form(graph: Graph) -> tuple[Graph, tuple[int, ...]]:
    """Return the lexicographically least dihedral image and the map used."""

    best: Graph | None = None
    best_map: tuple[int, ...] = DIHEDRAL[0]
    for relabel in DIHEDRAL:
        image = apply_map(graph, relabel)
        if best is None or image < best:
            best, best_map = image, relabel
    assert best is not None
    return best, best_map


def transport(
    graph: Graph, relabel: Sequence[int], multipliers: Sequence[int]
) -> tuple[int, ...]:
    """Carry a certificate for ``apply_map(graph, relabel)`` back to ``graph``."""

    image = apply_map(graph, relabel)
    lookup = {chord: weight for chord, weight in zip(image, multipliers)}
    moved = []
    for low, high, step in graph:
        a, b = relabel[low], relabel[high]
        moved.append(lookup[(min(a, b), max(a, b), step)])
    return tuple(moved)


def dihedral_classes() -> list[dict[str, Any]]:
    """Return one refuted record per dihedral class of admissible graphs."""

    orbits: dict[Graph, int] = {}
    for graph in admissible_graphs():
        key, _relabel = canonical_form(graph)
        orbits[key] = orbits.get(key, 0) + 1
    records = []
    for representative in sorted(orbits):
        multipliers = find_certificate(representative)
        if multipliers is None:
            raise AssertionError(f"no certificate found for {representative}")
        total, counts = certificate_data(representative, multipliers)
        records.append(
            {
                "chords": [list(chord) for chord in representative],
                "orbit_size": orbits[representative],
                "multipliers": list(multipliers),
                "bound_total": str(total),
                "span_counts": counts,
                "strict": total > max(counts),
            }
        )
    return records


def _record_graph(record: dict[str, Any]) -> Graph:
    return tuple(
        (int(chord[0]), int(chord[1]), int(chord[2])) for chord in record["chords"]
    )


def check_classes(records: Iterable[dict[str, Any]]) -> list[str]:
    """Replay the enumeration against stored class records.

    Every admissible graph is mapped to its class representative, the stored
    certificate is transported back to that graph, and verified there.  This
    keeps the check independent of the dihedral bookkeeping.
    """

    errors: list[str] = []
    by_representative: dict[Graph, dict[str, Any]] = {}
    for record in records:
        graph = _record_graph(record)
        if graph in by_representative:
            errors.append(f"duplicate class representative {graph}")
        by_representative[graph] = record
        if canonical_form(graph)[0] != graph:
            errors.append(f"class representative {graph} is not canonical")
        if not verify_certificate(graph, record["multipliers"]):
            errors.append(f"certificate fails on representative {graph}")

    seen: dict[Graph, int] = {}
    for graph in admissible_graphs():
        key, relabel = canonical_form(graph)
        record = by_representative.get(key)
        if record is None:
            errors.append(f"admissible graph {graph} has no stored class")
            continue
        seen[key] = seen.get(key, 0) + 1
        moved = transport(graph, relabel, record["multipliers"])
        if not verify_certificate(graph, moved):
            errors.append(f"transported certificate fails on {graph}")
    for key, record in by_representative.items():
        if seen.get(key, 0) != record["orbit_size"]:
            errors.append(f"orbit size mismatch for {key}")
    return errors[:20]


def payload() -> dict[str, Any]:
    """Return the stable exact certificate payload."""

    degree_graphs = chord_graphs()
    admissible = [graph for graph in degree_graphs if ledger_admissible(graph)]
    records = dihedral_classes()
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "turn_bounds": {
            "step_2_equals": str(STEP2_TURN),
            "step_3_equals": str(STEP3_TURN),
            "step_4_at_least": str(STEP4_TURN_LOWER_BOUND),
            "step_4_exact_bound": "2*arccos(1/4)/(2*pi)",
        },
        "counts": {
            "degree_admissible_graphs": len(degree_graphs),
            "ledger_admissible_graphs": len(admissible),
            "dihedral_classes": len(records),
            "refuted_classes": len(records),
            "surviving_graphs": EXPECTED_SURVIVOR_COUNT,
            "strict_certificates": sum(1 for record in records if record["strict"]),
        },
        "classes": records,
        "provenance": dict(PROVENANCE),
    }


def validate_payload(data: dict[str, Any]) -> list[str]:
    """Return structural and mathematical errors in a stored payload."""

    errors: list[str] = []
    if data.get("schema") != SCHEMA:
        errors.append("unexpected schema")
    for key in ("status", "trust", "claim_scope", "n", "counts", "classes"):
        if key not in data:
            errors.append(f"missing key {key}")
    if errors:
        return errors
    if data["n"] != N:
        errors.append("unexpected n")
    if not step4_turn_lower_bound_is_certified():
        errors.append("step-4 rational turn bound lacks an exact certificate")
    bounds = data.get("turn_bounds", {})
    if (
        bounds.get("step_2_equals") != str(STEP2_TURN)
        or bounds.get("step_3_equals") != str(STEP3_TURN)
        or bounds.get("step_4_at_least") != str(STEP4_TURN_LOWER_BOUND)
    ):
        errors.append("stored turn bounds do not match the module constants")
    records = data["classes"]
    errors.extend(check_classes(records))
    counts = data["counts"]
    degree_graphs = chord_graphs()
    admissible = [graph for graph in degree_graphs if ledger_admissible(graph)]
    if counts.get("degree_admissible_graphs") != len(degree_graphs):
        errors.append("degree_admissible_graphs mismatch")
    if counts.get("ledger_admissible_graphs") != len(admissible):
        errors.append("ledger_admissible_graphs mismatch")
    if counts.get("dihedral_classes") != len(records):
        errors.append("dihedral_classes mismatch")
    if counts.get("surviving_graphs") != EXPECTED_SURVIVOR_COUNT:
        errors.append("surviving_graphs must be zero")
    if sum(record["orbit_size"] for record in records) != len(admissible):
        errors.append("orbit sizes do not cover the admissible graphs")
    return errors[:20]


def assert_expected_payload(data: dict[str, Any]) -> None:
    """Assert the stable pinned fields of the payload."""

    expected = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "provenance": dict(PROVENANCE),
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise AssertionError(f"unexpected value for {key}")
    counts = data.get("counts", {})
    pinned = {
        "degree_admissible_graphs": EXPECTED_DEGREE_GRAPH_COUNT,
        "ledger_admissible_graphs": EXPECTED_ADMISSIBLE_GRAPH_COUNT,
        "dihedral_classes": EXPECTED_DIHEDRAL_CLASS_COUNT,
        "refuted_classes": EXPECTED_DIHEDRAL_CLASS_COUNT,
        "surviving_graphs": EXPECTED_SURVIVOR_COUNT,
    }
    for key, value in pinned.items():
        if counts.get(key) != value:
            raise AssertionError(f"unexpected count for {key}")
    errors = validate_payload(data)
    if errors:
        raise AssertionError("; ".join(errors[:5]))
