"""Generic three-row equilateral hinge behind a Kalmanson self-edge.

For cyclically ordered ``A,B,C,D``, the three row requirements

``A: {B,C}``, ``B: {A,C}``, and ``D: {A,B}``

force the two sides of the strict K2 inequality to be equal.  A dihedral
reorientation of a stored cyclic quadruple may present the same inequality as
either K1 or K2.  This module only recognizes that local equality pattern; it
does not assert that a polygon or a family of row systems must contain one.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import combinations
from typing import TypeAlias

Label: TypeAlias = int
Pair: TypeAlias = tuple[Label, Label]
Equality: TypeAlias = tuple[Pair, Pair]
RowsInput: TypeAlias = Mapping[Label, Sequence[Label]] | Sequence[Sequence[Label]]


def _label(value: object, name: str) -> Label:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int (not bool)")
    return value


def _label_sequence(
    values: object,
    name: str,
    *,
    expected_length: int | None = None,
) -> tuple[Label, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise TypeError(f"{name} must be a sequence of ints")
    labels = tuple(_label(value, f"{name}[{index}]") for index, value in enumerate(values))
    if expected_length is not None and len(labels) != expected_length:
        raise ValueError(f"{name} must contain exactly {expected_length} labels")
    if len(set(labels)) != len(labels):
        raise ValueError(f"{name} must not contain duplicate labels")
    return labels


def _pair(a: Label, b: Label) -> Pair:
    if a == b:
        raise ValueError("a distance pair requires two distinct labels")
    return (a, b) if a < b else (b, a)


@dataclass(frozen=True)
class HingeInstance:
    """One oriented K2 hinge, expressed against a stored cyclic quadruple."""

    quadruple: tuple[Label, Label, Label, Label]
    a: Label
    b: Label
    c: Label
    d: Label
    centers: tuple[Label, Label, Label]
    required_pairs: tuple[Pair, Pair, Pair]
    inequality_kind: str
    inequality: str
    left_pairs: tuple[Pair, Pair]
    right_pairs: tuple[Pair, Pair]
    equalities: tuple[Equality, Equality, Equality]

    @property
    def kind(self) -> str:
        """Short alias for ``inequality_kind``."""
        return self.inequality_kind

    def as_dict(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible explanation."""
        return {
            "quadruple": list(self.quadruple),
            "a": self.a,
            "b": self.b,
            "c": self.c,
            "d": self.d,
            "centers": list(self.centers),
            "required_pairs": [list(pair) for pair in self.required_pairs],
            "inequality_kind": self.inequality_kind,
            "inequality": self.inequality,
            "left_pairs": [list(pair) for pair in self.left_pairs],
            "right_pairs": [list(pair) for pair in self.right_pairs],
            "equalities": [
                {
                    "center": center,
                    "left_pair": list(left),
                    "right_pair": list(right),
                }
                for center, (left, right) in zip(
                    self.centers,
                    self.equalities,
                    strict=True,
                )
            ],
        }


def dihedral_orientations(
    quadruple: Sequence[Label],
) -> tuple[tuple[Label, Label, Label, Label], ...]:
    """Return the four rotations and four reflected rotations of a quadruple."""
    quad = _label_sequence(quadruple, "quadruple", expected_length=4)
    return tuple(
        tuple(quad[(start + direction * offset) % 4] for offset in range(4))
        for direction in (1, -1)
        for start in range(4)
    )


def _normalize_rows(
    rows: RowsInput,
    labels: tuple[Label, ...] | None,
) -> tuple[dict[Label, frozenset[Label]], tuple[Label, ...]]:
    if isinstance(rows, Mapping):
        items: list[tuple[Label, Sequence[Label]]] = []
        for raw_center, raw_row in rows.items():
            center = _label(raw_center, "row center")
            items.append((center, raw_row))
        if labels is None:
            labels = tuple(center for center, _ in items)
        elif any(center not in labels for center, _ in items):
            raise ValueError("rows contain a center outside the cyclic order")
    else:
        if isinstance(rows, (str, bytes)) or not isinstance(rows, Sequence):
            raise TypeError("rows must be a mapping or a sequence of rows")
        if labels is None:
            labels = tuple(range(len(rows)))
        elif len(rows) != len(labels):
            raise ValueError("sequence rows must align one-for-one with the cyclic order")
        items = list(zip(labels, rows, strict=True))

    known = set(labels)
    normalized: dict[Label, frozenset[Label]] = {}
    for center, raw_row in items:
        if isinstance(raw_row, (str, bytes)) or not isinstance(raw_row, Sequence):
            raise TypeError(f"row at center {center} must be a sequence of ints")
        witnesses = tuple(
            _label(value, f"row[{center}][{index}]")
            for index, value in enumerate(raw_row)
        )
        if len(set(witnesses)) != len(witnesses):
            raise ValueError(f"row at center {center} contains duplicate witnesses")
        if center in witnesses:
            raise ValueError(f"row at center {center} contains its own center")
        unknown = set(witnesses) - known
        if unknown:
            raise ValueError(
                f"row at center {center} contains unknown labels: {sorted(unknown)}"
            )
        normalized[center] = frozenset(witnesses)
    return normalized, labels


