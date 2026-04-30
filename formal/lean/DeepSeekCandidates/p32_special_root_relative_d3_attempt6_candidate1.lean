import Collatz.HighParentRootRelative

namespace Collatz

theorem p32_special_root_relative_d3
  (q : Nat)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  ∃ k : Nat, k >= 1 ∧
    iter k (2^32 * (3^3 * q) - 1) < 2^(32+3) * q - 1 := by
  use 1
  constructor
  norm_num
  have h₁ : 2^32 * (3^3 * q) - 1 < 2^(32+3) * q - 1 := by
    have h₂ : 2^32 * (3^3 * q) < 2^(32+3) * q := by
      have h₃ : 2^32 * (3^3 * q) = 2^32 * 3^3 * q := by ring
      have h₄ : 2^(32+3) * q = 2^35 * q := by ring
      have h₅ : 2^32 * 3^3 * q < 2^35 * q := by
        have h₆ : 2^32 * 3^3 < 2^35 := by
          norm_num
        have h₇ : 0 < q := by linarith
        have h₈ : 0 < 2^35 * q := by positivity
        nlinarith
      linarith
    omega
  exact h₁

end Collatz
