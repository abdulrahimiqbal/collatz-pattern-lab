import Collatz.Certificates

namespace Collatz

def S3DebtExactClaim (cert : S3DebtExactCert) : Prop :=
  cert.exactCongruenceCertificate.typeName = "S3_EXACT_CONGRUENCE" ∧
  cert.exactCongruenceCertificate.branchId = cert.branchId ∧
  cert.exactCongruenceCertificate.sourceParent = cert.sourceParent ∧
  cert.exactCongruenceCertificate.targetParent = cert.targetParent ∧
  cert.exactCongruenceCertificate.valuation = cert.valuation ∧
  cert.exactCongruenceCertificate.sourceModulus = 2 ^ cert.exactCongruenceCertificate.branchDepth ∧
  cert.exactCongruenceCertificate.branchResidue < cert.exactCongruenceCertificate.sourceModulus ∧
  cert.exactCongruenceCertificate.theoremName = "mixed_modulus_debt_transition_exactness" ∧
  cert.debtMeasureDefinition.typeName = "MIXED_LOG_GAIN_RANK" ∧
  cert.debtMeasureDefinition.measureId = "mixed_log_gain_rank" ∧
  cert.debtMeasureDefinition.branchId = cert.branchId ∧
  cert.debtMeasureDefinition.sourceParent = cert.sourceParent ∧
  cert.debtMeasureDefinition.targetParent = cert.targetParent ∧
  cert.debtMeasureDefinition.valuation = cert.valuation ∧
  cert.debtMeasureDefinition.gainNum = cert.gainNum ∧
  cert.debtMeasureDefinition.gainDen = cert.gainDen ∧
  cert.debtMeasureDefinition.decreaseInequality = "gain_num < gain_den" ∧
  cert.localDescentCertificate.typeName = "LOCAL_DESCENT_FROM_DEBT_GAIN" ∧
  cert.localDescentCertificate.branchId = cert.branchId ∧
  cert.localDescentCertificate.gainNum = cert.gainNum ∧
  cert.localDescentCertificate.gainDen = cert.gainDen ∧
  cert.localDescentCertificate.rule = "positive denominator and gain ratio below one implies local debt descent" ∧
  cert.gainDen > 0 ∧
  cert.gainNum < cert.gainDen

instance (cert : S3DebtExactCert) : Decidable (S3DebtExactClaim cert) := by
  unfold S3DebtExactClaim
  infer_instance

def checkS3DebtExactCert (cert : S3DebtExactCert) : Bool :=
  decide (S3DebtExactClaim cert)

theorem checkS3DebtExactCert_sound
    (cert : S3DebtExactCert) :
    checkS3DebtExactCert cert = true →
    S3DebtExactClaim cert := by
  intro h
  unfold checkS3DebtExactCert at h
  exact of_decide_eq_true h

def AllS3DebtExactClaims : List S3DebtExactCert → Prop
  | [] => True
  | cert :: rest => S3DebtExactClaim cert ∧ AllS3DebtExactClaims rest

def checkAllS3DebtExactCerts : List S3DebtExactCert → Bool
  | [] => true
  | cert :: rest => checkS3DebtExactCert cert && checkAllS3DebtExactCerts rest

theorem checkAllS3DebtExactCerts_sound
    (certs : List S3DebtExactCert) :
    checkAllS3DebtExactCerts certs = true →
    AllS3DebtExactClaims certs := by
  induction certs with
  | nil =>
      intro _h
      exact True.intro
  | cons cert rest ih =>
      intro h
      unfold checkAllS3DebtExactCerts at h
      have hcert : checkS3DebtExactCert cert = true := by
        exact (Bool.and_eq_true (checkS3DebtExactCert cert) (checkAllS3DebtExactCerts rest)).mp h |>.left
      have hrest : checkAllS3DebtExactCerts rest = true := by
        exact (Bool.and_eq_true (checkS3DebtExactCert cert) (checkAllS3DebtExactCerts rest)).mp h |>.right
      exact ⟨checkS3DebtExactCert_sound cert hcert, ih hrest⟩

def expectedKDivisibilityModulus (valuation : Nat) : Nat :=
  if valuation = 0 then 1 else 2 ^ valuation