def _inequality_data(
    quadruple: tuple[Label, Label, Label, Label],
    oriented: tuple[Label, Label, Label, Label],
) -> tuple[str, str, tuple[Pair, Pair], tuple[Pair, Pair]]:
    q0, q1, q2, q3 = quadruple
    candidates = (
        (
            "K1",
            f"d({q0},{q1}) + d({q2},{q3}) < d({q0},{q2}) + d({q1},{q3})",
            (_pair(q0, q1), _pair(q2, q3)),
            (_pair(q0, q2), _pair(q1, q3)),
        ),
        (
            "K2",
            f"d({q0},{q3}) + d({q1},{q2}) < d({q0},{q2}) + d({q1},{q3})",
            (_pair(q0, q3), _pair(q1, q2)),
            (_pair(q0, q2), _pair(q1, q3)),
        ),
    )
    a, b, c, d = oriented
    oriented_left = {_pair(a, d), _pair(b, c)}
    oriented_right = {_pair(a, c), _pair(b, d)}
    for kind, description, left, right in candidates:
        if set(left) == oriented_left and set(right) == oriented_right:
            return kind, description, left, right
    raise AssertionError("a dihedral orientation must encode stored K1 or K2")


def _instance(
    quadruple: tuple[Label, Label, Label, Label],
    oriented: tuple[Label, Label, Label, Label],
) -> HingeInstance:
    a, b, c, d = oriented
    kind, description, left, right = _inequality_data(quadruple, oriented)
    return HingeInstance(
        quadruple=quadruple,
        a=a,
        b=b,
        c=c,
        d=d,
        centers=(a, b, d),
        required_pairs=((b, c), (a, c), (a, b)),
        inequality_kind=kind,
        inequality=description,
        left_pairs=left,
        right_pairs=right,
        equalities=(
            ((_pair(a, b)), (_pair(a, c))),
            ((_pair(a, b)), (_pair(b, c))),
            ((_pair(a, d)), (_pair(b, d))),
        ),
    )


def _requirements_hold(
    rows: Mapping[Label, frozenset[Label]],
    instance: HingeInstance,
) -> bool:
    return all(
        center in rows and set(required) <= rows[center]
        for center, required in zip(
            instance.centers,
            instance.required_pairs,
            strict=True,
        )
    )


def find_hinge_instances(
    rows: RowsInput,
    cyclic_order: Sequence[Label],
) -> tuple[HingeInstance, ...]:
    """Find every Kalmanson equilateral hinge in an arbitrary cyclic order.

    A mapping may omit centers; a sequence supplies one row per cyclic-order
    position.  Every supplied center and witness must be a known cyclic label.
    """
    order = _label_sequence(cyclic_order, "cyclic_order")
    normalized, _ = _normalize_rows(rows, order)
    found: list[HingeInstance] = []
    for quadruple in combinations(order, 4):
        for oriented in dihedral_orientations(quadruple):
            instance = _instance(quadruple, oriented)
            if _requirements_hold(normalized, instance):
                found.append(instance)
    return tuple(found)


def find_core_hinge_instances(
    rows: RowsInput,
    quadruple: Sequence[Label],
    core_centers: Sequence[Label],
) -> tuple[HingeInstance, ...]:
    """Find hinge orientations whose required centers are one three-row core.

    For sequence input, centers are the integer labels ``0..len(rows)-1``.
    Mapping input uses its keys as the complete label universe.  ``quadruple``
    is already in cyclic order; its eight dihedral presentations are checked.
    """
    quad = _label_sequence(quadruple, "quadruple", expected_length=4)
    core = _label_sequence(core_centers, "core_centers", expected_length=3)
    normalized, labels = _normalize_rows(rows, None)
    known = set(labels)
    unknown_quad = set(quad) - known
    if unknown_quad:
        raise ValueError(f"quadruple contains unknown labels: {sorted(unknown_quad)}")
    unknown_core = set(core) - known
    if unknown_core:
        raise ValueError(f"core_centers contains unknown labels: {sorted(unknown_core)}")

    required_center_set = set(core)
    found: list[HingeInstance] = []
    for oriented in dihedral_orientations(quad):
        instance = _instance(quad, oriented)
        if set(instance.centers) == required_center_set and _requirements_hold(
            normalized,
            instance,
        ):
            found.append(instance)
    return tuple(found)


__all__ = [
    "HingeInstance",
    "dihedral_orientations",
    "find_core_hinge_instances",
    "find_hinge_instances",
]
