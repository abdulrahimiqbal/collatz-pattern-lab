import Collatz.Run057Data

/-!
RUN-057 proof status.

The current taxonomy refutes reopening the universal entry gate.  No descent
theorem is introduced here.
-/

namespace Collatz

theorem run057_parametric_entry_coverage_check_fails :
    checkParametricEntryCoverageTaxonomy
      run057ParametricEntryCoverageTaxonomy = false := by
  native_decide

theorem run057_parametric_entry_coverage_gap :
    ParametricEntryCoverageGap
      run057ParametricEntryCoverageTaxonomy := by
  unfold ParametricEntryCoverageGap
  simp [run057ParametricEntryCoverageTaxonomy]

def Run057FormalizationStatus : String :=
  "MISSING_PARAMETRIC_ENTRY_COVERAGE"

def Run057MissingParametricEntryCoverage : List String :=
  [
    "odd_entry_parent_level_1: no generated P1 node/domain and no odd immediate-descent certificate",
    "odd_entry_parent_levels_ge_33: no parametric lift or high-parent coverage family into the finite certified node range"
  ]

end Collatz
