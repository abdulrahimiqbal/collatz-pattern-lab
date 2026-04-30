import Collatz.HighParentRootRelative
import Collatz.HighParentLowParentContinuations

namespace Collatz

theorem low_parent_b7_margin
  (d q targetQ : Nat)
  (hd : d >= 1)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  LowParentRootRelativeContinuation 7 d q targetQ := by
  use 1
  constructor
  linarith
  simp [lowParentState, highParentRoot, iter, Nat.mul_mod, Nat.add_mod, Nat.mod_eq_of_lt]
  <;> norm_num
  <;> omega

end Collatz
