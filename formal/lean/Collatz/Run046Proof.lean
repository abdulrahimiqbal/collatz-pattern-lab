import Collatz.Run046Data

/-!
RUN-047 Lean replay wrapper for final RUN-045/RUN-046 certificate data.

The theorems in this file are produced by Lean checkers over literal
certificate payloads.  The final semantic bridge from these checked payloads to
`DescentTheorem` remains an explicit RUN-047 formalization gap.
-/

namespace Collatz

theorem run046_s3_check :
    checkAllS3DebtExactCerts run046S3DebtCerts = true := by
  native_decide

theorem run046_s3_sound :
    AllS3DebtClaims run046S3DebtCerts :=
  checkAllS3DebtExactCerts_sound run046S3DebtCerts run046_s3_check

theorem run046_s4_check :
    checkAllS4ParentMapCerts run046S4ParentMapCerts = true := by
  native_decide

theorem run046_s4_sound :
    AllS4ParentMapClaims run046S4ParentMapCerts :=
  checkAllS4ParentMapCerts_sound run046S4ParentMapCerts run046_s4_check

theorem run046_s6_check :
    checkAllS6LemmaCerts run046S6LemmaCerts = true := by
  native_decide

theorem run046_s6_sound :
    AllS6LemmaClaims run046S6LemmaCerts :=
  checkAllS6LemmaCerts_sound run046S6LemmaCerts run046_s6_check

theorem run046_kernel_check :
    checkNaturalViabilityKernelCert run046NaturalKernelCert = true := by
  native_decide

theorem run046_kernel_empty :
    NaturalViabilityKernelEmpty run046NaturalKernelCert :=
  checkNaturalViabilityKernelCert_sound run046NaturalKernelCert run046_kernel_check

theorem run046_top_level_check :
    checkTopLevelCertBundle run046TopLevelCerts = true := by
  native_decide

theorem run046_top_level_sound :
    TopLevelCertificatesImplyDescent run046TopLevelCerts :=
  checkTopLevelCertBundle_sound run046TopLevelCerts run046_top_level_check

end Collatz
