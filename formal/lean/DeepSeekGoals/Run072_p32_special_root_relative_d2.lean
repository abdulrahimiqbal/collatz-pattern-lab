import Collatz.HighParentRootRelative

namespace Collatz

/-
theorem p32_special_root_relative_d2
  (q : Nat)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  ∃ k : Nat, k >= 1 ∧
    iter k (2^32 * (3^2 * q) - 1) < 2^(32+2) * q - 1 := by
  ...
-/

end Collatz
