import Collatz.Run051ReflectionProof

/-!
RUN-057 parametric entry coverage vocabulary.

The current generated taxonomy is an audit object: it can close only if the
artifact supplies a real map from arbitrary odd-entry parent levels into the
certified reflected system.
-/

namespace Collatz

inductive ParentCoverageCategory where
  | coveredFiniteParentLevel
  | coveredParametricParentFamily
  | immediateDescentParentFamily
  | transitionsIntoCertifiedRange
  | uncoveredParentFamily
deriving Repr, DecidableEq

structure ParametricEntryCoverageTaxonomy where
  finiteParentLevelMin : Nat
  finiteParentLevelMax : Nat
  finiteParentLevelCount : Nat
  s4SourceLevelCount : Nat
  s4TargetLevelCount : Nat
  hasParametricParentFamily : Bool
  hasOddImmediateDescentFamily : Bool
  uncoveredFamilyCount : Nat
  universalEntryCoverageSupported : Bool
  failureReason : String
deriving Repr

def checkParametricEntryCoverageTaxonomy
    (taxonomy : ParametricEntryCoverageTaxonomy) : Bool :=
  taxonomy.universalEntryCoverageSupported &&
    taxonomy.hasParametricParentFamily &&
    decide (taxonomy.uncoveredFamilyCount = 0)

def ParametricEntryCoverageGap
    (taxonomy : ParametricEntryCoverageTaxonomy) : Prop :=
  taxonomy.universalEntryCoverageSupported = false ∧
    taxonomy.uncoveredFamilyCount > 0 ∧
    taxonomy.failureReason = "MISSING_PARAMETRIC_ENTRY_COVERAGE"

def ParametricEntryCoverageCert :=
  ParametricEntryCoverageTaxonomy

end Collatz
