import pytest

from erdos97.n10_kalmanson_pair_filter import N10KalmansonPairSearch


def test_pair_filter_recognizes_small_exact_obstructions() -> None:
    search = N10KalmansonPairSearch()
    row_mask = search.base._mask

    hinge = {
        0: row_mask((1, 2, 4, 5)),
        1: row_mask((0, 2, 6, 7)),
        3: row_mask((0, 1, 8, 9)),
    }
    ladder = {
        0: row_mask((1, 2, 3, 5)),
        3: row_mask((0, 1, 5, 7)),
        9: row_mask((0, 2, 7, 8)),
    }

    assert search.status(hinge) == "self_edge"
    assert search.status(ladder) == "inverse_pair"


def test_explicit_rows_reject_a_self_witness() -> None:
    rows = tuple((0, 1, 2, 3) for _center in range(10))

    with pytest.raises(ValueError, match="cannot contain its center"):
        N10KalmansonPairSearch().rows_status(rows)


def test_explicit_rows_reject_an_out_of_range_witness() -> None:
    rows = tuple((0, 1, 2, 3) for _center in range(10))
    rows = ((1, 2, 3, 10), *rows[1:])

    with pytest.raises(ValueError, match="out-of-range witness"):
        N10KalmansonPairSearch().rows_status(rows)


@pytest.mark.slow
def test_python_row0_slice_matches_cpp_replay() -> None:
    result = N10KalmansonPairSearch().search_slice(0, 1)

    assert result.to_dict() == {
        "row0_start": 0,
        "row0_end": 1,
        "nodes": 835,
        "self_edge_prunes": 245,
        "inverse_pair_prunes": 2_620,
        "full_assignments": 0,
        "closed": True,
    }
