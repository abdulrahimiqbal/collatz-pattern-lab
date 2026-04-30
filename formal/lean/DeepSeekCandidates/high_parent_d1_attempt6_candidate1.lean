import Collatz.HighParentRootRelative

namespace Collatz

theorem high_parent_d1
  (q : Nat)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  eventually_descends (2^33 * q - 1) := by
  use 1
  constructor
  norm_num
  norm_num [Nat.mul_sub_left_distrib, Nat.mul_sub_right_distrib, Nat.pow_succ]
  <;> omega

end Collatz
