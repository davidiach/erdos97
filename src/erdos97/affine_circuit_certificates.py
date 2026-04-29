"""Exact affine-circuit certificate checks for selected witness systems.

This module implements the Prompt 2 reduction:

* build the signed affine-circuit matrix ``L`` from selected four-cohorts;
* split off the unavoidable lifted kernel ``span(1, x, y, x^2 + y^2)`` by a
  nonsingular four-point base;
* peel singleton rows to a weighted two-core;
* search for minimal-support cofactor certificates;
* analyze pure pair-gain components.

The code is exact SymPy linear algebra. It is a checker for fixed coordinates
and selected cohorts; it is not a proof that all possible systems have full
rank.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from itertools import combinations
from typing import Sequence


def _sympy():
    try:
        import sympy as sp  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dev dependency
        raise RuntimeError("SymPy is required for affine-circuit certificates") from exc
    return sp


@dataclass(frozen=True)
class QuotientReduction:
    base: list[int]
    quotient_columns: list[int]
    rank_z: int
    det_z_base: object
    kernel_dim_l: int
    kernel_dim_quotient: int


@dataclass(frozen=True)
class TwoCoreResult:
    """Result of singleton peeling.

    ``peeled_columns`` records the deterministic order used by this checker:
    rows are scanned from low to high index, and the first current singleton
    column is removed at each step. The remaining core and kernel dimension are
    the invariant data; the exact peel order is a diagnostic trace.
    """

    initial_columns: list[int]
    core_columns: list[int]
    active_rows: list[int]
    peeled_columns: list[int]
    kernel_dim_before: int
    kernel_dim_after: int


@dataclass(frozen=True)
class CofactorCertificate:
    support: list[int]
    basis_rows: list[int]
    active_rows: list[int]
    cofactors: list[object]


@dataclass(frozen=True)
class PairGainComponent:
    vertices: list[int]
    rows: list[int]
    edge_count: int
    is_tree: bool
    balanced: bool
    witness_values: dict[int, object]
    conflict: dict[str, object] | None


def _as_points(points: Sequence[Sequence[object]]):
    sp = _sympy()
    out = []
    for idx, point in enumerate(points):
        if len(point) != 2:
            raise ValueError(f"point {idx} must have length 2")
        out.append((sp.sympify(point[0]), sp.sympify(point[1])))
    return out


def _is_zero(value: object) -> bool:
    sp = _sympy()
    return value == 0 or sp.simplify(value) == 0


def lifted_matrix(points: Sequence[Sequence[object]]):
    """Return the matrix with rows ``(1, x, y, x^2+y^2)``."""
    sp = _sympy()
    pts = _as_points(points)
    return sp.Matrix([[1, x, y, sp.expand(x * x + y * y)] for x, y in pts])


def affine_area_delta(points: Sequence[Sequence[object]], a: int, b: int, c: int):
    """Return ``det [[1,x,y]_a, [1,x,y]_b, [1,x,y]_c]``."""
    sp = _sympy()
    pts = _as_points(points)
    n = len(pts)
    for label in (a, b, c):
        if label < 0 or label >= n:
            raise ValueError(f"point index out of range: {label}")
    return sp.factor(
        sp.Matrix([[1, pts[idx][0], pts[idx][1]] for idx in (a, b, c)]).det()
    )


def affine_circuit_row(
    points: Sequence[Sequence[object]],
    cohort: Sequence[int],
    n: int | None = None,
):
    """Return one signed affine-circuit row for a selected four-cohort.

    Empty cohorts are accepted and produce a zero row. Nonempty cohorts must
    contain exactly four distinct labels.
    """
    sp = _sympy()
    pts = _as_points(points)
    if n is None:
        n = len(pts)
    if len(cohort) == 0:
        return sp.zeros(1, n)
    if len(cohort) != 4:
        raise ValueError(f"cohort must be empty or length 4, got {len(cohort)}")
    if len(set(cohort)) != 4:
        raise ValueError(f"cohort contains duplicate labels: {list(cohort)}")
    for label in cohort:
        if label < 0 or label >= n:
            raise ValueError(f"cohort label out of range: {label}")

    a, b, c, d = cohort
    coeffs = {
        a: affine_area_delta(pts, b, c, d),
        b: -affine_area_delta(pts, a, c, d),
        c: affine_area_delta(pts, a, b, d),
        d: -affine_area_delta(pts, a, b, c),
    }
    row = sp.zeros(1, n)
    for col, value in coeffs.items():
        row[0, col] = sp.factor(value)
    return row


def affine_circuit_matrix(points: Sequence[Sequence[object]], cohorts: Sequence[Sequence[int]]):
    """Return the signed affine-circuit matrix ``L`` for all selected rows."""
    sp = _sympy()
    pts = _as_points(points)
    n = len(pts)
    rows = [affine_circuit_row(pts, row, n) for row in cohorts]
    if not rows:
        return sp.zeros(0, n)
    return sp.Matrix.vstack(*rows)


def matrix_is_zero(matrix) -> bool:
    """Return True if every entry simplifies to zero."""
    return all(_is_zero(entry) for entry in matrix)


def valid_lifted_bases(points: Sequence[Sequence[object]]) -> list[list[int]]:
    """Return all four-label bases with nonsingular lifted matrix."""
    Z = lifted_matrix(points)
    bases: list[list[int]] = []
    for base in combinations(range(Z.rows), 4):
        if not _is_zero(Z.extract(base, range(4)).det()):
            bases.append(list(base))
    return bases


def quotient_reduction(L, Z, base: Sequence[int]) -> QuotientReduction:
    """Return rank/nullity data for one lifted base quotient."""
    sp = _sympy()
    n = Z.rows
    if len(base) != 4:
        raise ValueError("base must contain four labels")
    if len(set(base)) != 4:
        raise ValueError(f"base contains duplicate labels: {list(base)}")
    for label in base:
        if label < 0 or label >= n:
            raise ValueError(f"base label out of range: {label}")
    det_base = sp.factor(Z.extract(base, range(4)).det())
    if _is_zero(det_base):
        raise ValueError(f"lifted base is singular: {list(base)}")
    quotient_columns = [idx for idx in range(n) if idx not in set(base)]
    return QuotientReduction(
        base=list(base),
        quotient_columns=quotient_columns,
        rank_z=int(Z.rank()),
        det_z_base=det_base,
        kernel_dim_l=int(L.cols - L.rank()),
        kernel_dim_quotient=int(len(quotient_columns) - L.extract(range(L.rows), quotient_columns).rank()),
    )


def quotient_matrix(L, base: Sequence[int]):
    """Return ``(L_N, N)`` for columns outside ``base``."""
    n = L.cols
    base_set = set(base)
    columns = [idx for idx in range(n) if idx not in base_set]
    return L.extract(range(L.rows), columns), columns


def _kernel_dim(matrix) -> int:
    return int(matrix.cols - matrix.rank())


def weighted_two_core(matrix, columns: Sequence[int] | None = None) -> TwoCoreResult:
    """Peel columns hit by singleton rows until no singleton row remains."""
    if columns is None:
        columns = list(range(matrix.cols))
    if len(columns) != matrix.cols:
        raise ValueError("columns length must match matrix column count")

    active: set[int] = set(range(matrix.cols))
    peeled: list[int] = []
    changed = True
    while changed:
        changed = False
        for row_idx in range(matrix.rows):
            nonzero = [
                col for col in sorted(active) if not _is_zero(matrix[row_idx, col])
            ]
            if len(nonzero) == 1:
                col = nonzero[0]
                active.remove(col)
                peeled.append(columns[col])
                changed = True
                break

    core_local = sorted(active)
    core_columns = [columns[col] for col in core_local]
    active_rows = [
        row_idx
        for row_idx in range(matrix.rows)
        if any(not _is_zero(matrix[row_idx, col]) for col in core_local)
    ]
    core = matrix.extract(active_rows, core_local)
    return TwoCoreResult(
        initial_columns=list(columns),
        core_columns=core_columns,
        active_rows=active_rows,
        peeled_columns=peeled,
        kernel_dim_before=_kernel_dim(matrix),
        kernel_dim_after=_kernel_dim(core),
    )


def two_core_matrix(matrix, core: TwoCoreResult):
    """Return the active-row/core-column submatrix described by ``core``."""
    local_columns = [core.initial_columns.index(col) for col in core.core_columns]
    return matrix.extract(core.active_rows, local_columns)


def _active_rows_for_support(matrix, support: Sequence[int]) -> list[int]:
    support_set = set(support)
    return [
        row_idx
        for row_idx in range(matrix.rows)
        if any(not _is_zero(matrix[row_idx, col]) for col in support_set)
    ]


def _has_singleton_row(matrix, support: Sequence[int]) -> bool:
    support_set = set(support)
    for row_idx in range(matrix.rows):
        count = sum(1 for col in support_set if not _is_zero(matrix[row_idx, col]))
        if count == 1:
            return True
    return False


def _independent_row_indices(matrix, rank: int) -> list[int]:
    if rank == 0:
        return []
    _rref, pivots = matrix.T.rref()
    return [int(idx) for idx in pivots[:rank]]


def cofactor_vector(matrix):
    """Return the cofactor null vector for a full-row-rank (m-1) x m matrix."""
    sp = _sympy()
    if matrix.cols != matrix.rows + 1:
        raise ValueError("cofactor vector needs an (m-1) x m matrix")
    values = []
    for col in range(matrix.cols):
        sub = matrix.copy()
        sub.col_del(col)
        values.append(sp.factor((-1) ** col * sub.det()))
    return values


def minimal_cofactor_certificates(
    matrix,
    columns: Sequence[int] | None = None,
    *,
    max_support_size: int | None = None,
    stop_after: int | None = None,
) -> list[CofactorCertificate]:
    """Return minimal-support cofactor certificates for ``ker(matrix)``.

    The search is exponential and intended for small cores or tests. It reports
    circuit supports: rank ``|S|-1``, one-dimensional kernel, no zero cofactor,
    and no singleton row against the support.
    """
    if columns is None:
        columns = list(range(matrix.cols))
    if len(columns) != matrix.cols:
        raise ValueError("columns length must match matrix column count")
    if max_support_size is None:
        max_support_size = matrix.cols
    if stop_after is not None and stop_after <= 0:
        return []

    certificates: list[CofactorCertificate] = []
    for size in range(1, min(max_support_size, matrix.cols) + 1):
        for support in combinations(range(matrix.cols), size):
            if _has_singleton_row(matrix, support):
                continue
            active_rows = _active_rows_for_support(matrix, support)
            sub = matrix.extract(active_rows, support)
            if sub.rank() != size - 1:
                continue
            if _kernel_dim(sub) != 1:
                continue
            basis_local = _independent_row_indices(sub, size - 1)
            basis_rows = [active_rows[idx] for idx in basis_local]
            basis_matrix = matrix.extract(basis_rows, support)
            cofactors = cofactor_vector(basis_matrix)
            if any(_is_zero(value) for value in cofactors):
                continue
            certificates.append(
                CofactorCertificate(
                    support=[columns[col] for col in support],
                    basis_rows=basis_rows,
                    active_rows=active_rows,
                    cofactors=cofactors,
                )
            )
            if stop_after is not None and len(certificates) >= stop_after:
                return certificates
    return certificates


def pair_gain_components(matrix, columns: Sequence[int] | None = None) -> list[PairGainComponent]:
    """Analyze connected components consisting only of pair rows.

    Rows meeting other than two active columns are ignored by this helper. Use
    it on a pure pair-row component, or as a diagnostic before mixed hypercore
    handling.
    """
    sp = _sympy()
    if columns is None:
        columns = list(range(matrix.cols))
    if len(columns) != matrix.cols:
        raise ValueError("columns length must match matrix column count")

    adjacency: dict[int, list[tuple[int, int, object]]] = defaultdict(list)
    edge_rows: set[int] = set()
    for row_idx in range(matrix.rows):
        nz = [col for col in range(matrix.cols) if not _is_zero(matrix[row_idx, col])]
        if len(nz) != 2:
            continue
        u, v = nz
        gain_uv = sp.factor(-matrix[row_idx, u] / matrix[row_idx, v])
        gain_vu = sp.factor(-matrix[row_idx, v] / matrix[row_idx, u])
        adjacency[u].append((v, row_idx, gain_uv))
        adjacency[v].append((u, row_idx, gain_vu))
        edge_rows.add(row_idx)

    seen: set[int] = set()
    components: list[PairGainComponent] = []
    for start in sorted(adjacency):
        if start in seen:
            continue
        values = {start: sp.Integer(1)}
        rows: set[int] = set()
        vertices: set[int] = set()
        balanced = True
        conflict: dict[str, object] | None = None
        q: deque[int] = deque([start])
        seen.add(start)
        while q:
            u = q.popleft()
            vertices.add(u)
            for v, row_idx, gain in adjacency[u]:
                rows.add(row_idx)
                expected = sp.factor(values[u] * gain)
                if v not in values:
                    values[v] = expected
                    seen.add(v)
                    q.append(v)
                elif sp.simplify(values[v] - expected) != 0:
                    balanced = False
                    if conflict is None:
                        conflict = {
                            "row": row_idx,
                            "from": columns[u],
                            "to": columns[v],
                            "existing": values[v],
                            "expected": expected,
                        }
        edge_count = len(rows)
        vertex_list = sorted(vertices)
        components.append(
            PairGainComponent(
                vertices=[columns[col] for col in vertex_list],
                rows=sorted(rows),
                edge_count=edge_count,
                is_tree=edge_count == len(vertex_list) - 1,
                balanced=balanced,
                witness_values={columns[col]: sp.factor(values[col]) for col in vertex_list},
                conflict=conflict,
            )
        )
    return components


def golden_decagon_example():
    """Return the exact 10-point nonconvex all-bad example and cohorts.

    The outer five points form a regular pentagon and the inner five points
    lie strictly inside it, so this is a negative-control example for the
    algebraic checker, not a convex-polygon candidate.
    """
    sp = _sympy()
    sqrt5 = sp.sqrt(5)
    rho = (sp.Integer(3) - sqrt5) / 2
    points = []
    for idx in range(10):
        radius = sp.Integer(1) if idx % 2 == 0 else rho
        theta = sp.pi * idx / 5
        points.append((sp.simplify(radius * sp.cos(theta)), sp.simplify(radius * sp.sin(theta))))

    cohorts: list[list[int]] = []
    for idx in range(10):
        offsets = [-3, -2, 2, 3] if idx % 2 == 0 else [-4, -1, 1, 4]
        cohorts.append(sorted((idx + offset) % 10 for offset in offsets))
    return points, cohorts


def single_circle_row_example():
    """Return a small exact example with one selected concyclic four-cohort."""
    sp = _sympy()
    points = [
        (sp.Integer(1), sp.Integer(0)),
        (sp.Integer(0), sp.Integer(1)),
        (sp.Integer(-1), sp.Integer(0)),
        (sp.Integer(0), sp.Integer(-1)),
        (sp.Integer(2), sp.Integer(3)),
        (sp.Integer(3), sp.Integer(5)),
    ]
    cohorts = [[], [], [], [], [], [0, 1, 2, 3]]
    return points, cohorts


def _json_value(value: object) -> str:
    return str(value)


def certificate_to_json(certificate: CofactorCertificate) -> dict[str, object]:
    return {
        "support": certificate.support,
        "basis_rows": certificate.basis_rows,
        "active_rows": certificate.active_rows,
        "cofactors": [_json_value(value) for value in certificate.cofactors],
    }


def pair_component_to_json(component: PairGainComponent) -> dict[str, object]:
    return {
        "vertices": component.vertices,
        "rows": component.rows,
        "edge_count": component.edge_count,
        "is_tree": component.is_tree,
        "balanced": component.balanced,
        "witness_values": {
            str(vertex): _json_value(value)
            for vertex, value in sorted(component.witness_values.items())
        },
        "conflict": None
        if component.conflict is None
        else {
            key: _json_value(value) if key in {"existing", "expected"} else value
            for key, value in component.conflict.items()
        },
    }


def analysis_to_json(
    *,
    example: str,
    base: Sequence[int],
    L,
    Z,
    quotient: QuotientReduction,
    core: TwoCoreResult,
    certificates: Sequence[CofactorCertificate],
    pair_components: Sequence[PairGainComponent],
) -> dict[str, object]:
    return {
        "type": "affine_circuit_certificate_analysis",
        "status": "exact_checker_not_a_proof",
        "example": example,
        "n": int(Z.rows),
        "rank_z": quotient.rank_z,
        "lz_zero": matrix_is_zero(L * Z),
        "base": list(base),
        "det_z_base": _json_value(quotient.det_z_base),
        "kernel_dim_l": quotient.kernel_dim_l,
        "kernel_dim_quotient": quotient.kernel_dim_quotient,
        "quotient_columns": quotient.quotient_columns,
        "two_core": {
            "initial_columns": core.initial_columns,
            "core_columns": core.core_columns,
            "active_rows": core.active_rows,
            "peeled_columns": core.peeled_columns,
            "kernel_dim_before": core.kernel_dim_before,
            "kernel_dim_after": core.kernel_dim_after,
        },
        "certificates": [certificate_to_json(cert) for cert in certificates],
        "pair_gain_components": [
            pair_component_to_json(component) for component in pair_components
        ],
    }
