import Collatz.HighParentRootRelative

namespace Collatz

theorem p32_special_root_relative_d1
  (q : Nat)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  ∃ k : Nat, k >= 1 ∧
    iter k (2^32 * (3 * q) - 1) < 2^(32+1) * q - 1 := by
  use 1
  constructor
  norm_num
  have h₁ : q ≥ 1 := by linarith
  have h₂ : 2^32 * (3 * q) - 1 < 2^(32+1) * q - 1 := by
    have h₃ : 2^32 * (3 * q) < 2^(32+1) * q := by
      have h₄ : 2^32 * 3 < 2^(32+1) := by
        norm_num
        <;> simp [pow_add, pow_one, mul_assoc]
        <;> norm_num
      have h₅ : 2^32 * (3 * q) < 2^(32+1) * q := by
        calc
          2^32 * (3 * q) = 2^32 * 3 * q := by ring
          _ < 2^(32+1) * q := by gcongr
      exact h₅
    omega
  exact h₂

end Collatz
