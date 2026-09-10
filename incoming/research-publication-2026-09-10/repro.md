# Reproduce the publication evidence

Python 3.10+; the exact checks use only the standard library. Execute from this
parent packet, not by collecting colliding historical test modules directly.

```sh
python -S publication.py
python -S publication.py --scoped --output /tmp/research-publication-fresh.json
python -S -m unittest -v test_research_publication_20260910.py
```

The first checks original bytes only. The second performs the complete scoped
exact replay, including the latest archive's 50 original tests, all older
retained angle certificates/vectors, five earlier exact geometric controls,
and the specified circumcenter scan. The third runs the 19 new defensive tests.

With pytest installed, the artifact-marked integration test is explicit:

```sh
python -m pytest -q -o addopts='' test_research_publication_20260910.py test_research_publication_replay_20260910.py
```

The 19 importer tests run again under pytest; they are not 19 additional tests.
New reports must be written outside `snapshots/`. No snapshot is regenerated in
place. The replay copies inputs to a temporary directory and checks all source
hashes again after execution. Do not disable assertions.

Historical numerical search commands are retained in their snapshot files.
Some earlier generators were not delivered. No missing file is invented;
PUBLICATION_AUDIT.md records precisely which historical claims cannot be replayed.

Repository-wide fast/artifact checks remain required before merge. From the
repository root, run `make verify-fast` and `make verify-artifacts`; the new
artifact-marked replay can also be selected with `python -m pytest -q -m artifact
incoming/research-publication-2026-09-10/test_research_publication_replay_20260910.py`.
See [INTEGRATION.md](INTEGRATION.md) for results from the actual checkout.
The export's optional remote publisher is not part of this repository import.
