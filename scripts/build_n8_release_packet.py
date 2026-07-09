#!/usr/bin/env python3
"""Build the n <= 8 reviewer release packet.

The release packet is generated into ``papers/release`` so the polished note,
one-page reviewer summary, PDF renderings, and checksum bundle stay
reproducible from one command.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = ROOT / "papers" / "release"
REPOSITORY_URL = "https://github.com/davidiach/erdos97"
BUNDLE_DIRECTORY_NAME = "erdos97-n8-release"
BUNDLE_MANIFEST_NAME = "n8-artifact-bundle-manifest.json"
BUNDLE_CHECKSUMS_NAME = "n8-artifact-bundle-SHA256SUMS.txt"
ZIP_NAME = "n8-artifact-bundle.zip"
RELEASE_OUTPUT_NAMES = (
    "small-counterexamples-erdos97-release.md",
    "small-counterexamples-erdos97-release.pdf",
    "n8-review-summary.md",
    "n8-review-summary.pdf",
    BUNDLE_MANIFEST_NAME,
    BUNDLE_CHECKSUMS_NAME,
    ZIP_NAME,
    "README.md",
    "SHA256SUMS.txt",
)
BUILDER_PATH = "scripts/build_n8_release_packet.py"

RELEASE_DATE = "2026-07-09"
OFFICIAL_STATUS_CHECK = "2026-07-09"
OFFICIAL_PAGE_LAST_EDITED = "2025-10-27"
ZIP_TIMESTAMP = (2026, 7, 9, 0, 0, 0)
ZIP_FILE_MODE = 0o100644
REPRODUCTION_PYTHON = "3.12.2"
REPRODUCTION_COMMANDS = [
    "python scripts/independent_check_n8_artifacts.py --check --json",
    "python scripts/enumerate_n8_incidence.py --summary",
    "python scripts/analyze_n8_exact_survivors.py --check --json",
    "python scripts/independent_n8_obstruction_recheck.py --check --json",
    "python scripts/check_n8_class14_certificate.py --check --json",
    "python scripts/check_n8_residual_certificates.py --check --json",
    (
        "python scripts/check_n8_survivors_smt.py --assert-clear "
        "--check-artifact data/certificates/n8_survivors_smt.json"
    ),
]


@dataclass(frozen=True)
class Section:
    heading: str
    body: str


NOTE_SECTIONS = [
    Section(
        "Abstract",
        """
        Erdos Problem #97 asks whether every convex polygon has a vertex with
        no other four vertices equidistant from it. This release note packages
        the repository's small-case theorem: no bad strictly convex polygon
        exists with n <= 8. An elementary geometric proof is independently
        corroborated by the selected-witness machine-checked finite-case
        pipeline. The official problem remains falsifiable/open, and external
        review is still requested before paper-style citation.
        """,
    ),
    Section(
        "Status And Scope",
        f"""
        Official/global status: falsifiable/open, rechecked at
        https://www.erdosproblems.com/97 on {OFFICIAL_STATUS_CHECK}; the page
        reports last edited {OFFICIAL_PAGE_LAST_EDITED}. This packet does not
        prove Erdos Problem #97, does not claim a counterexample, and does not
        promote any n=9 or n=10 artifact. It packages the n <= 8 elementary
        proof and selected-witness finite-case evidence for external review.
        """,
    ),
    Section(
        "Elementary Geometric Theorem",
        """
        Theorem. If every vertex of a strictly convex n-gon has four other
        vertices at one common distance, then n >= 9.

        Count apex-marked isosceles triangles. Strict convexity permits at most
        one apex on either side of a base line, and no apex on the base itself;
        therefore T <= n(n-2). Badness gives T >= 6n, excluding n <= 7. In an
        octagon equality saturates every base capacity. Length-2 diagonals then
        force equal side lengths, while every length-3 diagonal forces one of
        two adjacent exterior turns to equal 2*pi/3. These marked turns cover
        the 8-cycle, so at least four are required, contradicting total exterior
        turn 2*pi. The full proof is docs/n8-geometric-proof.md.
        """,
    ),
    Section(
        "Problem And Selected Witnesses",
        """
        A bad polygon would have vertices p_0,...,p_{n-1} such that for every
        center i there are four other vertices at one common distance from
        p_i. Choosing one such 4-set S_i at every center gives the
        selected-witness formulation. Ruling out all selected-witness systems
        for a fixed n rules out bad polygons with that n, because any bad
        polygon supplies at least one selected row at each center.
        """,
    ),
    Section(
        "Lemma Library L1-L10",
        """
        L1. Selected-witness extraction: every bad polygon supplies one
        selected 4-row S_i at each center.

        L2. Two-circle cap: for distinct centers a,b, |S_a cap S_b| <= 2,
        since two distinct circles share at most two points.

        L3. Witness-pair capacity: a fixed unordered witness pair can occur in
        at most two selected rows, because all such centers lie on the
        perpendicular bisector of that pair.

        L4. Crossing-bisector rule: if two rows share exactly two witnesses,
        the center chord is the perpendicular bisector of the common-witness
        chord, and the two chords cross at the midpoint.

        L5. Sharpened count: L2-L4 rule out selected-witness counterexamples
        for n <= 7; the retained n=7 Fano enumeration independently audits the
        equality case.

        L6. n=8 indegree regularity: the witness-pair capacity forces every
        witness label to have selected indegree exactly 4.

        L7. n=8 incidence enumeration: with row 0 fixed to {1,2,3,4} by
        relabeling, exact enumeration leaves 15 canonical survivor classes.

        L8. Forced geometry equations: two-overlap rows generate exact
        perpendicular-bisector equations; selected rows generate exact
        equal-distance equations.

        L9. Survivor obstruction: class 12 has no compatible cyclic order; ten
        classes are killed by rational y_2 span certificates; classes 3, 4, 5,
        and 14 are killed by the named duplicate, collinearity, Groebner, and
        strict-interior certificates.

        L10. Independent cross-checks: a SymPy-free rational recheck covers 11
        classes, and an order-free z3 nonlinear-real-arithmetic replay finds
        all 15 classes UNSAT for strictly convex octagon realization.
        """,
    ),
    Section(
        "Machine-Checked Corroboration",
        """
        The selected-witness pipeline separately excludes n <= 8. L5 handles
        n <= 7. For n=8, L6 reduces the incidence
        layer to regular 4-in/4-out selected-witness systems. L7 exhausts the
        resulting necessary incidence systems and reduces them to 15 canonical
        classes. L8 translates every survivor into exact algebraic and
        cyclic-order constraints. L9 kills all 15 classes with exact checks.
        L10 gives two independent defensive replays. Therefore the repository
        has independent machine-checked finite-case corroboration for n <= 8,
        subject to the stated artifact-review boundary.
        """,
    ),
    Section(
        "Reproduction Commands",
        """
        python scripts/independent_check_n8_artifacts.py --check --json
        python scripts/enumerate_n8_incidence.py --summary
        python scripts/analyze_n8_exact_survivors.py --check --json
        python scripts/independent_n8_obstruction_recheck.py --check --json
        python scripts/check_n8_class14_certificate.py --check --json
        python scripts/check_n8_residual_certificates.py --check --json
        python scripts/check_n8_survivors_smt.py --assert-clear --check-artifact data/certificates/n8_survivors_smt.json
        """,
    ),
    Section(
        "Expected Stable Invariants",
        """
        The incidence enumeration reports 117072 balanced cap matrices with
        row 0 fixed, 4560 forced-perpendicular survivors with row 0 fixed, and
        15 canonical survivor classes. The exact survivor checker rejects all
        15 classes. The SymPy-free recheck kills classes
        0,1,2,6,7,8,9,10,11,12,13 and explicitly leaves 3,4,5,14 to the
        focused Groebner-dependent audit path. The z3 SMT cross-check reports
        all 15 survivor classes UNSAT for strictly convex realization.
        """,
    ),
    Section(
        "Reviewer Boundary",
        """
        The reviewer should check the base-apex and diagonal-chain geometry,
        the row-0 relabeling symmetry break, the exact incidence filters, and
        the exact certificate replays for classes 3, 4, 5, and especially 14.
        A successful external review may support paper-style use of the n <= 8
        theorem and its computational corroboration. It would not update the
        official/global status and would not settle any case n >= 9.
        """,
    ),
]


SUMMARY_SECTIONS = [
    Section(
        "Purpose",
        """
        This packet is ready for an external reviewer to inspect the repo-local
        elementary n <= 8 theorem and selected-witness corroboration. The global
        problem remains open; the request is only to review this small-case
        proof and its finite-case artifact.
        """,
    ),
    Section(
        "What To Review",
        """
        1. The elementary route: base-apex counting, octagon equality
        saturation, equilateral turns, and the C8 vertex-cover contradiction.

        2. The selected-witness incidence route: n <= 7 by counting/crossing,
        n=8 by 15 canonical survivor classes and exact obstruction.

        3. The focused delicate certificates: classes 3, 4, 5, and 14, with
        class 14 the main Groebner plus strict-convexity branch audit.

        4. The independent replays: SymPy-free partial recheck and z3 NRA
        all-class cross-check.
        """,
    ),
    Section(
        "Minimal Commands",
        """
        python scripts/independent_check_n8_artifacts.py --check --json
        python scripts/enumerate_n8_incidence.py --summary
        python scripts/analyze_n8_exact_survivors.py --check --json
        python scripts/check_n8_class14_certificate.py --check --json
        """,
    ),
    Section(
        "Safe Review Outcomes",
        """
        Accepted: the elementary n <= 8 theorem and/or selected-witness
        corroboration are suitable for paper-style citation with stated scope.

        Gap found: record the exact failed lemma, checker, certificate, or
        convention; do not change global status without a separate
        source-of-truth update.
        """,
    ),
]


BUNDLE_SOURCE_FILES = [
    "CITATION.cff",
    "LICENSE.md",
    "LICENSE-CODE.md",
    "LICENSE-DOCS-DATA.md",
    "pyproject.toml",
    "requirements-lock.txt",
    "metadata/erdos97.yaml",
    "docs/n8-proof-trail.md",
    "docs/n8-incidence-enumeration.md",
    "docs/n8-exact-survivors.md",
    "docs/n8-independent-obstruction.md",
    "docs/n8-survivors-smt-cross-check.md",
    "docs/n8-class14-certificate.md",
    "docs/n8-residual-certificates.md",
    "docs/n7-fano-enumeration.md",
    "docs/n8-geometric-proof.md",
    "docs/n8-geometric-proof-audit-2026-07-09.md",
    "docs/dumitrescu-isosceles-n8-shortcut.md",
    "papers/n8-reviewer-packet.md",
    "papers/small-counterexamples-erdos97.md",
    "data/incidence/n8_reconstructed_15_survivors.json",
    "data/incidence/n8_incidence_completeness.json",
    "data/incidence/n8_compatible_orders.json",
    "certificates/n8_exact_analysis.json",
    "certificates/n8_polynomial_systems.txt",
    "data/certificates/n8_survivors_smt.json",
    "scripts/independent_check_n8_artifacts.py",
    "scripts/independent_check_n8_incidence_json.py",
    "scripts/independent_n8_obstruction_recheck.py",
    "scripts/enumerate_n8_incidence.py",
    "scripts/analyze_n8_exact_survivors.py",
    "scripts/check_n8_class14_certificate.py",
    "scripts/check_n8_residual_certificates.py",
    "scripts/check_n8_survivors_smt.py",
    BUILDER_PATH,
    "src/erdos97/__init__.py",
    "src/erdos97/n8_incidence.py",
    "src/erdos97/n8_independent_obstruction.py",
]

BUNDLE_DOCUMENT_FILES = [
    "papers/release/small-counterexamples-erdos97-release.md",
    "papers/release/small-counterexamples-erdos97-release.pdf",
    "papers/release/n8-review-summary.md",
    "papers/release/n8-review-summary.pdf",
]

BUNDLE_README_REFERENCES = [
    "BUNDLE_MANIFEST.json",
    "SHA256SUMS.txt",
    "CITATION.cff",
    "LICENSE.md",
    "LICENSE-CODE.md",
    "LICENSE-DOCS-DATA.md",
    "pyproject.toml",
    "requirements-lock.txt",
    "docs/n8-geometric-proof.md",
    "docs/n8-geometric-proof-audit-2026-07-09.md",
    "papers/release/small-counterexamples-erdos97-release.md",
    "papers/release/small-counterexamples-erdos97-release.pdf",
    "papers/release/n8-review-summary.md",
    "papers/release/n8-review-summary.pdf",
] + [command.split()[1] for command in REPRODUCTION_COMMANDS]


def clean_text(text: str) -> str:
    return "\n".join(line.rstrip() for line in textwrap.dedent(text).strip().splitlines())


def markdown_document(title: str, subtitle: str, sections: Iterable[Section]) -> str:
    parts = [f"# {title}", "", subtitle, ""]
    for section in sections:
        parts.append(f"## {section.heading}")
        parts.append("")
        body = clean_text(section.body)
        if section.heading in {"Reproduction Commands", "Minimal Commands"}:
            parts.extend(["```bash", body, "```"])
        else:
            parts.append(body)
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def make_pdf(path: Path, title: str, subtitle: str, sections: list[Section]) -> None:
    try:
        from reportlab import rl_config
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            Paragraph,
            Preformatted,
            SimpleDocTemplate,
            Spacer,
            Table,
        )
    except ImportError as exc:  # pragma: no cover - depends on local tooling.
        raise SystemExit("reportlab is required to build release PDFs") from exc

    rl_config.invariant = 1
    path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReleaseTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReleaseSubtitle",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#333333"),
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReleaseHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            spaceBefore=8,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReleaseBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=12.2,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReleaseCode",
            parent=styles["Code"],
            fontName="Courier",
            fontSize=7.4,
            leading=8.8,
            leftIndent=0.32 * inch,
            spaceAfter=6,
        )
    )

    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=0.72 * inch,
        rightMargin=0.72 * inch,
        topMargin=0.62 * inch,
        bottomMargin=0.62 * inch,
        title=title,
        author="davidiach/erdos97",
    )
    story = [
        