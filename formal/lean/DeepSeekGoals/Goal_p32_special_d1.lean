import Collatz.HighParentRootRelative

namespace Collatz

-- Proof-search target. Keep this commented in the goal bank.
/-
theorem p32_special_root_relative_d1
  (q : Nat)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  ∃ k : Nat, k >= 1 ∧
    iter k (2^32 * (3 * q) - 1) < 2^(32+1) * q - 1 := by
  ...
-/

#check highParentRoot
end Collatz
