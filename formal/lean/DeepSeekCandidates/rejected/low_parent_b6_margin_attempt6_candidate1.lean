import Collatz.HighParentRootRelative
import Collatz.HighParentLowParentContinuations

namespace Collatz

theorem low_parent_b6_margin
  (d q targetQ : Nat)
  (hd : d >= 1)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  LowParentRootRelativeContinuation 6 d q targetQ := by
  rw [LowParentRootRelativeContinuation]
  have h₁ : q % 2 = 1 := hodd
  have h₂ : d ≥ 1 := hd
  have h₃ : q > 0 := hq
  have h₄ : q / 2 < q := by
    omega
  have h₅ : d ≤ 6 := by
    by_contra h
    have h₆ : d ≥ 7 := by omega
    have h₇ : d / 2 ≥ 3 := by omega
    have h₈ : q / 2 < q := by omega
    have h₉ : q / 2 ≥ 1 := by omega
    have h₁₀ : q / 2 < d / 2 := by omega
    omega
  interval_cases d <;> interval_cases q <;> norm_num [Nat.div_eq_of_lt] at * <;> omega

end Collatz
