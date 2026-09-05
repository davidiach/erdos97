from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_docs_index_coverage import (  # noqa: E402
    documentation_files,
    index_link_targets,
    main,
)

DOCS_ROOT = ROOT / "docs"


def test_index_links_every_documentation_file() -> None:
    assert main() == 0


def test_index_does_not_list_itself() -> None:
    covered = {path.relative_to(DOCS_ROOT).as_posix() for path in documentation_files()}
    assert "index.md" not in covered


def test_documentation_files_are_markdown_or_html() -> None:
    suffixes = {path.suffix for path in documentation_files()}
    assert suffixes <= {".html", ".md"}
    assert suffixes


def test_index_link_targets_skip_external_and_anchor_links() -> None:
    text = (
        "- [a](a.md)\n"
        "- [b](https://example.com/b.md)\n"
        "- [c](mailto:someone@example.com)\n"
        "- [d](#section)\n"
        "- [e](e.md#section)\n"
    )
    assert index_link_targets(text) == ["a.md", "e.md"]


def test_reference_titled_and_encoded_links() -> None:
    text = (
        '[Inline](<notes with spaces.md> "title")\n'
        '[Reference][note]\n\n'
        '[note]: nested/note.md#section "title"\n\n'
        '[Encoded](note%23one.md?view=1#section)\n'
        '[External](//example.com/note.md)\n'
    )
    assert index_link_targets(text) == [
        'notes with spaces.md', 'nested/note.md', 'note#one.md',
    ]


def test_examples_comments_and_images_are_not_navigation() -> None:
    text = (
        '<!-- [Hidden](comment.md) -->\n\n'
        'Text <!-- [Hidden](inline-comment.md) --> text\n\n'
        '```markdown\n[Example](fenced.md)\n```\n\n'
        '~~~\n[Example](tilde-fenced.md)\n~~~\n\n'
        '    [Example](indented.md)\n\n'
        '`[Example](code.md)`\n\n'
        '![Image](image.md)\n\n'
        '[Visible](visible.md)\n'
    )
    assert index_link_targets(text) == ['visible.md']


def test_main_rejects_missing_hidden_and_dangling_entries(tmp_path, monkeypatch, capsys) -> None:
    from scripts import check_docs_index_coverage as checker

    docs = tmp_path / 'docs'
    docs.mkdir()
    note = docs / 'note.md'
    note.write_text('# Note\n')
    index = docs / 'index.md'
    monkeypatch.setattr(checker, 'DOCS_ROOT', docs)
    monkeypatch.setattr(checker, 'INDEX', index)
    monkeypatch.setattr(checker, 'documentation_files', lambda: [note])

    for text in ['# Index\n', '<!-- [Note](note.md) -->', '```\n[Note](note.md)\n```']:
        index.write_text(text)
        assert checker.main() == 1
        assert 'does not link docs/note.md' in capsys.readouterr().err

    index.write_text('[Note](note.md)\n[Missing](missing.md)\n')
    assert checker.main() == 1
    assert 'links a missing file: missing.md' in capsys.readouterr().err

    (docs / 'directory').mkdir()
    index.write_text('[Note](note.md)\n[Directory](directory)\n')
    assert checker.main() == 1
    assert 'links a missing file: directory' in capsys.readouterr().err

    index.write_text('[Note][note]\n\n[note]: note.md "title"\n')
    assert checker.main() == 0


def test_git_inventory_includes_unicode_and_untracked_but_not_ignored(tmp_path, monkeypatch) -> None:
    import subprocess

    from scripts import check_docs_index_coverage as checker

    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    docs = tmp_path / 'docs'
    docs.mkdir()
    for name in ['index.md', 'caf\u00e9.md', 'new note.md', 'ignored.md']:
        (docs / name).write_text('# Note\n')
    (tmp_path / '.gitignore').write_text('docs/ignored.md\n')
    subprocess.run(['git', 'add', 'docs/caf\u00e9.md'], cwd=tmp_path, check=True)
    monkeypatch.setattr(checker, 'REPO_ROOT', tmp_path)
    monkeypatch.setattr(checker, 'DOCS_ROOT', docs)
    assert {p.name for p in checker.documentation_files()} == {'caf\u00e9.md', 'new note.md'}
