import Collatz.HighParentRootRelative
import Collatz.HighParentLowParentContinuations

namespace Collatz

theorem low_parent_b6_margin
  (d q targetQ : Nat)
  (hd : d >= 1)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  LowParentRootRelativeContinuation 6 d q targetQ := by
  rw [LowParentRootRelativeContinuation]
  norm_num
  <;>
  rcases d with (_ | _ | d) <;>
  rcases q with (_ | _ | q) <;>
  simp_all [Nat.div_eq_of_lt, Nat.mod_eq_of_lt, Nat.div_eq_of_lt, Nat.mod_eq_of_lt] <;>
  omega

end Collatz
