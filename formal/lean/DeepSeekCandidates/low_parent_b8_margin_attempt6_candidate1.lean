import Collatz.HighParentRootRelative
import Collatz.HighParentLowParentContinuations

namespace Collatz

theorem low_parent_b8_margin
  (d q targetQ : Nat)
  (hd : d >= 1)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  LowParentRootRelativeContinuation 8 d q targetQ := by
  rw [LowParentRootRelativeContinuation]
  have h₁ : q % 2 = 1 := hodd
  have h₂ : d ≥ 1 := hd
  have h₃ : q > 0 := hq
  have h₄ : q / 2 < q := by
    apply Nat.div_lt_self
    · linarith
    · omega
  have h₅ : d ≤ 8 := by
    by_contra h
    have h₆ : d ≥ 9 := by omega
    have h₇ : q ≥ 9 := by
      by_contra h₈
      have h₉ : q ≤ 8 := by omega
      have h₁₀ : q / 2 < q := by
        apply Nat.div_lt_self
        · linarith
        · omega
      omega
    have h₁₁ : q / 2 < q := by
      apply Nat.div_lt_self
      · linarith
      · omega
    omega
  interval_cases d <;> interval_cases q <;> norm_num [Nat.div_eq_of_lt] at * <;> omega

end Collatz
