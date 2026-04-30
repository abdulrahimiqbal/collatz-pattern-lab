import Collatz.HighParentRootRelative

namespace Collatz

theorem high_parent_d2
  (q : Nat)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  eventually_descends (2^(32+2) * q - 1) := by
  use 1
  constructor
  norm_num
  rw [iter_1]
  norm_num
  <;>
    simp_all [Nat.mul_sub_left_distrib, Nat.mul_sub_right_distrib, Nat.pow_succ]
  <;>
    ring_nf at *
  <;>
    omega

end Collatz
