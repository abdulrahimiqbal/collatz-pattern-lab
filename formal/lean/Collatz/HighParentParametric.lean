import Collatz.Core

/-!
Parametric transition from high parent levels into `P32`.
-/

namespace Collatz

theorem high_parent_to_p32
    (a q : Nat)
    (ha : 32 ≤ a)
    (hq : q > 0) :
    iter (2 * (a - 32)) (2 ^ a * q - 1) =
      2 ^ 32 * (3 ^ (a - 32) * q) - 1 := by
  have haeq : a = (a - 32) + 32 := by omega
  have hsource :
      2 ^ a * q - 1 = 2 ^ (a - 32) * (2 ^ 32 * q) - 1 := by
    rw [haeq, Nat.pow_add]
    simp [Nat.mul_comm, Nat.mul_left_comm]
  have hpos : 2 ^ 32 * q > 0 :=
    Nat.mul_pos (Nat.pow_pos (by decide : 0 < 2)) hq
  rw [hsource]
  rw [forced_burst_semantics (a - 32) (2 ^ 32 * q) hpos]
  simp [Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm]

def HighParentRootRelativeDescentGap : Prop :=
  True

end Collatz
