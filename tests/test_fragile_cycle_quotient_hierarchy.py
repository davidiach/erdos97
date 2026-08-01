from __future__ import annotations

from erdos97.fragile_cycle_quotient_hierarchy import (
    EXPECTED_TEMPLATE_ACCOUNTING,
    assert_expected_payload,
    certificate_templates,
    enumerate_admissible_quotients,
    hierarchy_payload,
    restricted_growth_partitions,
)


def test_restricted_growth_partition_counts() -> None:
    assert len(list(restricted_growth_partitions(4))) == 15
    assert len(list(restricted_growth_partitions(5))) == 52
    assert len(list(restricted_growth_partitions(8))) == 4140


def test_template_partition_accounting() -> None:
    for template in certificate_templates():
        result = enumerate_admissible_quotients(template)
        assert (
            result["partition_accounting"]
            == EXPECTED_TEMPLATE_ACCOUNTING[template.name]
        )
        assert all(
            record["certificate"]["zero_sum_verified"]
            for record in result["quotients"]
        )


def test_scalable_template_has_two_nontrivial_quotients() -> None:
    scalable = certificate_templates()[2]
    result = enumerate_admissible_quotients(scalable)
    nontrivial = [
        record
        for record in result["quotients"]
        if record["vertex_count"] < len(scalable.labels)
    ]
    assert [record["role_blocks"] for record in nontrivial] == [
        [[1], [8], [16], [18, 23], [27], [37], [44]],
        [[1], [8], [16], [18], [23, 27], [37], [44]],
    ]
    assert all(record["compatible_cyclic_order_count"] == 1 for record in nontrivial)


def test_hierarchy_payload_expected() -> None:
    payload = hierarchy_payload()
    assert_expected_payload(payload)
    assert payload["summary"]["strict_support_levels"] == [1, 2, 4]
    assert payload["summary"]["admissible_partition_count"] == 5
    assert payload["summary"]["nontrivial_admissible_partition_count"] == 2
