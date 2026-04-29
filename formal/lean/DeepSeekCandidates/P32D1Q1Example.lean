import Collatz.HighParentRootRelative

namespace Collatz

theorem p32_special_root_relative_d1_q1 :
  ∃ k : Nat, k >= 1 ∧
    iter k (2^32 * (3*1) - 1) < 2^33 * 1 - 1 := by
  refine ⟨198, by decide, ?_⟩
  native_decide

end Collatz
