# Certificates

This directory is legacy/path-stable space for early exact or interval
certificates and manual certificate templates.

New generated checked certificates should normally live under
`data/certificates/`, with provenance recorded in
`metadata/generated_artifacts.yaml`. The existing n=8 files stay here because
their historical paths are referenced by docs, tests, and manifests.

The current file `best_B12_certificate_template.json` is only a template produced from a numerical near-miss. It is not a proof certificate.

A real certificate should include:

- exact coordinates or exact parameter equations;
- the selected 4-sets `S_i`;
- exact checks that all selected squared-distance differences are zero;
- exact checks that all strict convexity orientation determinants are positive;
- an independent verification script, preferably in Sympy, Sage, Lean, or interval arithmetic.
