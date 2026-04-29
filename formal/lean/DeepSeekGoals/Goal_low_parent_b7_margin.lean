import Collatz.HighParentLowParentContinuations

namespace Collatz

-- BLOCKED: missing target-coordinate formula from RUN-069 branch payload
/-
theorem low_parent_b7_margin
  (d q targetQ : Nat)
  (hd : d >= 1)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  LowParentRootRelativeContinuation 7 d q targetQ := by
  ...
-/

#check LowParentRootRelativeContinuation
end Collatz
