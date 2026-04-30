import Collatz.HighParentRootRelative

namespace Collatz

theorem high_parent_d3
  (q : Nat)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  eventually_descends (2^(32+3) * q - 1) := by
  rw [eventually_descends]
  use 0
  simp_all [Nat.mul_sub_left_distrib, Nat.mul_sub_right_distrib, Nat.pow_add, Nat.pow_mul, Nat.mul_assoc]
  <;> omega

end Collatz
