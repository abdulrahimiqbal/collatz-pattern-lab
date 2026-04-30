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
  have h₁ : 2^32 * (3 * q) - 1 < 2^(32+1) * q - 1 := by
    have h₂ : 2^32 * (3 * q) < 2^(32+1) * q := by
      norm_num
      <;>
      ring_nf
      <;>
      omega
    omega
  exact h₁

end Collatz
