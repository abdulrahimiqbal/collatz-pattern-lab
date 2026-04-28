import Collatz.ReflectionCheckers

/-!
Global semantic obligations for the reflected RUN-051 transition system.

RUN-054 completed the transition-soundness bridge for reflected S4 edges.  This
module records the first remaining RUN-055 obstruction: the current reflected
`CertifiedSystemBundle.system` projection has no entry states and no covered
states.  Therefore the requested `checkEntry_sound` theorem cannot be proved
from the present typed bundle without adding a real entry/coverage projection.
-/

namespace Collatz

namespace GlobalSemantics

variable {NodeId EdgeId CertId : Type}
variable [DecidableEq EdgeId]

theorem reflected_system_entry_state_false
    (b : CertifiedSystemBundle NodeId EdgeId CertId)
    (n : Nat) (state : InternalState) :
    ¬ b.system.entryState n state := by
  intro h
  exact h

theorem reflected_system_covered_false
    (b : CertifiedSystemBundle NodeId EdgeId CertId)
    (state : InternalState) :
    ¬ b.system.covered state := by
  intro h
  exact h

theorem reflected_system_not_universal_entry
    (b : CertifiedSystemBundle NodeId EdgeId CertId) :
    ¬ UniversalEntrySemantics b.system := by
  intro hentry
  have hgt : (3 : Nat) > 1 := by decide
  have hodd : (3 : Nat) % 2 ≠ 0 := by decide
  obtain ⟨state, hstate_entry, _hroot, _hcurrent, _hcovered⟩ :=
    hentry 3 hgt hodd
  exact reflected_system_entry_state_false b 3 state hstate_entry

theorem checkEntry_soundness_obstructed
    [DecidableEq NodeId] [DecidableEq CertId]
    (b : CertifiedSystemBundle NodeId EdgeId CertId) :
    Reflection.checkEntry b = true →
    ¬ UniversalEntrySemantics b.system := by
  intro _hcheck
  exact reflected_system_not_universal_entry b

def MissingGlobalSemanticsGaps : List String :=
  [
    "MISSING_ENTRY_TO_COVERAGE_LINK: CertifiedSystemBundle.system currently has entryState := False, so reflected universal-entry booleans do not construct an InternalState.",
    "MISSING_COVERAGE_DOMAIN_MEMBERSHIP_THEOREM: RUN-051 coverage domains validate finite residue metadata, but do not define system.covered or prove arbitrary entry membership.",
    "MISSING_NO_ESCAPE_PROOF_TREE_SEMANTICS: S6 proof trees validate typed dependency shapes, but do not construct NoEscapeSemantics for covered states.",
    "MISSING_KERNEL_TO_PATH_LINK: the natural-kernel payload validates the divisibility story, but does not map every infinite internal path in b.system into that kernel.",
    "MISSING_WELL_FOUNDED_RANK_BRIDGE: checkWellFounded accepts ranked or guarded edges, but no theorem turns those checks into WellFoundedSystem b.system."
  ]

end GlobalSemantics

end Collatz
