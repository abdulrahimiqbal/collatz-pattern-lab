import Collatz.ParametricEntryCoverage

/-!
Generated RUN-057 parametric entry coverage taxonomy.
-/

namespace Collatz

def run057ParametricEntryCoverageTaxonomy :
    ParametricEntryCoverageTaxonomy := {
  finiteParentLevelMin := 2,
  finiteParentLevelMax := 32,
  finiteParentLevelCount := 31,
  s4SourceLevelCount := 20,
  s4TargetLevelCount := 14,
  hasParametricParentFamily := false,
  hasOddImmediateDescentFamily := false,
  uncoveredFamilyCount := 2,
  universalEntryCoverageSupported := false,
  failureReason := "MISSING_PARAMETRIC_ENTRY_COVERAGE"
}

def run057UncoveredParentFamilies : List String :=
  [
    "odd_entry_parent_level_1",
    "odd_entry_parent_levels_ge_33"
  ]

end Collatz
