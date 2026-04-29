from __future__ import annotations

import sympy as sp

from erdos97.affine_circuit_certificates import (
    affine_circuit_matrix,
    golden_decagon_example,
    lifted_matrix,
    matrix_is_zero,
    minimal_cofactor_certificates,
    pair_gain_components,
    quotient_matrix,
    quotient_reduction,
    single_circle_row_example,
    two_core_matrix,
    valid_lifted_bases,
    weighted_two_core,
)


def test_single_concyclic_row_annihilates_lifted_columns() -> None:
    points, cohorts = single_circle_row_example()

    L = affine_circuit_matrix(points, cohorts)
    Z = lifted_matrix(points)

    assert Z.rank() == 4
    assert matrix_is_zero(L * Z)


def test_quotient_and_two_core_detect_isolated_column() -> None:
    points, cohorts = single_circle_row_example()
    L = affine_circuit_matrix(points, cohorts)
    Z = lifted_matrix(points)
    base = [0, 1, 2, 4]

    quotient = quotient_reduction(L, Z, base)
    LN, columns = quotient_matrix(L, base)
    core = weighted_two_core(LN, columns)
    A_core = two_core_matrix(LN, core)
    certs = minimal_cofactor_certificates(A_core, core.core_columns)

    assert quotient.kernel_dim_l == 4 + quotient.kernel_dim_quotient
    assert core.kernel_dim_before == core.kernel_dim_after
    assert core.peeled_columns == [3]
    assert core.core_columns == [5]
    assert certs
    assert certs[0].support == [5]
    assert certs[0].cofactors == [1]


def test_golden_decagon_exact_example_has_lifted_kernel() -> None:
    points, cohorts = golden_decagon_example()
    L = affine_circuit_matrix(points, cohorts)
    Z = lifted_matrix(points)

    assert Z.rank() == 4
    assert matrix_is_zero(L * Z)
    assert valid_lifted_bases(points)


def test_pair_gain_tree_and_balanced_cycle_components() -> None:
    tree = sp.Matrix([[1, -2, 0], [0, 3, -4]])
    tree_components = pair_gain_components(tree)
    assert len(tree_components) == 1
    assert tree_components[0].is_tree
    assert tree_components[0].balanced

    balanced_cycle = sp.Matrix([[1, -1, 0], [0, 1, -1], [-1, 0, 1]])
    balanced_components = pair_gain_components(balanced_cycle)
    assert len(balanced_components) == 1
    assert not balanced_components[0].is_tree
    assert balanced_components[0].balanced

    unbalanced_cycle = sp.Matrix([[1, -1, 0], [0, 1, -1], [-2, 0, 1]])
    unbalanced_components = pair_gain_components(unbalanced_cycle)
    assert len(unbalanced_components) == 1
    assert not unbalanced_components[0].balanced


def test_minimal_cofactor_certificate_for_pair_tree() -> None:
    matrix = sp.Matrix([[1, -2, 0], [0, 3, -4]])

    certs = minimal_cofactor_certificates(matrix)

    assert len(certs) == 1
    assert certs[0].support == [0, 1, 2]
    assert certs[0].basis_rows == [0, 1]
    assert all(value != 0 for value in certs[0].cofactors)
