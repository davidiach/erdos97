#!/usr/bin/env python3
"""Build the n <= 8 reviewer release packet.

The release packet is generated into ``papers/release`` so the polished note,
one-page reviewer summary, PDF renderings, and checksum bundle stay
reproducible from one command.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import textwrap
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = ROOT / "papers" / "release"
BUNDLE_STAGING_DIR = ROOT / "tmp" / "n8-artifact-bundle"
BUNDLE_ROOT = BUNDLE_STAGING_DIR / "erdos97-n8-release"
ZIP_PATH = RELEASE_DIR / "n8-artifact-bundle.zip"
BUNDLE_MANIFEST_PATH = RELEASE_DIR / "n8-artifact-bundle-manifest.json"
BUNDLE_CHECKSUMS_PATH = RELEASE_DIR / "n8-artifact-bundle-SHA256SUMS.txt"

RELEASE_DATE = "2026-07-02"
OFFICIAL_STATUS_CHECK = "2026-07-02"
OFFICIAL_PAGE_LAST_EDITED = "2025-10-27"
ZIP_TIMESTAMP = (2026, 7, 2, 0, 0, 0)


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
        the repository's small-case result: in the selected-witness formulation
        there is no strictly convex counterexample with n <= 8, in the
        repo-local machine-checked finite-case sense. The official problem
        remains falsifiable/open, and independent review is still requested
        before paper-style or public theorem-style use.
        """,
    ),
    Section(
        "Status And Scope",
        f"""
        Official/global status: falsifiable/open, rechecked at
        https://www.erdosproblems.com/97 on {OFFICIAL_STATUS_CHECK}; the page
        reports last edited {OFFICIAL_PAGE_LAST_EDITED}. This packet does not
        prove Erdos Problem #97, does not claim a counterexample, and does not
        promote any n=9 or n=10 artifact. It isolates the n <= 8 selected-witness
        finite-case evidence for external review.
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
        "Finite-Case Theorem Under Review",
        """
        Claim under review. In the selected-witness formulation, no strictly
        convex counterexample exists for n <= 8.

        Proof sketch. L5 excludes n <= 7. For n=8, L6 reduces the incidence
        layer to regular 4-in/4-out selected-witness systems. L7 exhausts the
        resulting necessary incidence systems and reduces them to 15 canonical
        classes. L8 translates every survivor into exact algebraic and
        cyclic-order constraints. L9 kills all 15 classes with exact checks.
        L10 gives two independent defensive replays. Therefore the repository
        has a machine-checked finite-case artifact for n <= 8, subject to the
        stated review boundary.
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
        The reviewer should check the geometric lemmas, the row-0 relabeling
        symmetry break, the exact incidence filters, and the exact certificate
        replays for classes 3, 4, 5, and especially 14. A successful review may
        support paper-style use of the n <= 8 finite-case result. It would not
        update the official/global status and would not settle any case n >= 9.
        """,
    ),
]


SUMMARY_SECTIONS = [
    Section(
        "Purpose",
        """
        This packet is ready for an external reviewer to inspect the repo-local
        selected-witness n <= 8 result for Erdos Problem #97. The global problem
        remains open; the request is only to review the small finite-case
        artifact and the short human-readable proof trail.
        """,
    ),
    Section(
        "What To Review",
        """
        1. The selected-witness incidence route: n <= 7 by counting/crossing,
        n=8 by 15 canonical survivor classes and exact obstruction.

        2. The focused delicate certificates: classes 3, 4, 5, and 14, with
        class 14 the main Groebner plus strict-convexity branch audit.

        3. The independent replays: SymPy-free partial recheck and z3 NRA
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
        Accepted: the repo-local n <= 8 selected-witness finite-case artifact is
        suitable for paper-style citation with the stated scope.

        Gap found: record the exact failed lemma, checker, certificate, or
        convention; do not change global status without a separate
        source-of-truth update.
        """,
    ),
]


BUNDLE_FILES = [
    "README.md",
    "STATE.md",
    "RESULTS.md",
    "pyproject.toml",
    "requirements-lock.txt",
    "metadata/erdos97.yaml",
    "docs/claims.md",
    "docs/n8-proof-trail.md",
    "docs/n8-incidence-enumeration.md",
    "docs/n8-exact-survivors.md",
    "docs/n8-independent-obstruction.md",
    "docs/n8-survivors-smt-cross-check.md",
    "docs/n8-class14-certificate.md",
    "docs/n8-residual-certificates.md",
    "docs/n7-fano-enumeration.md",
    "docs/n8-geometric-proof.md",
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
]


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
        Paragraph(title, styles["ReleaseTitle"]),
        Paragraph(subtitle, styles["ReleaseSubtitle"]),
        Table(
            [
                ["Status", "Repo-local n <= 8 finite-case release packet"],
                ["Global status", "Falsifiable/open; no general proof or counterexample claimed"],
                ["Date", RELEASE_DATE],
            ],
            colWidths=[1.25 * inch, 5.45 * inch],
            hAlign="LEFT",
            style=[
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#888888")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eeeeee")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ],
        ),
        Spacer(1, 8),
    ]

    for section in sections:
        story.append(Paragraph(section.heading, styles["ReleaseHeading"]))
        for block in clean_text(section.body).split("\n\n"):
            if "\n" in block and block.lstrip().startswith("python "):
                wrapped = "\n".join(
                    wrapped_line
                    for line in block.splitlines()
                    for wrapped_line in (
                        textwrap.wrap(
                            line,
                            width=88,
                            subsequent_indent="    ",
                            break_long_words=False,
                            break_on_hyphens=False,
                        )
                        or [""]
                    )
                )
                story.append(Preformatted(wrapped, styles["ReleaseCode"]))
            else:
                story.append(Paragraph(block.replace("\n", " "), styles["ReleaseBody"]))

    def footer(canvas, _doc) -> None:  # type: ignore[no-untyped-def]
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(0.72 * inch, 0.38 * inch, "davidiach/erdos97 n <= 8 release packet")
        canvas.drawRightString(7.78 * inch, 0.38 * inch, f"Page {_doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def copy_bundle_files() -> list[dict[str, object]]:
    if BUNDLE_ROOT.exists():
        shutil.rmtree(BUNDLE_ROOT)
    BUNDLE_ROOT.mkdir(parents=True)
    records: list[dict[str, object]] = []

    for rel in BUNDLE_FILES:
        src = ROOT / rel
        if not src.exists():
            raise SystemExit(f"missing bundle input: {rel}")
        dst = BUNDLE_ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        records.append(
            {
                "path": rel,
                "size_bytes": dst.stat().st_size,
                "sha256": sha256_file(dst),
            }
        )

    src_root = ROOT / "src" / "erdos97"
    for src in sorted(src_root.rglob("*.py")):
        rel = src.relative_to(ROOT).as_posix()
        dst = BUNDLE_ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        records.append(
            {
                "path": rel,
                "size_bytes": dst.stat().st_size,
                "sha256": sha256_file(dst),
            }
        )

    records.sort(key=lambda item: str(item["path"]))
    return records


def write_bundle_manifest(records: list[dict[str, object]]) -> None:
    manifest = {
        "schema": "erdos97.n8_release_bundle.v1",
        "release_date": RELEASE_DATE,
        "official_status_check": OFFICIAL_STATUS_CHECK,
        "claim_scope": (
            "Repo-local selected-witness n <= 8 finite-case release packet; "
            "not a proof of Erdos Problem #97 and not a counterexample."
        ),
        "reproduction_commands": [
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
        ],
        "files": records,
    }
    write_text(BUNDLE_ROOT / "BUNDLE_MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
    checksum_lines = [
        f"{record['sha256']}  {record['path']}"
        for record in records
    ]
    checksum_lines.append(f"{sha256_file(BUNDLE_ROOT / 'BUNDLE_MANIFEST.json')}  BUNDLE_MANIFEST.json")
    write_text(BUNDLE_ROOT / "SHA256SUMS.txt", "\n".join(checksum_lines) + "\n")
    shutil.copy2(BUNDLE_ROOT / "BUNDLE_MANIFEST.json", BUNDLE_MANIFEST_PATH)
    shutil.copy2(BUNDLE_ROOT / "SHA256SUMS.txt", BUNDLE_CHECKSUMS_PATH)


def zip_bundle() -> None:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(BUNDLE_ROOT.rglob("*")):
            if path.is_file():
                info = zipfile.ZipInfo(
                    path.relative_to(BUNDLE_ROOT.parent).as_posix(),
                    date_time=ZIP_TIMESTAMP,
                )
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                archive.writestr(info, path.read_bytes())


def write_release_checksums() -> None:
    paths = [
        RELEASE_DIR / "small-counterexamples-erdos97-release.md",
        RELEASE_DIR / "small-counterexamples-erdos97-release.pdf",
        RELEASE_DIR / "n8-review-summary.md",
        RELEASE_DIR / "n8-review-summary.pdf",
        BUNDLE_MANIFEST_PATH,
        BUNDLE_CHECKSUMS_PATH,
        ZIP_PATH,
        RELEASE_DIR / "README.md",
    ]
    lines = [f"{sha256_file(path)}  {path.relative_to(RELEASE_DIR).as_posix()}" for path in paths]
    write_text(RELEASE_DIR / "SHA256SUMS.txt", "\n".join(lines) + "\n")


def main() -> int:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    stale_expanded_bundle = RELEASE_DIR / "n8-artifact-bundle"
    if stale_expanded_bundle.exists():
        shutil.rmtree(stale_expanded_bundle)
    note_subtitle = (
        "Self-contained reviewer release note. Source-of-truth status remains "
        "README.md, STATE.md, RESULTS.md, docs/claims.md, and metadata/erdos97.yaml."
    )
    summary_subtitle = (
        "One-page external-review summary for the repo-local selected-witness "
        "n <= 8 finite-case artifact."
    )

    write_text(
        RELEASE_DIR / "small-counterexamples-erdos97-release.md",
        markdown_document(
            "Small Counterexamples To Erdos Problem 97: n <= 8 Release Note",
            note_subtitle,
            NOTE_SECTIONS,
        ),
    )
    write_text(
        RELEASE_DIR / "n8-review-summary.md",
        markdown_document("n <= 8 Review Summary", summary_subtitle, SUMMARY_SECTIONS),
    )
    make_pdf(
        RELEASE_DIR / "small-counterexamples-erdos97-release.pdf",
        "Small Counterexamples To Erdos Problem 97",
        note_subtitle,
        NOTE_SECTIONS,
    )
    make_pdf(
        RELEASE_DIR / "n8-review-summary.pdf",
        "n <= 8 Review Summary",
        summary_subtitle,
        SUMMARY_SECTIONS,
    )

    records = copy_bundle_files()
    write_bundle_manifest(records)
    zip_bundle()
    shutil.rmtree(BUNDLE_STAGING_DIR)
    write_text(
        RELEASE_DIR / "README.md",
        clean_text(
            f"""
            # n <= 8 Release Packet

            Status: generated reviewer release packet; not mathematical evidence
            by itself.

            Generated by:

            ```bash
            python scripts/build_n8_release_packet.py
            ```

            Contents:

            - `small-counterexamples-erdos97-release.md` and `.pdf`: compact
              self-contained reviewer note for the repo-local selected-witness
              `n <= 8` finite-case artifact.
            - `n8-review-summary.md` and `.pdf`: one-page external-review
              summary suitable for email.
            - `n8-artifact-bundle-manifest.json`: copied source, script,
              document, and certificate inputs included in the reproducibility
              bundle, with sizes and SHA-256 hashes.
            - `n8-artifact-bundle-SHA256SUMS.txt`: plain-text checksums for
              the files inside the reproducibility bundle.
            - `n8-artifact-bundle.zip`: zipped reproducibility bundle.
            - `SHA256SUMS.txt`: release-level checksums.

            Official/global status remains falsifiable/open, rechecked from
            https://www.erdosproblems.com/97 on {OFFICIAL_STATUS_CHECK}. No
            general proof and no counterexample are claimed.
            """
        )
        + "\n",
    )
    write_release_checksums()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
