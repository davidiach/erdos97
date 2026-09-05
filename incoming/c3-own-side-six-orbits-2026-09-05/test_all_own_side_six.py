"""Regression coverage for the complete five/six-orbit graph classification."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("all_own_side_six", ROOT / "all_systems.py")
assert SPEC is not None and SPEC.loader is not None
s = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(s)


class AllOwnSideSixTests(unittest.TestCase):
    def test_complete_oriented_graph_counts(self):
        for n, expected in ((5, 24), (6, 14490)):
            graphs = list(s.oriented_graphs(n))
            self.assertEqual(len(graphs), expected)
            self.assertEqual(len(set(graphs)), expected)
            for graph in graphs:
                for i, row in enumerate(graph):
                    self.assertEqual(len(set(row)), 2)
                    self.assertNotIn(i, row)
                    self.assertTrue(all(i not in graph[j] for j in row))

    def test_every_discarded_graph_has_an_explicit_valid_path(self):
        records, survivors = s.graph_audit()
        self.assertEqual(len(records), 14514)
        self.assertEqual(tuple(survivors), s.EXPECTED_GRAPHS)
        for record in records:
            if record["shortcut"] is not None:
                s.verify_shortcut(record["graph"], record["shortcut"])

    def test_bounded_size_is_not_silently_extended(self):
        for n in (0, 4, 7):
            with self.assertRaises(ValueError):
                list(s.oriented_graphs(n))

    def test_shortcut_requires_an_alternative_path(self):
        records, _ = s.graph_audit()
        record = next(r for r in records if r["shortcut"] is not None)
        bad = deepcopy(record["shortcut"])
        bad["path"] = [bad["edge"][1], bad["edge"][0]]
        with self.assertRaises(ValueError):
            s.verify_shortcut(record["graph"], bad)

    def test_shortcut_requires_increasing_radii(self):
        records, _ = s.graph_audit()
        record = next(r for r in records if r["shortcut"] is not None)
        bad = deepcopy(record["shortcut"])
        bad["path"] = bad["path"][::-1]
        with self.assertRaises(ValueError):
            s.verify_shortcut(record["graph"], bad)

    def test_generated_all_systems_report(self):
        report, graphs, phases = s.generate()
        self.assertEqual(report, json.loads((ROOT / "all_systems_report.json").read_text()))
        self.assertEqual(len(graphs), 14514)
        self.assertEqual(len(phases), 7680)
        self.assertEqual(report["n5"]["survivors"], 0)
        self.assertEqual(report["n6"]["final_survivors"], 0)


if __name__ == "__main__":
    unittest.main()
