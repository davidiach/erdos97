from __future__ import annotations

import sys
from pathlib import Path

from scripts.run_artifact_audit import AuditCommand, run_audit_command, sha256_bytes


def test_sha256_bytes_is_stable() -> None:
    assert sha256_bytes(b"erdos97\n") == "d804cace0801472174f9f279439ba930de0123adced9367f0df1dcc8dc996d4b"


def test_run_audit_command_records_metadata(tmp_path: Path) -> None:
    command = AuditCommand(
        ident="smoke",
        command=(sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'ok\\n')"),
        claim_scope="test command only",
    )

    record = run_audit_command(command, tmp_path)

    assert record["id"] == "smoke"
    assert record["exit_code"] == 0
    assert record["claim_scope"] == "test command only"
    assert record["stdout_bytes"] == len(b"ok\n")
    assert (tmp_path / record["stdout_path"]).read_bytes() == b"ok\n"
    assert (tmp_path / record["stderr_path"]).read_bytes() == b""
    assert len(record["combined_output_sha256"]) == 64
