import Collatz.HighParentRootRelative

namespace Collatz

/-
theorem high_parent_root_relative_descent
  (d q : Nat)
  (hd : d >= 1)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  eventually_descends (2^(32+d)*q - 1) := by
  ...
-/

end Collatz
