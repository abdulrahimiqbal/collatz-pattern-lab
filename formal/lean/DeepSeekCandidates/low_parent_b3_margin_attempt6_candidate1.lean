import Collatz.HighParentRootRelative
import Collatz.HighParentLowParentContinuations

namespace Collatz

theorem low_parent_b3_margin
  (d q targetQ : Nat)
  (hd : d >= 1)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  LowParentRootRelativeContinuation 3 d q targetQ := by
  rw [LowParentRootRelativeContinuation]
  simp_all [Nat.odd_iff_not_even, Nat.even_iff, Nat.mod_eq_of_lt]
  <;>
  omega

end Collatz
