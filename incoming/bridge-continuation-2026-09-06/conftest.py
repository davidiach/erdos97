"""Collect publication tests; replay historical modules in isolated subprocesses.

The snapshots reuse global names such as verify, fixtures, and test_bridge.
Direct collection would bind unrelated modules in a single pytest process.
All 101 archived tests remain exercised by test_publication.py below.
"""

collect_ignore = ["snapshots"]
