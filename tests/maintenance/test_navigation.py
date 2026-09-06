from pathlib import Path

from scripts.generate_navigation import inventory_text, session_entries


def test_inventory_includes_landing_page_and_encodes_paths():
    output = inventory_text(['docs/index.md', 'docs/a b.md', 'docs/inventory.md', 'docs/image.png'])
    assert '[index.md](index.md)' in output
    assert '[a b.md](a%20b.md)' in output
    assert '- [inventory.md]' not in output
    assert 'image.png' not in output


def test_session_index_preserves_duplicate_anchors_and_ignores_code():
    output = session_entries('# Log\n## Session 2026-09-06 - Topic\n## Session 2026-09-06 - Topic\n```\n## False 2026-09-07\n```\n')
    assert output == [
        ('2026-09-06', 'Session 2026-09-06 - Topic', 'session-2026-09-06---topic'),
        ('2026-09-06', 'Session 2026-09-06 - Topic', 'session-2026-09-06---topic-1'),
    ]


def test_incoming_index_covers_retained_packet_directories():
    root = Path(__file__).resolve().parents[2]
    text = (root / 'incoming/README.md').read_text()
    for packet in (root / 'incoming').iterdir():
        if packet.is_dir() and not packet.name.startswith('.') and packet.name != '__pycache__':
            assert f']({packet.name}/' in text
