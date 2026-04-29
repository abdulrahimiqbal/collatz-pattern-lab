import Collatz.HighParentRootRelative

namespace Collatz

theorem p32_d1_iter_64
  (q : Nat)
  (hq : q > 0) :
  iter 64 (2^32 * (3*q) - 1) = 3^33 * q - 1 := by
  have h3q : 3 * q > 0 := by omega
  have h := forced_burst_semantics 32 (3 * q) h3q
  have hsteps : 2 * 32 = 64 := by decide
  rw [hsteps] at h
  have hmul : 3 ^ 32 * (3 * q) = 3 ^ 33 * q := by
    rw [show 33 = 32 + 1 by decide]
    rw [Nat.pow_succ]
    simp [Nat.mul_assoc, Nat.mul_comm]
  rw [hmul] at h
  exact h

theorem p32_d1_iter_65
  (q : Nat)
  (hq : q > 0)
  (hodd : q % 2 = 1) :
  iter 65 (2^32 * (3*q) - 1) = (3^33 * q - 1) / 2 := by
  have h64 := p32_d1_iter_64 q hq
  rw [show 65 = 64 + 1 by decide]
  rw [iter_add]
  rw [h64]
  have hpow_odd : (3 ^ 33) % 2 = 1 := by decide
  have hprod_odd : (3 ^ 33 * q) % 2 = 1 := by
    rw [Nat.mul_mod, hpow_odd, hodd]
  have hpos_prod : 3 ^ 33 * q > 0 := by
    exact Nat.mul_pos (Nat.pow_pos (by decide : 0 < 3)) hq
  have heven : (3 ^ 33 * q - 1) % 2 = 0 := by
    omega
  simp [iter]
  unfold C
  rw [if_pos heven]

theorem p32_d1_iter_64_plus_h
  (q h m : Nat)
  (hq : q > 0)
  (hm : 3^33 * q - 1 = 2^h * m) :
  iter (64 + h) (2^32 * (3*q) - 1) = m := by
  rw [iter_add]
  rw [p32_d1_iter_64 q hq]
  rw [hm]
  exact iter_div2_power h m

end Collatz
