"""Load fixed selected-witness patterns from JSON artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from erdos97.fragile_hypergraph import rows_from_zero_one_matrix
from erdos97.stuck_sets import validate_selected_pattern

Pattern = list[list[int]]


def _rows_from_candidate(raw: Any) -> Pattern | None:
    if not isinstance(raw, list):
        return None
    if not raw:
        return None
    if not all(isinstance(row, list) for row in raw):
        return None

    try:
        if all(len(row) == 4 for row in raw):
            rows = [[int(label) for label in row] for row in raw]
        elif all(all(value in (0, 1, False, True) for value in row) for row in raw):
            rows = rows_from_zero_one_matrix(raw)
            rows = [rows[center] for center in range(len(rows))]
        else:
            return None
        validate_selected_pattern(rows)
        return rows
    except (TypeError, ValueError):
        return None


def extract_pattern_payload(payload: Any) -> tuple[str, Pattern]:
    """Extract ``(name, selected_rows)`` from a known repo JSON shape."""

    if isinstance(payload, dict):
        name = str(payload.get("pattern") or payload.get("pattern_name") or payload.get("name") or "json_pattern")
        for key in ("selected_rows", "S", "rows"):
            rows = _rows_from_candidate(payload.get(key))
            if rows is not None:
                return name, rows
        if "motif" in payload:
            motif_name, rows = extract_pattern_payload(payload["motif"])
            if name != "json_pattern":
                return f"{name}:{motif_name}", rows
            return motif_name, rows

    rows = _rows_from_candidate(payload)
    if rows is not None:
        return "json_pattern", rows

    raise ValueError("could not find a selected-witness pattern in JSON payload")


def load_pattern_json(path: Path) -> tuple[str, Pattern]:
    """Load selected rows from a JSON file."""

    return extract_pattern_payload(json.loads(path.read_text(encoding="utf-8")))
