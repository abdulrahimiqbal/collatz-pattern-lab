import Collatz.HighParentRootRelative

namespace Collatz

theorem goal_d1_q1 :
  eventually_descends (2^33 * 1 - 1) := by
  refine' ⟨200, _⟩
  norm_num
  <;> decide
  <;> rfl
  <;> decide
  <;> rfl

end Collatz
