import Collatz.HighParentRootRelative

namespace Collatz

theorem p32_special_root_relative_d2
  (q : Nat)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  ∃ k : Nat, k >= 1 ∧
    iter k (2^32 * (3^2 * q) - 1) < 2^(32+2) * q - 1 := by
  use 1
  constructor
  norm_num
  have h₁ : q ≥ 1 := by linarith
  have h₂ : 2^32 * (3^2 * q) - 1 < 2^(32+2) * q - 1 := by
    have h₃ : 2^32 * (3^2 * q) < 2^(32+2) * q := by
      have h₄ : 2^32 * (3^2 * q) = 2^32 * 9 * q := by ring
      have h₅ : 2^(32+2) * q = 2^34 * q := by ring
      have h₆ : 2^32 * 9 * q < 2^34 * q := by
        have h₇ : 2^32 * 9 < 2^34 := by
          norm_num
          <;> simp [pow_add, pow_mul]
          <;> norm_num
          <;> omega
        have h₈ : 0 < q := by linarith
        have h₉ : 0 < 2^34 * q := by positivity
        nlinarith
      nlinarith
    omega
  exact h₂

end Collatz
