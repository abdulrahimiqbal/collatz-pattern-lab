/-!
RUN-056B global semantic map vocabulary.

These structures record machine-readable map attempts for entry, coverage,
no-escape, and well-foundedness.  A map checker only opens when the generated
artifact has theorem-grade witness fields; the current RUN-056B data is
expected to fail closed.
-/

namespace Collatz

structure GlobalSemanticMap where
  kind : String
  status : Bool
  failureReasons : List String
  observedFiniteNodeCount : Nat
  witnessCount : Nat
  theoremWitnessesPresent : Bool
  semanticMapHash : String
deriving Repr

def checkGlobalSemanticMap (expectedKind : String) (m : GlobalSemanticMap) : Bool :=
  (m.kind == expectedKind) &&
    m.status &&
    m.failureReasons.isEmpty &&
    m.theoremWitnessesPresent &&
    decide (m.witnessCount > 0)

def checkEntrySemanticMap (m : GlobalSemanticMap) : Bool :=
  checkGlobalSemanticMap "ENTRY_TO_CERTIFIED_NODE_MAP" m

def checkCoverageSemanticMap (m : GlobalSemanticMap) : Bool :=
  checkGlobalSemanticMap "COVERAGE_DOMAIN_MEMBERSHIP_MAP" m

def checkNoEscapeSemanticMap (m : GlobalSemanticMap) : Bool :=
  checkGlobalSemanticMap "NO_ESCAPE_APPLICABLE_EDGE_MAP" m

def checkWellFoundedSemanticMap (m : GlobalSemanticMap) : Bool :=
  checkGlobalSemanticMap "WELL_FOUNDED_KERNEL_TO_PATH_MAP" m

def Run056BExpectedMapKinds : List String :=
  [
    "ENTRY_TO_CERTIFIED_NODE_MAP",
    "COVERAGE_DOMAIN_MEMBERSHIP_MAP",
    "NO_ESCAPE_APPLICABLE_EDGE_MAP",
    "WELL_FOUNDED_KERNEL_TO_PATH_MAP"
  ]

end Collatz
