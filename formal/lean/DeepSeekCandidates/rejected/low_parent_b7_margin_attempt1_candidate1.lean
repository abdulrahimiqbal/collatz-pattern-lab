import Collatz.HighParentRootRelative
import Collatz.HighParentLowParentContinuations

namespace Collatz

theorem low_parent_b7_margin
  (d q targetQ : Nat)
  (hd : d >= 1)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  LowParentRootRelativeContinuation 7 d q targetQ := by
  rw [LowParentRootRelativeContinuation]
  simp_all [Nat.div_eq_of_lt]
  <;>
  omega

end Collatz
