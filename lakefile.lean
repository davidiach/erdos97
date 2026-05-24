import Lake
open Lake DSL

package erdos97_lean where
  -- This package is intentionally dependency-free for the first Lean pilot.
  -- Future work can add mathlib/Formal Conjectures imports once the local
  -- bridge statements are stable enough to justify the dependency.

@[default_target]
lean_lib Erdos97 where
  srcDir := "lean"
