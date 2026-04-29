import Collatz.Run051Bundle
import Collatz.GlobalSemantics

/-!
RUN-053 reflection check over the typed RUN-051 bundle.

The finite bundle and component checkers are fully computable and the generated
bundle passes those checks.  RUN-054 proves the transition-soundness component
for reflected S4 parent transitions.  RUN-056 replaces the empty entry/coverage
projection with typed parent-coordinate predicates.  The final descent theorem
is not declared here because the remaining global soundness theorems are still
open.
-/

namespace Collatz

theorem run051Entry_check :
    Reflection.checkEntry run051Bundle = true := by
  native_decide

theorem run051Coverage_check :
    Reflection.checkCoverage run051Bundle = true := by
  native_decide

theorem run051TransitionSoundness_check :
    Reflection.checkTransitionSoundness run051Bundle = true := by
  native_decide

theorem run051NoEscape_check :
    Reflection.checkNoEscape run051Bundle = true := by
  native_decide

theorem run051WellFounded_check :
    Reflection.checkWellFounded run051Bundle = true := by
  native_decide

theorem run051DescentImplication_check :
    Reflection.checkDescentImplication run051Bundle = true := by
  native_decide

theorem run051Bundle_check :
    Reflection.checkCertifiedSystemBundle run051Bundle = true := by
  native_decide

theorem run051TransitionSoundness_sound :
    TransitionSoundnessSemantics run051Bundle.system :=
  Reflection.checkTransitionSoundness_sound
    run051Bundle
    run051TransitionSoundness_check

theorem run051EntryProjection_built :
    GlobalSemantics.EntryProjectionBuilt run051Bundle :=
  GlobalSemantics.entry_projection_built run051Bundle

theorem run051CoveredProjection_built :
    GlobalSemantics.CoveredProjectionBuilt run051Bundle :=
  GlobalSemantics.covered_projection_built run051Bundle

def Run053MissingReflectionGaps : List String :=
  Reflection.MissingReflectionSoundnessTheorems ++
  [
    "there is no theorem converting S3 SUPPORTING_DEBT_EDGE records into the ranking/no-escape assumptions consumed by WellFoundedSystem",
    "there is no typed S6 proof-step checker whose soundness closes NoEscapeSemantics and CoverageSemantics"
  ]

def Run054RemainingReflectionGaps : List String :=
  [
    "checkEntry_sound: reflected universal-entry fields do not yet construct UniversalEntrySemantics run051Bundle.system",
    "checkCoverage_sound: coverage domain map fields do not yet construct CoverageSemantics run051Bundle.system",
    "checkNoEscape_sound: typed S6 proof trees do not yet construct NoEscapeSemantics run051Bundle.system",
    "checkWellFounded_sound: S3 ranking support and kernel path fields do not yet construct WellFoundedSystem run051Bundle.system"
  ]

def Run055MissingGlobalSemanticsGaps : List String :=
  GlobalSemantics.MissingGlobalSemanticsGaps

def Run056ProjectionStatus : List String :=
  [
    "ENTRY_PROJECTION_BUILT: run051Bundle.system.entryState is a typed parent-coordinate entry predicate",
    "COVERAGE_PROJECTION_BUILT: run051Bundle.system.covered is a typed coverage-domain membership predicate",
    "RUN057_REMAINING: prove checkEntry_sound and checkCoverage_sound from these predicates"
  ]

end Collatz
