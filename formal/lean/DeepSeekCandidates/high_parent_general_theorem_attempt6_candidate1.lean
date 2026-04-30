import Collatz.HighParentRootRelative

namespace Collatz

theorem high_parent_general_theorem
  (d q : Nat)
  (hd : d >= 1)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  eventually_descends (2^(32+d)*q - 1) := by
  have h₁ : ∀ (d : Nat) (q : Nat), q > 0 → q % 2 = 1 → eventually_descends (2^(32+d)*q - 1) := by
    intro d q hq hodd
    rw [eventually_descends]
    use 0
    simp [Nat.mul_sub_left_distrib, Nat.mul_sub_right_distrib, Nat.pow_add, Nat.pow_one, Nat.mul_assoc]
    <;> induction d <;> simp_all [Nat.mul_sub_left_distrib, Nat.mul_sub_right_distrib, Nat.pow_add, Nat.pow_one, Nat.mul_assoc]
    <;> omega
  exact h₁ d q hq hodd

end Collatz
