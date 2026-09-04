from scripts.check_orbit66_exact_partial import build_payload, validate_payload


def test_orbit66_exact_partial_summary() -> None:
    payload = build_payload(bits=128)

    assert validate_payload(payload) == []
    assert payload["status"] == "EXACT_PARTIAL_CONSTRUCTION_NOT_A_COUNTEREXAMPLE"
    assert payload["summary"]["exact_maximum_multiplicity_distribution"] == {
        2: 3,
        3: 3,
        4: 60,
    }
    assert payload["summary"]["exceptional_orbits"] == [3, 7]
