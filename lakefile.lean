import Lake
open Lake DSL

package collatz_formal where
  srcDir := "formal/lean"

@[default_target]
lean_lib Collatz where
