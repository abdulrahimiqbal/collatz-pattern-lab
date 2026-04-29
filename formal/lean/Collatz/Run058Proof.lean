import Collatz.Run058Data

namespace Collatz

theorem run058_p1_direct_descent :
    ∀ q : Nat, q > 1 → q % 2 = 1 → eventually_descends (2 * q - 1) :=
  p1_direct_descent

theorem run058_step_count :
    run058P1CertificateStepCount = 3 := by
  native_decide

def Run058FormalizationStatus : String :=
  "P1_DIRECT_DESCENT_PROVED"

end Collatz
