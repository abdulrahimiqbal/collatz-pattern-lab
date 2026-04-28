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

theorem even_immediate_descends {m : Nat} (hm : m > 0) :
    eventually_descends (2 * m) := by
  refine ⟨1, by decide, ?_⟩
  simp [iter, C]
  omega

theorem C_two_mul (m : Nat) : C (2 * m) = m := by
  unfold C
  have h : (2 * m) % 2 = 0 := by
    simp [Nat.mul_comm]
  rw [if_pos h]
  exact Nat.mul_div_right m (by decide : 0 < 2)

theorem C_two_mul_sub_one (m : Nat) (hm : m > 0) :
    C (2 * m - 1) = 2 * (3 * m - 1) := by
  unfold C
  have hodd : (2 * m - 1) % 2 ≠ 0 := by
    have hm' : 2 * m - 1 = 2 * (m - 1) + 1 := by
      omega
    rw [hm']
    simp
  rw [if_neg hodd]
  omega

theorem iter_pair_parent (m : Nat) (hm : m > 0) :
    iter 2 (2 * m - 1) = 3 * m - 1 := by
  simp [iter, C_two_mul_sub_one m hm, C_two_mul]

theorem iter_div2_power (h m : Nat) :
    iter h ((2 ^ h) * m) = m := by
  induction h with
  | zero =>
      simp [iter]
  | succ h ih =>
      rw [Nat.pow_succ]
      simp [iter]
      have hrearr : 2 ^ h * 2 * m = 2 * (2 ^ h * m) := by
        simp [Nat.mul_comm, Nat.mul_left_comm]
      rw [hrearr, C_two_mul]
      exact ih

theorem forced_burst_semantics (a q : Nat) (hq : q > 0) :
    iter (2 * a) (2 ^ a * q - 1) = 3 ^ a * q - 1 := by
  induction a generalizing q with
  | zero =>
      simp [iter]
  | succ a ih =>
      have hpow : 2 ^ (a + 1) * q - 1 = 2 * (2 ^ a * q) - 1 := by
        rw [Nat.pow_succ]
        simp [Nat.mul_comm, Nat.mul_left_comm]
      rw [hpow]
      have hm : 2 ^ a * q > 0 :=
        Nat.mul_pos (Nat.pow_pos (by decide : 0 < 2)) hq
      have hpair := iter_pair_parent (2 ^ a * q) hm
      have hadd : 2 * (a + 1) = 2 + 2 * a := by
        omega
      rw [hadd]
      rw [iter_add]
      rw [hpair]
      have h3q : 3 * q > 0 := by
        omega
      have ih3 := ih (3 * q) h3q
      have hre : 3 * (2 ^ a * q) - 1 = 2 ^ a * (3 * q) - 1 := by
        simp [Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm]
      rw [hre]
      rw [ih3]
      simp [Nat.pow_succ, Nat.mul_assoc, Nat.mul_comm]

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
