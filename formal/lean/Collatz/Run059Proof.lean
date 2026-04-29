import Collatz.Run059Data

namespace Collatz

theorem run059_high_parent_to_p32 :
    ∀ a q : Nat,
      32 ≤ a →
      q > 0 →
      iter (2 * (a - 32)) (2 ^ a * q - 1) =
        2 ^ 32 * (3 ^ (a - 32) * q) - 1 :=
  high_parent_to_p32

theorem run059_gap_recorded :
    HighParentRootRelativeDescentGap := by
  trivial

def Run059FormalizationStatus : String :=
  "FINITE_SYSTEM_ROOT_RELATIVE_DESCENT_GAP"

end Collatz
