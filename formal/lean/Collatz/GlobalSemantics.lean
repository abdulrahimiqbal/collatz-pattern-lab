import Collatz.ReflectionCheckers

/-!
Global semantic projection facts for the reflected RUN-051 transition system.

RUN-056 replaces the empty `entryState`/`covered` projection with typed
predicates.  This module records what the new projection actually means.  It
does not claim the remaining RUN-057/RUN-058/RUN-059 soundness theorems.
-/

namespace Collatz

namespace GlobalSemantics

variable {NodeId EdgeId CertId : Type}
variable [DecidableEq EdgeId]

def EntryProjectionBuilt
    (b : CertifiedSystemBundle NodeId EdgeId CertId) : Prop :=
  ∀ n state,
    b.system.entryState n state →
      n > 1 ∧
      n % 2 ≠ 0 ∧
      state.root = n ∧
      state.current = n ∧
      ∃ q : Nat,
        q > 0 ∧
        state.node = { id := 0 } ∧
        state.current = parentStateNat 0 q

def CoveredProjectionBuilt
    (b : CertifiedSystemBundle NodeId EdgeId CertId) : Prop :=
  ∀ state,
    b.system.covered state →
      ∃ q : Nat,
        q > 0 ∧
        state.current = parentStateNat state.node.id q ∧
        ∃ domain ∈ b.coverageCert.domains,
          domain.coversParentCoordinate state.node.id q

theorem entry_projection_built
    (b : CertifiedSystemBundle NodeId EdgeId CertId) :
    EntryProjectionBuilt b := by
  intro n state hentry
  simpa [
    EntryProjectionBuilt,
    CertifiedSystemBundle.system,
    CertifiedSystemBundle.entryPredicate
  ] using hentry

theorem covered_projection_built
    (b : CertifiedSystemBundle NodeId EdgeId CertId) :
    CoveredProjectionBuilt b := by
  intro state hcovered
  simpa [
    CoveredProjectionBuilt,
    CertifiedSystemBundle.system,
    CertifiedSystemBundle.coveredPredicate
  ] using hcovered

def MissingGlobalSemanticsGaps : List String :=
  [
    "MISSING_ENTRY_TO_COVERAGE_LINK: entryState is now typed, but Lean still needs a theorem that every odd n > 1 has a covered parent-coordinate domain from the generated coverage map.",
    "MISSING_COVERAGE_DOMAIN_MEMBERSHIP_THEOREM: covered is now coverage-domain membership, but Lean still needs closure of those domains under reflected S4 target states.",
    "MISSING_NO_ESCAPE_PROOF_TREE_SEMANTICS: S6 proof trees validate typed dependency shapes, but do not construct NoEscapeSemantics for covered states.",
    "MISSING_KERNEL_TO_PATH_LINK: the natural-kernel payload validates the divisibility story, but does not map every infinite internal path in b.system into that kernel.",
    "MISSING_WELL_FOUNDED_RANK_BRIDGE: checkWellFounded accepts ranked or guarded edges, but no theorem turns those checks into WellFoundedSystem b.system."
  ]

end GlobalSemantics

end Collatz
