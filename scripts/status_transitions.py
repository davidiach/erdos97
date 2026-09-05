"""Evidence-bound status transitions, not a proof verifier or review authority.

The optional proposal is inactive unless every referenced artifact and the
recorded independent acceptance match. A maintainer still has to authenticate
that review; a JSON assertion cannot establish a reviewer's independence.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

TRANSITION_PATH = "metadata/status_transition.json"
STATUS_FILES = {"README.md", "STATE.md", "RESULTS.md", "docs/claims.md"}
LOCAL_FIELDS = ("overall_claim", "strongest_result", "strongest_result_proof",
                "strongest_result_review_status")
OFFICIAL_FIELDS = ("official_status", "official_status_last_checked", "official_page")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(f"status transition: {message}")


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def load_object(data: bytes, label: str) -> dict[str, Any]:
    result = json.loads(data)
    require(isinstance(result, dict), f"{label} must be an object")
    return result


def checked_artifact(root: Path, reference: object) -> bytes:
    require(isinstance(reference, dict), "artifact reference must be an object")
    rel = reference.get("path")
    digest = reference.get("sha256")
    require(nonempty(rel) and nonempty(digest), "artifact needs path and sha256")
    path = Path(rel)
    require(not path.is_absolute() and ".." not in path.parts, "artifact path must be repo-relative")
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root.resolve()), "artifact escapes the repository")
    require(resolved.is_file(), f"missing artifact {rel}")
    data = resolved.read_bytes()
    require(bool(data), f"empty artifact {rel}")
    require(hashlib.sha256(data).hexdigest() == digest, f"artifact hash mismatch: {rel}")
    return data


def proposal_digest(proposal: dict[str, Any]) -> str:
    content = {key: value for key, value in proposal.items() if key != "review"}
    encoded = json.dumps(content, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def checked_date(value: object, label: str) -> date:
    require(isinstance(value, str) and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)),
            f"{label} must be YYYY-MM-DD")
    parsed = date.fromisoformat(value)
    require(parsed <= date.today(), f"{label} is in the future")
    return parsed


def load_reviewed_transition(root: Path) -> dict[str, Any] | None:
    path = root / TRANSITION_PATH
    if not path.exists():
        return None
    proposal = load_object(path.read_bytes(), TRANSITION_PATH)
    require(proposal.get("schema") == 1, "unsupported schema")
    kind = proposal.get("local_claim")
    require(kind in {"none", "proof", "counterexample"}, "invalid local_claim")
    bound = proposal.get("finite_bound")
    require(bound is None or (type(bound) is int and bound >= 1), "invalid finite_bound")
    require(kind != "none" or bound is not None, "a finite-only transition needs finite_bound")
    local = proposal.get("local_repo")
    official = proposal.get("problem")
    require(isinstance(local, dict) and all(nonempty(local.get(k)) for k in LOCAL_FIELDS),
            "local_repo must supply the exact reviewed metadata fields")
    require(isinstance(official, dict) and all(nonempty(official.get(k)) for k in OFFICIAL_FIELDS),
            "problem must supply separate externally checked status fields")
    checked_date(official["official_status_last_checked"], "official status date")
    if kind == "none":
        require(bool(re.search(rf"\bn\s*<=\s*{bound}\b", local["strongest_result"])),
                "strongest_result must state the reviewed finite_bound")

    evidence = proposal.get("evidence")
    require(isinstance(evidence, dict), "evidence must be an object")
    checked_artifact(root, evidence.get("proof"))
    require(local["strongest_result_proof"] == evidence["proof"]["path"],
            "strongest_result_proof must name the checked proof")
    verification = load_object(checked_artifact(root, evidence.get("verification")), "verification")
    require(verification.get("status") == "passed", "verification has not passed")
    require(verification.get("proof_sha256") == evidence["proof"]["sha256"],
            "verification is not bound to this proof")
    methods = {"exact_certificate", "formal_proof", "paper_review"}
    if kind == "counterexample":
        methods.remove("paper_review")
    require(verification.get("method") in methods, "verification method is insufficient")
    require(nonempty(verification.get("details")), "verification needs details")
    source = load_object(checked_artifact(root, evidence.get("official_source")), "official source")
    require(all(source.get(k) == official[k] for k in OFFICIAL_FIELDS),
            "official status must match its separate source record")

    review = load_object(checked_artifact(root, proposal.get("review")), "review")
    require(review.get("decision") == "accepted" and review.get("independent") is True,
            "recorded independent acceptance is required; pending review cannot promote")
    require(nonempty(review.get("reviewer")), "review must identify its reviewer")
    require(nonempty(review.get("review_url")), "review must give a provenance URL")
    checked_date(review.get("reviewed_on"), "review date")
    require(review.get("proposal_sha256") == proposal_digest(proposal),
            "review is not bound to this exact proposal and evidence")

    approved = proposal.get("approved_statements", {})
    require(isinstance(approved, dict) and set(approved) <= STATUS_FILES,
            "approved_statements may only address proof-facing status files")
    require(kind != "none" or not approved,
            "finite-only transitions cannot exempt global proof/counterexample statements")
    for statements in approved.values():
        require(isinstance(statements, list) and all(nonempty(s) for s in statements),
                "approved statements must be nonempty literal paragraphs")
    return proposal


def validate_transition_metadata(proposal: dict[str, Any], metadata: dict[str, Any]) -> None:
    for section, fields in (("problem", OFFICIAL_FIELDS), ("local_repo", LOCAL_FIELDS)):
        actual = metadata.get(section)
        require(isinstance(actual, dict), f"metadata {section} is missing")
        for field in fields:
            require(actual.get(field) == proposal[section][field],
                    f"metadata {section}.{field} differs from the reviewed proposal")


def remove_approved_paragraphs(text: str, label: str, proposal: dict[str, Any]) -> str:
    """Exempt complete reviewed paragraphs only, never substrings or regexes."""
    approved = {" ".join(s.split()) for s in proposal.get("approved_statements", {}).get(label, [])}
    return "".join(
        "\n" * block.count("\n") if " ".join(block.split()) in approved else block
        for block in re.split(r"(\n\s*\n)", text)
    )
