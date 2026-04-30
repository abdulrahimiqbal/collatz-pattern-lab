import Collatz.HighParentRootRelative
import Collatz.HighParentLowParentContinuations

namespace Collatz

theorem low_parent_b7_margin
  (d q targetQ : Nat)
  (hd : d >= 1)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  LowParentRootRelativeContinuation 7 d q targetQ := by
  rw [LowParentRootRelativeContinuation]
  have h₁ : q % 2 = 1 := hodd
  have h₂ : d ≥ 1 := hd
  have h₃ : q > 0 := hq
  have h₄ : (q + 1) / 2 ≤ d := by
    omega
  have h₅ : (q - 1) / 2 < d := by
    omega
  omega

end Collatz
