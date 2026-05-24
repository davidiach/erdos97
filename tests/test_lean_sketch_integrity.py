from pathlib import Path

from scripts.check_lean_sketch_integrity import check_tree


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_accepts_marked_sketch(tmp_path: Path) -> None:
    write(
        tmp_path / "lean" / "Erdos97" / "Basic.lean",
        "/- not the official geometric statement -/\n",
    )
    write(
        tmp_path / "lean" / "Erdos97" / "Sketches" / "T01.lean",
        "\n".join(
            [
                "-- EVOLVE-BLOCK-START",
                "theorem local_placeholder : True := by",
                "  trivial",
                "-- EVOLVE-BLOCK-END",
            ]
        ),
    )

    assert check_tree(tmp_path) == []


def test_rejects_sorry_outside_evolve_block(tmp_path: Path) -> None:
    write(
        tmp_path / "lean" / "Erdos97" / "Basic.lean",
        "/- not the official geometric statement -/\n",
    )
    write(
        tmp_path / "lean" / "Erdos97" / "Sketches" / "T01.lean",
        "\n".join(
            [
                "theorem local_placeholder : True := by",
                "  sorry",
                "-- EVOLVE-BLOCK-START",
                "-- EVOLVE-BLOCK-END",
            ]
        ),
    )

    findings = check_tree(tmp_path)

    assert any("inside an EVOLVE block" in finding.message for finding in findings)


def test_rejects_miracle_lemma_name(tmp_path: Path) -> None:
    write(
        tmp_path / "lean" / "Erdos97" / "Basic.lean",
        "/- not the official geometric statement -/\n",
    )
    write(
        tmp_path / "lean" / "Erdos97" / "Sketches" / "T01.lean",
        "\n".join(
            [
                "-- EVOLVE-BLOCK-START",
                "lemma no_bad_convex_polygon_nine : True := by",
                "  trivial",
                "-- EVOLVE-BLOCK-END",
            ]
        ),
    )

    findings = check_tree(tmp_path)

    assert any("miracle lemma" in finding.message for finding in findings)
