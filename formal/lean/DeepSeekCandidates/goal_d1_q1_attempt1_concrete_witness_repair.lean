import Collatz.HighParentRootRelative

namespace Collatz

theorem goal_d1_q1 :
  eventually_descends (2^33 * 1 - 1) := by
  refine Exists.intro 200 ?_
  exact And.intro (by decide) (by native_decide)

end Collatz
