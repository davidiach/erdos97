# Numerical runs

Save reproducible JSON outputs here. Do not treat any JSON output as a proof.

Recommended naming:

```text
<pattern>_<optimizer>_<mode>_<date>_<short-seed>.json
```

Archive imports may use:

```text
archive_<pattern>_<short_description>.json
```

For these imports, `mode: "archive_normalized"` means the file was converted
from an external research archive into the verifier-compatible run schema.
Such files may use `seed: -1`, `elapsed_sec: 0.0`, and additional provenance
fields such as `source_file` and `archive_metrics`. They are retained as
search-history artifacts unless the verifier and exactification standards say
otherwise.

Every saved run should record:

- pattern name and formula;
- optimizer and parameterization mode;
- random seed if known;
- equality residuals;
- convexity margin;
- minimum edge length;
- verifier output;
- interpretation: rejected, near-miss, or exactification candidate.
