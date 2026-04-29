import Collatz.HighParentRootRelative

namespace Collatz

-- Proof-search target. Keep this commented in the goal bank.
/-
theorem p32_special_root_relative_general
  (d q : Nat)
  (hd : d >= 1)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  P32SpecialRootRelativeDescends d q := by
  ...
-/

#check highParentRoot
end Collatz