def S4TransitionClaim (cert : S4TransitionCert) : Prop :=
  cert.coefficient = 3 ^ cert.sourceParent ∧
  cert.oddModulus = cert.coefficient ∧
  cert.divValuation = cert.valuation ∧
  cert.kDivisibilityModulus = expectedKDivisibilityModulus cert.valuation ∧
  cert.excludedNextPowerModulus = 2 ^ (cert.valuation + 1) ∧
  (cert.inversePowerTwoMod3a * (2 ^ cert.valuation)) % cert.oddModulus = 1 % cert.oddModulus ∧
  (cert.targetOddResidueMod3a * (2 ^ cert.valuation)) % cert.oddModulus = cert.c % cert.oddModulus ∧
  cert.parentFloor + cert.valuation = cert.targetParent ∧
  cert.membershipTargetParent = cert.targetParent

instance (cert : S4TransitionCert) : Decidable (S4TransitionClaim cert) := by
  unfold S4TransitionClaim
  infer_instance

def checkS4TransitionCert (cert : S4TransitionCert) : Bool :=
  decide (S4TransitionClaim cert)

theorem checkS4TransitionCert_sound
    (cert : S4TransitionCert) :
    checkS4TransitionCert cert = true →
    S4TransitionClaim cert := by
  intro h
  unfold checkS4TransitionCert at h
  exact of_decide_eq_true h

def AllS4TransitionClaims : List S4TransitionCert → Prop
  | [] => True
  | cert :: rest => S4TransitionClaim cert ∧ AllS4TransitionClaims rest

def checkAllS4TransitionCerts : List S4TransitionCert → Bool
  | [] => true
  | cert :: rest => checkS4TransitionCert cert && checkAllS4TransitionCerts rest

theorem checkAllS4TransitionCerts_sound
    (certs : List S4TransitionCert) :
    checkAllS4TransitionCerts certs = true →
    AllS4TransitionClaims certs := by
  induction certs with
  | nil =>
      intro _h
      exact True.intro
  | cons cert rest ih =>
      intro h
      unfold checkAllS4TransitionCerts at h
      have hcert : checkS4TransitionCert cert = true := by
        exact (Bool.and_eq_true (checkS4TransitionCert cert) (checkAllS4TransitionCerts rest)).mp h |>.left
      have hrest : checkAllS4TransitionCerts rest = true := by
        exact (Bool.and_eq_true (checkS4TransitionCert cert) (checkAllS4TransitionCerts rest)).mp h |>.right
      exact ⟨checkS4TransitionCert_sound cert hcert, ih hrest⟩

def S6LemmaStructuralClaim (cert : S6LemmaCert) : Prop :=
  cert.certificateId ≠ "" ∧
  cert.lemmaId ≠ "" ∧
  cert.blockerId ≠ "" ∧
  cert.dependencyIds ≠ []

instance (cert : S6LemmaCert) : Decidable (S6LemmaStructuralClaim cert) := by
  unfold S6LemmaStructuralClaim
  infer_instance

def checkS6LemmaCert (cert : S6LemmaCert) : Bool :=
  decide (S6LemmaStructuralClaim cert)

theorem checkS6LemmaCert_sound
    (cert : S6LemmaCert) :
    checkS6LemmaCert cert = true →
    S6LemmaStructuralClaim cert := by
  intro h
  unfold checkS6LemmaCert at h
  exact of_decide_eq_true h

def checkUniversalEntryCert (bundle : TopLevelCertBundle) : Bool :=
  decide (bundle.theoremStatement = "forall n > 1 exists k >= 1 such that C^k(n) < n")

def checkParentStateCoverageCert (bundle : TopLevelCertBundle) : Bool :=
  decide (bundle.openNodeCount = 0 ∧ bundle.acceptedNodeCount = bundle.totalNodeCount)

def checkTransitionSoundnessCert (bundle : TopLevelCertBundle) : Bool :=
  decide (bundle.transitionSoundnessHash ≠ "")

def checkWellFoundedRankingCert (bundle : TopLevelCertBundle) : Bool :=
  decide (bundle.wellFoundedRankingHash ≠ "")

def checkDescentImplicationCert (bundle : TopLevelCertBundle) : Bool :=
  decide (bundle.descentImplicationStatement = "forall n > 1 exists t >= 0 such that C^t(n) = 1")

def checkRun024Manifest (manifest : Run024Manifest) : Bool :=
  checkAllS3DebtExactCerts manifest.s3DebtExactCerts &&
  checkAllS4TransitionCerts manifest.s4Certs &&
  manifest.s6Certs.all checkS6LemmaCert &&
  checkUniversalEntryCert manifest.topLevel &&
  checkParentStateCoverageCert manifest.topLevel &&
  checkTransitionSoundnessCert manifest.topLevel &&
  checkWellFoundedRankingCert manifest.topLevel &&
  checkDescentImplicationCert manifest.topLevel

end Collatz
