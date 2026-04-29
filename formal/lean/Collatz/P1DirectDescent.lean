import Collatz.Core

/-!
Direct descent for the `P1` odd-entry family.
-/

namespace Collatz

theorem odd_nat_decomp (q : Nat) (hq_odd : q % 2 = 1) :
    q = 2 * (q / 2) + 1 := by
  have h := Nat.mod_add_div q 2
  omega

theorem p1_iter_three_eq (q : Nat) (hq_gt_one : q > 1) (hq_odd : q % 2 = 1) :
    iter 3 (2 * q - 1) = 3 * (q / 2) + 1 := by
  let r := q / 2
  have hq : q = 2 * r + 1 := by
    simpa [r] using odd_nat_decomp q hq_odd
  have hr_pos : r > 0 := by
    omega
  have hstart : 2 * q - 1 = 2 * (2 * r + 1) - 1 := by
    rw [hq]
  rw [hstart]
  have htarget : 3 * (2 * r + 1) - 1 = 2 * (3 * r + 1) := by
    omega
  simp [iter]
  rw [C_two_mul_sub_one (2 * r + 1) (by omega : 2 * r + 1 > 0)]
  rw [C_two_mul]
  rw [htarget]
  rw [C_two_mul]

theorem p1_direct_descent (q : Nat) (hq_gt_one : q > 1) (hq_odd : q % 2 = 1) :
    eventually_descends (2 * q - 1) := by
  let r := q / 2
  have hq : q = 2 * r + 1 := by
    simpa [r] using odd_nat_decomp q hq_odd
  have hr_pos : r > 0 := by
    omega
  refine ⟨3, by decide, ?_⟩
  rw [p1_iter_three_eq q hq_gt_one hq_odd]
  rw [hq]
  omega

theorem p1_direct_descent_from_parent_state
    {n q : Nat}
    (hn : n = 2 * q - 1)
    (hn_gt_one : n > 1)
    (hq_odd : q % 2 = 1) :
    eventually_descends n := by
  have hq_gt_one : q > 1 := by omega
  subst n
  exact p1_direct_descent q hq_gt_one hq_odd

end Collatz
