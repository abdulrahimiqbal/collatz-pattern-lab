import Collatz.Core
import Collatz.P1DirectDescent
import Collatz.HighParentParametric

/-!
Root-relative high-parent proof-search definitions.

This module is intentionally small: it exposes the exact objects that the
remaining high-parent family must close, while leaving open proof targets as
goal templates under `formal/lean/DeepSeekGoals/`.
-/

namespace Collatz

#check high_parent_to_p32
#check p1_direct_descent
#check descent_implies_collatz
#check forced_burst_semantics
#check iter_div2_power
#check p1_direct_descent_from_parent_state

def highParentRoot (d q : Nat) : Nat :=
  2 ^ (32 + d) * q - 1

def highParentP32Current (d q : Nat) : Nat :=
  2 ^ 32 * (3 ^ d * q) - 1

def RootRelativeDescends (d q : Nat) : Prop :=
  ∃ k : Nat, k >= 1 ∧ iter k (highParentRoot d q) < highParentRoot d q

def P32SpecialRootRelativeDescends (d q : Nat) : Prop :=
  ∃ k : Nat, k >= 1 ∧
    iter k (highParentP32Current d q) < highParentRoot d q

-- TARGET:
-- theorem high_parent_root_relative_descent
--   (d q : Nat)
--   (hd : d >= 1)
--   (hq : q > 0)
--   (hodd : q % 2 = 1) :
--   RootRelativeDescends d q := ...

end Collatz
