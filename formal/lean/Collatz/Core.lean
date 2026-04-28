import Std

/-!
Core Collatz definitions and the theorem bridge.

This module proves that a descent theorem for the usual Collatz map implies
reachability of `1` for every positive natural number.
-/

namespace Collatz

def C (n : Nat) : Nat :=
  if n % 2 = 0 then n / 2 else 3 * n + 1

def iter : Nat -> Nat -> Nat
  | 0, n => n
  | Nat.succ k, n => iter k (C n)

theorem iter_add (a b n : Nat) : iter (a + b) n = iter b (iter a n) := by
  induction a generalizing n with
  | zero => simp [iter]
  | succ a ih =>
      simp [iter, Nat.succ_add, ih]

theorem C_positive {n : Nat} (hn : n > 0) : C n > 0 := by
  unfold C
  by_cases h : n % 2 = 0
  · rw [if_pos h]
    have hn_ne_one : n ≠ 1 := by
      intro hn1
      rw [hn1] at h
      have hmod : (1 % 2 : Nat) = 1 := by decide
      rw [hmod] at h
      omega
    have hle : 2 ≤ n := by omega
    exact Nat.div_pos hle (by decide)
  · rw [if_neg h]
    omega

theorem iter_positive {n k : Nat} (hn : n > 0) : iter k n > 0 := by
  induction k generalizing n with
  | zero => simpa [iter] using hn
  | succ k ih =>
      simpa [iter] using ih (C_positive hn)

def reaches_one (n : Nat) : Prop :=
  ∃ t : Nat, iter t n = 1

def eventually_descends (n : Nat) : Prop :=
  ∃ k : Nat, k ≥ 1 ∧ iter k n < n

def DescentTheorem : Prop :=
  ∀ n : Nat, n > 1 -> eventually_descends n

def CollatzConjecture : Prop :=
  ∀ n : Nat, n > 0 -> reaches_one n

theorem descent_implies_collatz
    (descent : DescentTheorem) :
    CollatzConjecture := by
  intro n
  induction n using Nat.strongRecOn with
  | ind n ih =>
      intro hn_pos
      by_cases h_one : n = 1
      · exact ⟨0, by simp [iter, h_one]⟩
      · have hn_gt_one : n > 1 := by omega
        obtain ⟨k, _hk_ge_one, hk_descends⟩ := descent n hn_gt_one
        have hm_pos : iter k n > 0 := iter_positive hn_pos
        obtain ⟨t, ht⟩ := ih (iter k n) hk_descends hm_pos
        exact ⟨k + t, by simpa [iter_add] using ht⟩

end Collatz
