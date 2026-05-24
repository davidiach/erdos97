# Proof Sketch Population

This directory is reserved for logged Lean proof-sketch attempts and ratings.
Records here are planning and audit artifacts only. They must not be cited as
mathematical evidence unless a separate Lean/Python verifier checks the exact
certificate or proof target.

Suggested JSONL fields:

```json
{
  "id": "t10_strict_cycle_YYYY_MM_DD_a01",
  "target": "lean/Erdos97/Sketches/T10StrictCycle.lean",
  "claim_scope": "local_template_only",
  "status": "compiles_with_sorries",
  "remaining_goals": [],
  "verifier_commands": [],
  "score": {
    "robustness": 0,
    "decomposition": 0,
    "logical_soundness": 0,
    "novelty": 0
  },
  "do_not_claim": ["n=9", "Erdos97"]
}
```
