# n <= 8 Release Packet

Status: generated reviewer release packet; not mathematical evidence
by itself.

Generated from source commit `794e7a286d2b27a5bfdbca3af83bc0fc3eda60cf` (tree
`4b0347dc81771c20a895b9b5a7ca5eb6668654c8`) in https://github.com/davidiach/erdos97. To rebuild it from that clean
source snapshot:

```bash
git checkout 794e7a286d2b27a5bfdbca3af83bc0fc3eda60cf
python scripts/build_n8_release_packet.py --source-ref HEAD
```

To verify these generated files without modifying the checkout:

```bash
python scripts/build_n8_release_packet.py --check
```

`n8-artifact-bundle.zip` is a self-contained platform-neutral review bundle with
its own README, licenses, citation metadata, code, and certificates.
`n8-artifact-bundle-manifest.json` records source and environment provenance;
`n8-artifact-bundle-SHA256SUMS.txt` and `SHA256SUMS.txt` record file integrity.

Official/global status remains falsifiable/open, rechecked from
https://www.erdosproblems.com/97 on 2026-07-09. No general
proof and no counterexample are claimed.
