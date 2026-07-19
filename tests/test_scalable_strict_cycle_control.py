import pytest

from erdos97.scalable_strict_cycle_control import (
    EXPECTED_SYMBOLIC_INVERSE_CLASSIFICATION_BY_KIND,
    assert_expected_structure,
    assert_expected_symbolic_inverse_classification,
    build_report,
    family_parameters,
    symbolic_inverse_classification,
)


def test_parameter_validation() -> None:
    with pytest.raises(ValueError, match="k >= 8"):
        family_parameters(7)
    with pytest.raises(TypeError, match="not bool"):
        family_parameters(True)


@pytest.mark.slow
def test_first_scalable_member_has_only_the_full_strict_cycle() -> None:
    report = build_report(8)
    assert_expected_structure(report)

    assert report.n == 47
    assert report.offsets == (9, 19, 25, 40)
    assert report.two_overlap_count == 47
    assert report.reciprocal_selected_pair_count == 0
    assert report.selected_digraph_strongly_connected
    assert report.kalmanson_self_edge_count == 0
    assert report.kalmanson_zero_based_row_count == 30_360
    assert report.kalmanson_primitive_vector_orbit_count == 7_580
    assert report.kalmanson_primitive_inverse_orbit_count == 0
    assert report.kalmanson_known_positive_circuit_size == 4
    assert report.shortest_strict_cycle == 47


@pytest.mark.slow
def test_all_k_primitive_inverse_pair_exclusion() -> None:
    summary = symbolic_inverse_classification()
    assert_expected_symbolic_inverse_classification(summary)

    assert (
        summary["template_classification_by_kind"]
        == EXPECTED_SYMBOLIC_INVERSE_CLASSIFICATION_BY_KIND
    )
