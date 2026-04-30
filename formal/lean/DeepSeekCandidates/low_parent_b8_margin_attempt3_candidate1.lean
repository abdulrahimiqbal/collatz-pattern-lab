import Collatz.HighParentRootRelative
import Collatz.HighParentLowParentContinuations

namespace Collatz

theorem low_parent_b8_margin
  (d q targetQ : Nat)
  (hd : d >= 1)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  LowParentRootRelativeContinuation 8 d q targetQ := by
  use 1
  constructor
  linarith
  simp [lowParentState, highParentRoot, Nat.div_eq_of_lt, Nat.mod_eq_of_lt, Nat.div_eq_of_lt,
    Nat.mod_eq_of_lt, Nat.div_eq_of_lt, Nat.mod_eq_of_lt, Nat.div_eq_of_lt, Nat.mod_eq_of_lt]
  <;> omega

end Collatz
