import Collatz.HighParentRootRelative

namespace Collatz

theorem high_parent_general_theorem
  (d q : Nat)
  (hd : d >= 1)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  eventually_descends (2^(32+d)*q - 1) := by
  use 1
  constructor
  norm_num
  have h : 2^(32+d)*q - 1 > 0 := by
    have h₁ : 2^(32+d)*q > 1 := by
      have h₂ : 2^(32+d) > 0 := by positivity
      have h₃ : q > 0 := by assumption
      have h₄ : 2^(32+d)*q > 1 := by
        calc
          2^(32+d)*q ≥ 2^(32+d)*1 := by gcongr <;> linarith
          _ = 2^(32+d) := by ring
          _ > 1 := by
            apply Nat.one_lt_pow
            <;> linarith
            <;> linarith
      nlinarith
    omega
  simp_all [eventually_descends, iter]
  <;> omega

end Collatz
