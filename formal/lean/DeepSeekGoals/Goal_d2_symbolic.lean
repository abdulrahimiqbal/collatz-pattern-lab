import Collatz.HighParentRootRelative

namespace Collatz

-- Proof-search target. Keep this commented in the goal bank.
/-
theorem high_parent_d2
  (q : Nat)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  eventually_descends (2^(32+2) * q - 1) := by
  ...
-/

#check highParentRoot
end Collatz
