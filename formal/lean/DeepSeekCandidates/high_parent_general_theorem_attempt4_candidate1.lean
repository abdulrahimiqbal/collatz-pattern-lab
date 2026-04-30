import Collatz.HighParentRootRelative

namespace Collatz

theorem high_parent_general_theorem
  (d q : Nat)
  (hd : d >= 1)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  eventually_descends (2^(32+d)*q - 1) := by
  have h₁ : ∀ (d : Nat) (q : Nat), q > 0 → q % 2 = 1 → eventually_descends (2^(32+d)*q - 1) := by
    intro d q hq hodd
    have h₂ : ∀ (d : Nat), eventually_descends (2^(32+d)*q - 1) := by
      intro d
      apply Nat.strong_induction_on d
      intro n ih
      have h₃ : n = 0 ∨ n > 0 := by omega
      cases h₃ with
      | inl h₃ =>
        simp_all [eventually_descends, Nat.descends_to_one]
        <;> omega
      | inr h₃ =>
        have h₄ : n ≥ 1 := by omega
        have h₅ : iter n (2^(32+d)*q - 1) < 2^(32+d)*q - 1 := by
          have h₆ : iter n (2^(32+d)*q - 1) < 2^(32+d)*q - 1 := by
            cases n with
            | zero => contradiction
            | succ n =>
              simp_all [iter, Nat.descends_to_one]
              <;> omega
          exact h₆
        simp_all [eventually_descends, Nat.descends_to_one]
        <;> omega
    exact h₂ d
  exact h₁ d q hq hodd

end Collatz
