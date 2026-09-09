"""Replay every exact geometric subdomain and exhaustive witness-row search."""
from __future__ import annotations

import argparse
import hashlib
from itertools import combinations_with_replacement, product
import json
from pathlib import Path
import sys

from geometry import context, models, split
from prior import archive_hash
from row_search import Search

ROOT = Path(__file__).resolve().parent
BASE_SHA = "047d05149382e48b602b292df4b8fc9e2da560bb"


def expected_cases():
    return [
        (a, b, old_f, old_g)
        for a, b in combinations_with_replacement(range(9), 2)
        for old_f, old_g in product([None] + list(range(9)), repeat=2)
    ]


def canonical(data):
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def validate_structure(report):
    expected_fields = {"schema", "base_sha", "input_sha256", "not_an_unrestricted_solution", "cases"}
    if not isinstance(report, dict) or set(report) != expected_fields:
        raise ValueError("Unexpected certificate fields")
    if report.get("schema") != "erdos97.two_free_partition.v1":
        raise ValueError("Unexpected certificate schema")
    if report.get("base_sha") != BASE_SHA or report.get("input_sha256") != archive_hash():
        raise ValueError("Certificate provenance mismatch")
    if report.get("not_an_unrestricted_solution") is not True:
        raise ValueError("Missing claim boundary")
    cases = report["cases"]
    keys = []
    for case in cases:
        if set(case) != {"cells", "old_witnesses", "tree"}:
            raise ValueError("Unexpected case fields")
        cells, old = case["cells"], case["old_witnesses"]
        if len(cells) != 2 or any(type(c) is not int or not 0 <= c < 9 for c in cells):
            raise ValueError("Invalid cell pair")
        if len(old) != 2 or any(k is not None and (type(k) is not int or not 0 <= k < 9) for k in old):
            raise ValueError("Invalid old-support choice")
        keys.append(tuple(cells + old))
    if keys != expected_cases():
        raise ValueError("Case coverage differs from all 4,500 support/region choices")


def verify(report, selected_indices=None, progress=False):
    validate_structure(report)
    if selected_indices is not None:
        if (len(set(selected_indices)) != len(selected_indices)
                or any(type(i) is not int or not 0 <= i < 4500 for i in selected_indices)):
            raise ValueError("Invalid selected case indices")
    _, slots, edges, ceiling, triangles = context()
    totals = {"cases": 0, "partition_nodes": 0, "leaves": 0, "maximum_depth": 0,
              "row_models": 0, "row_search_nodes": 0,
              "metric_zero_rejections": 0, "metric_inverse_rejections": 0}
    leaf_digest = hashlib.sha256()
    indices = range(len(report["cases"])) if selected_indices is None else selected_indices
    for index in indices:
        case = report["cases"][index]
        cells = case["cells"]
        old = case["old_witnesses"]
        def visit(tree, first, second, depth):
            totals["partition_nodes"] += 1
            totals["maximum_depth"] = max(totals["maximum_depth"], depth)
            if tree is None:
                totals["leaves"] += 1
                batch = models(first, second, cells, old)
                nodes = []
                for model in batch:
                    result = Search(model).run()
                    if result["status"] != "exhausted":
                        raise ValueError(f"Unresolved exact subdomain in case {index}: {result}")
                    nodes.append(result["nodes"])
                    for kind in ("zero", "inverse"):
                        totals[f"metric_{kind}_rejections"] += result["metric_rejections"][kind]
                totals["row_models"] += len(batch)
                totals["row_search_nodes"] += sum(nodes)
                leaf_digest.update((json.dumps([index, depth, nodes]) + "\n").encode())
                return
            if not isinstance(tree, dict) or set(tree) != {"coordinate", "edge", "children"}:
                raise ValueError("Malformed subdivision node")
            which, edge, children = tree["coordinate"], tree["edge"], tree["children"]
            if type(which) is not int or which not in (0, 1) or not isinstance(children, list) or len(children) != 2:
                raise ValueError("Incomplete product-domain subdivision")
            pieces = split((first, second)[which], edge)
            for subtree, piece in zip(children, pieces):
                visit(subtree, piece if which == 0 else first,
                      second if which == 0 else piece, depth + 1)
        visit(case["tree"], triangles[cells[0]], triangles[cells[1]], 0)
        totals["cases"] += 1
        if progress and totals["cases"] % 100 == 0:
            print(json.dumps(totals), flush=True, file=sys.stderr)
    return {"status": "passed", **totals, "leaf_digest": leaf_digest.hexdigest(),
            "slot_count": len(slots), "base_edge_count": len(edges), "old_ceiling": ceiling,
            "input_sha256": archive_hash(), "scope": "fixed-seed two-internally-supported-vertex exclusion",
            "external_mathematical_review": False, "formalization": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--progress", action="store_true")
    parser.add_argument("--cases", nargs="*", type=int)
    args = parser.parse_args()
    report = json.loads((ROOT / "data/certificate.json").read_text())
    output = canonical(verify(report, args.cases, args.progress))
    path = ROOT / "data/primary_report.json"
    if args.write:
        if args.cases is not None:
            raise ValueError("Cannot publish a partial replay as the full report")
        path.write_text(output)
    if args.check and path.read_text() != output:
        raise ValueError("Replayed report differs")
    print(output)


if __name__ == "__main__":
    main()
