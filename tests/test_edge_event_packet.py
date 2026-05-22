from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from erdos97.edge_event_packet import (
    edge_event_report,
    edge_gram_matrix,
    edge_event_matrix,
    normalize_points,
    row_difference_identity_errors,
    selected_interval_packets,
)


ROOT = Path(__file__).resolve().parents[1]
RATIONAL_ARC_PENTAGON = [
    (0, 0),
    (1, 0),
    ("4/5", "3/5"),
    ("3/5", "4/5"),
    (0, 1),
]


def test_row_difference_identity_is_exact_on_rational_polygon() -> None:
    points = normalize_points(RATIONAL_ARC_PENTAGON)
    d_matrix = edge_event_matrix(points)
    g_matrix = edge_gram_matrix(points)

    errors = row_difference_identity_errors(d_matrix, g_matrix)

    assert all(value == 0 for row in errors for value in row)


def test_selected_equal_radius_row_gives_transverse_packets() -> None:
    points = normalize_points(RATIONAL_ARC_PENTAGON)

    packets = selected_interval_packets(points, {0: [1, 2, 3, 4]})

    assert len(packets) == 3
    assert all(packet.zero_sum_verified for packet in packets)
    assert all(packet.transverse_verified for packet in packets)
    assert [packet.edge_interval for packet in packets] == [(1,), (2,), (3,)]


def test_edge_event_report_is_json_friendly_and_verified() -> None:
    report = edge_event_report(RATIONAL_ARC_PENTAGON, {0: [1, 2, 3, 4]})

    assert report["schema"] == "erdos97.edge_event_packet.v1"
    assert report["identity_checks"]["row_difference_identity_verified"] is True
    assert report["identity_checks"]["gram_closure_verified"] is True
    assert report["identity_checks"]["column_line_cut_checks_verified"] is True
    assert report["identity_checks"]["selected_interval_packets_verified"] is True
    assert report["selected_interval_packets"][0]["row_zero_sum"] == 0


def test_edge_event_checker_accepts_utf8_sig_json(tmp_path: Path) -> None:
    input_path = tmp_path / "edge-event-input.json"
    input_path.write_text(
        json.dumps(
            {
                "coordinates": RATIONAL_ARC_PENTAGON,
                "selected_rows": {"0": [1, 2, 3, 4]},
            }
        ),
        encoding="utf-8-sig",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_edge_event_packet.py",
            str(input_path),
            "--assert-verified",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["schema"] == "erdos97.edge_event_packet.v1"
    assert payload["identity_checks"]["selected_interval_packets_verified"] is True
