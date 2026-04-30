import Collatz.HighParentRootRelative
import Collatz.HighParentLowParentContinuations

namespace Collatz

theorem low_parent_b5_margin
  (d q targetQ : Nat)
  (hd : d >= 1)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  LowParentRootRelativeContinuation 5 d q targetQ := by
  rw [LowParentRootRelativeContinuation]
  simp_all [Nat.mod_eq_of_lt, Nat.div_eq_of_lt, Nat.div_eq_of_lt, Nat.div_eq_of_lt,
    Nat.div_eq_of_lt, Nat.div_eq_of_lt, Nat.div_eq_of_lt, Nat.div_eq_of_lt,
    Nat.div_eq_of_lt, Nat.div_eq_of_lt]
  <;> omega

end Collatz
