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


def sha256_records(records: Sequence[dict[str, object]]) -> str:
    digest = hashlib.sha256()
    for record in sorted(records, key=lambda item: str(item["path"])):
        digest.update(str(record["path"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(record["sha256"]).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def file_record(path: Path, relative_path: str) -> dict[str, object]:
    return {
        "path": relative_path,
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def git_output(*args: str, text: bool = True) -> str | bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=text,
    )
    return completed.stdout.strip() if text else completed.stdout


def require_clean_worktree() -> None:
    status = str(git_output("status", "--porcelain=v1", "--untracked-files=all"))
    if status:
        raise SystemExit(
            "release generation/checking requires a clean Git worktree; "
            f"found:\n{status}"
        )


def git_file_bytes(commit: str, relative_path: str) -> bytes:
    try:
        return bytes(git_output("show", f"{commit}:{relative_path}", text=False))
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            f"source commit {commit} does not contain {relative_path}"
        ) from exc


def commit_object_available(commit: str) -> bool:
    """Whether ``commit`` can be resolved in this clone.

    The recorded source commit can be legitimately absent: shallow CI
    checkouts do not fetch ancestors, and a squash-merge rewrites the
    branch history that contained it. Its snapshot is then verified
    against HEAD instead of the recorded commit.
    """
    try:
        git_output("rev-parse", "--verify", "--quiet", f"{commit}^{{commit}}")
    except subprocess.CalledProcessError:
        return False
    return True


def current_source_records() -> list[dict[str, object]]:
    if len(BUNDLE_SOURCE_FILES) != len(set(BUNDLE_SOURCE_FILES)):
        raise SystemExit("BUNDLE_SOURCE_FILES contains duplicate paths")
    records = []
    for relative_path in BUNDLE_SOURCE_FILES:
        path = ROOT / relative_path
        if not path.is_file():
            raise SystemExit(f"missing bundle input: {relative_path}")
        records.append(file_record(path, relative_path))
    return sorted(records, key=lambda item: str(item["path"]))


def load_manifest(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read release manifest {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"release manifest must be an object: {path}")
    return payload


def recorded_source_commit(manifest: dict[str, object]) -> str:
    source = manifest.get("source")
    if not isinstance(source, dict) or not isinstance(source.get("commit"), str):
        raise SystemExit("existing release manifest has no source.commit")
    return source["commit"]


def resolve_source_provenance(
    source_ref: str | None,
    *,
    release_dir: Path = RELEASE_DIR,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    require_clean_worktree()
    source_records = current_source_records()
    builder_sha256 = sha256_file(ROOT / BUILDER_PATH)
    manifest_path = release_dir / BUNDLE_MANIFEST_NAME

    def build_source_object(commit: str, tree: str) -> dict[str, object]:
        return {
            "repository_url": REPOSITORY_URL,
            "commit": commit,
            "tree": tree,
            "commit_url": f"{REPOSITORY_URL}/commit/{commit}",
            "builder": {"path": BUILDER_PATH, "sha256": builder_sha256},
            "bundle_source_files_sha256": sha256_records(source_records),
            "worktree": {
                "dirty": False,
                "policy": (
                    "Build and check require a clean Git worktree. Generated release "
                    "outputs are committed after, and are not part of, the named "
                    "source snapshot."
                ),
            },
        }

    if source_ref is None:
        if not manifest_path.is_file():
            raise SystemExit(
                "no recorded source snapshot; rerun with --source-ref HEAD "
                "from the clean source commit"
            )
        existing = load_manifest(manifest_path)
        source = existing.get("source")
        if not isinstance(source, dict):
            raise SystemExit("existing release manifest has no source object")
        builder = source.get("builder")
        if not isinstance(builder, dict) or builder.get("sha256") != builder_sha256:
            raise SystemExit(
                "builder differs from the recorded source snapshot; commit the "
                "source changes, then rebuild with --source-ref HEAD"
            )
        commit = recorded_source_commit(existing)
        if not commit_object_available(commit):
            recorded_tree = source.get("tree")
            if not isinstance(recorded_tree, str) or not recorded_tree:
                raise SystemExit("existing release manifest has no source.tree")
            recorded_records_sha256 = source.get("bundle_source_files_sha256")
            if sha256_records(source_records) != recorded_records_sha256:
                raise SystemExit(
                    "bundle source files changed since the recorded source "
                    f"snapshot {commit}; rebuild with --source-ref HEAD from "
                    "the clean source commit"
                )
            print(
                f"note: recorded source commit {commit} is not present in "
                "this clone (shallow checkout or squash-merged branch); "
                "verified the recorded source snapshot against HEAD instead",
                file=sys.stderr,
            )
            return build_source_object(commit, recorded_tree), source_records
    else:
        commit = str(git_output("rev-parse", f"{source_ref}^{{commit}}"))

    tree = str(git_output("rev-parse", f"{commit}^{{tree}}"))
    for record in source_records:
        relative_path = str(record["path"])
        committed_sha256 = hashlib.sha256(
            git_file_bytes(commit, relative_path)
        ).hexdigest()
        if committed_sha256 != record["sha256"]:
            raise SystemExit(
                f"{relative_path} does not match source commit {commit}; "
                "commit source inputs before building"
            )

    return build_source_object(commit, tree), source_records


def dependency_snapshot() -> dict[str, object]:
    lock_path = ROOT / "requirements-lock.txt"
    dependencies = []
    for line in lock_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([^\s]+)", stripped)
        if not match:
            raise SystemExit(f"unsupported requirements-lock entry: {stripped}")
        dependencies.append({"name": match.group(1), "version": match.group(2)})

    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    requires_match = re.search(r'^requires-python\s*=\s*"([^"]+)"', pyproject, re.M)
    if not requires_match:
        raise SystemExit("pyproject.toml has no requires-python field")
    return {
        "snapshot_kind": "declared_reproduction_environment",
        "python": {
            "implementation": "CPython",
            "version": REPRODUCTION_PYTHON,
            "requires_python": requires_match.group(1),
        },
        "platform": {
            "supported_hosts": ["Linux", "macOS", "Windows"],
            "archive_paths": "POSIX",
            "archive_compression": "stored",
            "host_specific_metadata": "excluded",
        },
        "lockfile": {
            "path": "requirements-lock.txt",
            "sha256": sha256_file(lock_path),
        },
        "dependencies": dependencies,
    }


def bundle_readme(source: dict[str, object]) -> str:
    return clean_text(
        f"""
        # Erdős Problem 97: n <= 8 Review Bundle

        This is the self-contained review bundle for the repository-local
        elementary `n <= 8` theorem and its selected-witness finite-case
        corroboration. It does not prove Erdős Problem #97 and does not claim
        a counterexample. The global problem remains open.

        Repository: {REPOSITORY_URL}

        Source commit: `{source['commit']}`

        The compact release note is
        `papers/release/small-counterexamples-erdos97-release.md` (also supplied
        as `papers/release/small-counterexamples-erdos97-release.pdf`). The
        one-page summary is `papers/release/n8-review-summary.md` (also supplied
        as `papers/release/n8-review-summary.pdf`). The shortest human proof is
        `docs/n8-geometric-proof.md`; its repository review record is
        `docs/n8-geometric-proof-audit-2026-07-09.md`.

        ## Integrity

        `BUNDLE_MANIFEST.json` records the source commit/tree, builder digest,
        declared Python/dependency environment, and every bundled file digest.
        `SHA256SUMS.txt` is the plain-text checksum list.

        ## Reproduction environment

        Use CPython {REPRODUCTION_PYTHON}. Install the pinned snapshot and this
        package without resolving newer dependencies:

        ```bash
        python -m pip install -r requirements-lock.txt
        python -m pip install -e . --no-deps
        ```

        Run the following commands from this directory:

        ```bash
        {chr(10).join(REPRODUCTION_COMMANDS)}
        ```

        Citation metadata is in `CITATION.cff`. The split license and complete
        license texts are `LICENSE.md`, `LICENSE-CODE.md`, and
        `LICENSE-DOCS-DATA.md`.
        """
    ) + "\n"


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def copy_bundle_files(
    bundle_root: Path,
    release_dir: Path,
    source: dict[str, object],
) -> list[dict[str, object]]:
    bundle_root.mkdir(parents=True)
    for relative_path in BUNDLE_SOURCE_FILES:
        copy_file(ROOT / relative_path, bundle_root / relative_path)
    for relative_path in BUNDLE_DOCUMENT_FILES:
        copy_file(release_dir / Path(relative_path).name, bundle_root / relative_path)
    write_text(bundle_root / "README.md", bundle_readme(source))

    for relative_path in BUNDLE_README_REFERENCES:
        if relative_path in {"BUNDLE_MANIFEST.json", "SHA256SUMS.txt"}:
            continue
        if not (bundle_root / relative_path).is_file():
            raise SystemExit(f"bundle README references missing file: {relative_path}")

    paths = [path for path in bundle_root.rglob("*") if path.is_file()]
    return sorted(
        [file_record(path, path.relative_to(bundle_root).as_posix()) for path in paths],
        key=lambda item: str(item["path"]),
    )


def write_bundle_manifest(
    bundle_root: Path,
    release_dir: Path,
    records: list[dict[str, object]],
    source: dict[str, object],
) -> None:
    manifest = {
        "schema": "erdos97.n8_release_bundle.v2",
        "release_date": RELEASE_DATE,
        "official_status_check": OFFICIAL_STATUS_CHECK,
        "claim_scope": (
            "Repo-local elementary n <= 8 theorem and selected-witness "
            "finite-case corroboration; not a proof of Erdos Problem #97 "
            "and not a counterexample."
        ),
        "source": source,
        "environment": dependency_snapshot(),
        "reproduction_commands": REPRODUCTION_COMMANDS,
        "files": records,
    }
    manifest_text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    write_text(bundle_root / "BUNDLE_MANIFEST.json", manifest_text)
    checksum_lines = [f"{record['sha256']}  {record['path']}" for record in records]
    checksum_lines.append(
        f"{sha256_file(bundle_root / 'BUNDLE_MANIFEST.json')}  BUNDLE_MANIFEST.json"
    )
    checksum_text = "\n".join(checksum_lines) + "\n"
    write_text(bundle_root / "SHA256SUMS.txt", checksum_text)
    write_text(release_dir / BUNDLE_MANIFEST_NAME, manifest_text)
    write_text(release_dir / BUNDLE_CHECKSUMS_NAME, checksum_text)


def canonical_zip_members(bundle_root: Path) -> list[tuple[str, Path]]:
    members = [
        (
            f"{BUNDLE_DIRECTORY_NAME}/{path.relative_to(bundle_root).as_posix()}",
            path,
        )
        for path in bundle_root.rglob("*")
        if path.is_file()
    ]
    return sorted(members, key=lambda item: item[0])


def zip_bundle(bundle_root: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.comment = b""
        for member_name, path in canonical_zip_members(bundle_root):
            info = zipfile.ZipInfo(member_name, date_time=ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.create_version = 20
            info.extract_version = 20
            info.flag_bits = 0
            info.internal_attr = 0
            info.external_attr = ZIP_FILE_MODE << 16
            info.extra = b""
            info.comment = b""
            archive.writestr(info, path.read_bytes())


def write_release_checksums(release_dir: Path) -> None:
    names = [name for name in RELEASE_OUTPUT_NAMES if name != "SHA256SUMS.txt"]
    lines = [f"{sha256_file(release_dir / name)}  {name}" for name in names]
    write_text(release_dir / "SHA256SUMS.txt", "\n".join(lines) + "\n")


def build_release(
    release_dir: Path,
    staging_dir: Path,
    source: dict[str, object],
) -> None:
    release_dir.mkdir(parents=True)
    note_subtitle = (
        "Self-contained reviewer release note. Source-of-truth status remains "
        "README.md, STATE.md, RESULTS.md, docs/claims.md, and metadata/erdos97.yaml."
    )
    summary_subtitle = (
        "One-page external-review summary for the repo-local elementary n <= 8 "
        "theorem and selected-witness corroboration."
    )

    write_text(
        release_dir / "small-counterexamples-erdos97-release.md",
        markdown_document(
            "Small Counterexamples To Erdos Problem 97: n <= 8 Release Note",
            note_subtitle,
            NOTE_SECTIONS,
        ),
    )
    write_text(
        release_dir / "n8-review-summary.md",
        markdown_document("n <= 8 Review Summary", summary_subtitle, SUMMARY_SECTIONS),
    )
    make_pdf(
        release_dir / "small-counterexamples-erdos97-release.pdf",
        "Small Counterexamples To Erdos Problem 97",
        note_subtitle,
        NOTE_SECTIONS,
    )
    make_pdf(
        release_dir / "n8-review-summary.pdf",
        "n <= 8 Review Summary",
        summary_subtitle,
        SUMMARY_SECTIONS,
    )

    bundle_root = staging_dir / BUNDLE_DIRECTORY_NAME
    records = copy_bundle_files(bundle_root, release_dir, source)
    write_bundle_manifest(bundle_root, release_dir, records, source)
    zip_bundle(bundle_root, release_dir / ZIP_NAME)
    write_text(release_dir / "README.md", release_readme(source))
    write_release_checksums(release_dir)


def release_readme(source: dict[str, object]) -> str:
    return clean_text(
        f"""
        # n <= 8 Release Packet

        Status: generated reviewer release packet; not mathematical evidence
        by itself.

        Generated from source commit `{source['commit']}` (tree
        `{source['tree']}`) in {REPOSITORY_URL}. To rebuild it from that clean
        source snapshot:

        ```bash
        git checkout {source['commit']}
        python scripts/build_n8_release_packet.py --source-ref HEAD
        ```

        To verify these generated files without modifying the checkout:

        ```bash
        python scripts/build_n8_release_packet.py --check
        ```

        `{ZIP_NAME}` is a self-contained platform-neutral review bundle with
        its own README, licenses, citation metadata, code, and certificates.
        `{BUNDLE_MANIFEST_NAME}` records source and environment provenance;
        `{BUNDLE_CHECKSUMS_NAME}` and `SHA256SUMS.txt` record file integrity.

        Official/global status remains falsifiable/open, rechecked from
        https://www.erdosproblems.com/97 on {OFFICIAL_STATUS_CHECK}. No general
        proof and no counterexample are claimed.
        """
    ) + "\n"


def compare_release(expected_dir: Path, actual_dir: Path) -> list[str]:
    mismatches = []
    for name in RELEASE_OUTPUT_NAMES:
        expected = expected_dir / name
        actual = actual_dir / name
        if not actual.is_file():
            mismatches.append(f"missing: {name}")
        elif expected.read_bytes() != actual.read_bytes():
            mismatches.append(
                f"stale: {name} (expected {sha256_file(expected)}, "
                f"found {sha256_file(actual)})"
            )
    return mismatches


def install_release(expected_dir: Path, actual_dir: Path) -> None:
    actual_dir.mkdir(parents=True, exist_ok=True)
    for name in RELEASE_OUTPUT_NAMES:
        copy_file(expected_dir / name, actual_dir / name)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="rebuild temporarily and compare without changing the checkout",
    )
    parser.add_argument(
        "--source-ref",
        help="clean committed source ref to record (normally HEAD)",
    )
    args = parser.parse_args(argv)
    if args.check and args.source_ref:
        parser.error("--check cannot be combined with --source-ref")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    source, _source_records = resolve_source_provenance(args.source_ref)
    with tempfile.TemporaryDirectory(prefix="erdos97-n8-release-") as temporary:
        temporary_root = Path(temporary)
        expected_dir = temporary_root / "release"
        build_release(expected_dir, temporary_root / "bundle", source)
        if args.check:
            mismatches = compare_release(expected_dir, RELEASE_DIR)
            if mismatches:
                print("n <= 8 release packet is stale:", file=sys.stderr)
                for mismatch in mismatches:
                    print(f"- {mismatch}", file=sys.stderr)
                return 1
            print("n <= 8 release packet is current")
            return 0
        install_release(expected_dir, RELEASE_DIR)
        print(
            f"wrote n <= 8 release packet from {source['commit']} "
            f"to {RELEASE_DIR.relative_to(ROOT)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
