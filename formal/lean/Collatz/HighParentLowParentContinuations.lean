import Collatz.HighParentRootRelative

/-!
Low-parent continuation search surface for the high-parent obstruction.

RUN-069 showed the available P32-special blocks enter parents `P1..P8`.
This file keeps the continuation obligation named without asserting any open
case as a theorem.
-/

namespace Collatz

def lowParentState (b q : Nat) : Nat :=
  2 ^ b * q - 1

def LowParentRootRelativeContinuation
    (b d q targetQ : Nat) : Prop :=
  ∃ k : Nat, k >= 1 ∧
    iter k (lowParentState b targetQ) < highParentRoot d q

def LowParentMarginCase (b : Nat) : Prop :=
  1 <= b ∧ b <= 8

end Collatz
