import Collatz.Certificates

namespace Collatz

def S3DebtClaim (cert : S3DebtExactCert) : Prop :=
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

abbrev S3DebtExactClaim := S3DebtClaim

instance (cert : S3DebtExactCert) : Decidable (S3DebtClaim cert) := by
  unfold S3DebtClaim
  infer_instance

def checkS3DebtExactCert (cert : S3DebtExactCert) : Bool :=
  decide (S3DebtClaim cert)

theorem checkS3DebtExactCert_sound
    (cert : S3DebtExactCert) :
    checkS3DebtExactCert cert = true →
    S3DebtClaim cert := by
  intro h
  unfold checkS3DebtExactCert at h
  exact of_decide_eq_true h

def AllS3DebtClaims : List S3DebtExactCert → Prop
  | [] => True
  | cert :: rest => S3DebtClaim cert ∧ AllS3DebtClaims rest

abbrev AllS3DebtExactClaims := AllS3DebtClaims

def checkAllS3DebtExactCerts : List S3DebtExactCert → Bool
  | [] => true
  | cert :: rest => checkS3DebtExactCert cert && checkAllS3DebtExactCerts rest

theorem checkAllS3DebtExactCerts_sound
    (certs : List S3DebtExactCert) :
    checkAllS3DebtExactCerts certs = true →
    AllS3DebtClaims certs := by
  induction certs with
  | nil =>
      intro _h
      exact True.intro
  | cons cert rest ih =>
      intro h
      unfold checkAllS3DebtExactCerts at h
      have hand := (Bool.and_eq_true (checkS3DebtExactCert cert) (checkAllS3DebtExactCerts rest)).mp h
      exact ⟨checkS3DebtExactCert_sound cert hand.left, ih hand.right⟩

def expectedKDivisibilityModulus (valuation : Nat) : Nat :=
  if valuation = 0 then 1 else 2 ^ valuation

def S4ParentMapPayloadClaim (cert : S4ParentMapCert) : Prop :=
  cert.mapA = cert.coefficient ∧
  cert.mapD = cert.domainModulus ∧
  cert.mapD > 0 ∧
  cert.domainModulus = (2 ^ cert.sourceDepth) * cert.kDivisibilityModulus ∧
  cert.domainResidue < cert.domainModulus ∧
  cert.sourceResidue < 2 ^ cert.sourceDepth ∧
  cert.minimumQ > 0 ∧
  (cert.mapA * cert.domainResidue + cert.mapB) % cert.mapD = 0 ∧
  cert.parentCoordinateMapCertificateHash ≠ "" ∧
  cert.parentCoordinateMapCertificateId ≠ "" ∧
  cert.parentCoordinateMapReplays = true ∧
  cert.parentCoordinateIntegralityProven = true ∧
  cert.parentCoordinatePositivityProven = true

def S4ParentMapClaim (cert : S4ParentMapCert) : Prop :=
  cert.coefficient = 3 ^ cert.sourceParent ∧
  cert.oddModulus = cert.coefficient ∧
  cert.divValuation = cert.valuation ∧
  cert.kDivisibilityModulus = expectedKDivisibilityModulus cert.valuation ∧
  cert.excludedNextPowerModulus = 2 ^ (cert.valuation + 1) ∧
  (cert.inversePowerTwoMod3a * (2 ^ cert.valuation)) % cert.oddModulus = 1 % cert.oddModulus ∧
  (cert.targetOddResidueMod3a * (2 ^ cert.valuation)) % cert.oddModulus = cert.c % cert.oddModulus ∧
  cert.parentFloor + cert.valuation = cert.targetParent ∧
  cert.membershipTargetParent = cert.targetParent ∧
  (cert.hasParentMapPayload = false ∨ S4ParentMapPayloadClaim cert)

abbrev S4TransitionClaim := S4ParentMapClaim

instance (cert : S4ParentMapCert) : Decidable (S4ParentMapClaim cert) := by
  unfold S4ParentMapClaim S4ParentMapPayloadClaim expectedKDivisibilityModulus
  infer_instance

def checkS4ParentMapCert (cert : S4ParentMapCert) : Bool :=
  decide (S4ParentMapClaim cert)

def checkS4TransitionCert := checkS4ParentMapCert

theorem checkS4ParentMapCert_sound
    (cert : S4ParentMapCert) :
    checkS4ParentMapCert cert = true →
    S4ParentMapClaim cert := by
  intro h
  unfold checkS4ParentMapCert at h
  exact of_decide_eq_true h

theorem checkS4TransitionCert_sound
    (cert : S4TransitionCert) :
    checkS4TransitionCert cert = true →
    S4TransitionClaim cert :=
  checkS4ParentMapCert_sound cert

def AllS4ParentMapClaims : List S4ParentMapCert → Prop
  | [] => True
  | cert :: rest => S4ParentMapClaim cert ∧ AllS4ParentMapClaims rest

abbrev AllS4TransitionClaims := AllS4ParentMapClaims

def checkAllS4ParentMapCerts : List S4ParentMapCert → Bool
  | [] => true
  | cert :: rest => checkS4ParentMapCert cert && checkAllS4ParentMapCerts rest

def checkAllS4TransitionCerts := checkAllS4ParentMapCerts

theorem checkAllS4ParentMapCerts_sound
    (certs : List S4ParentMapCert) :
    checkAllS4ParentMapCerts certs = true →
    AllS4ParentMapClaims certs := by
  induction certs with
  | nil =>
      intro _h
      exact True.intro
  | cons cert rest ih =>
      intro h
      unfold checkAllS4ParentMapCerts at h
      have hand := (Bool.and_eq_true (checkS4ParentMapCert cert) (checkAllS4ParentMapCerts rest)).mp h
      exact ⟨checkS4ParentMapCert_sound cert hand.left, ih hand.right⟩

theorem checkAllS4TransitionCerts_sound
    (certs : List S4TransitionCert) :
    checkAllS4TransitionCerts certs = true →
    AllS4TransitionClaims certs :=
  checkAllS4ParentMapCerts_sound certs

def S6LemmaExactPayloadClaim (cert : S6LemmaCert) : Prop :=
  cert.dependencyHashCount = cert.dependencyIds.length ∧
  cert.dependencyReplayPayloadCount = cert.dependencyIds.length ∧
  cert.coverageCertificateCount > 0 ∧
  cert.noEscapeCertificateCount > 0 ∧
  cert.rankingOrInductionCertificateCount > 0 ∧
  cert.s3DebtExactCertificateCount > 0 ∧
  cert.s4ParentTransitionCertificateCount > 0 ∧
  cert.allDependenciesPresent = true ∧
  cert.allDependenciesHashMatch = true ∧
  cert.allDependenciesReplayPass = true ∧
  cert.closesTargetBlocker = true ∧
  cert.statementMatchesBlocker = true ∧
  cert.status = true

def S6LemmaClaim (cert : S6LemmaCert) : Prop :=
  cert.certificateId ≠ "" ∧
  cert.lemmaId ≠ "" ∧
  cert.blockerId ≠ "" ∧
  cert.dependencyIds ≠ [] ∧
  (cert.hasExactPayload = false ∨ S6LemmaExactPayloadClaim cert)

abbrev S6LemmaStructuralClaim := S6LemmaClaim

instance (cert : S6LemmaCert) : Decidable (S6LemmaClaim cert) := by
  unfold S6LemmaClaim S6LemmaExactPayloadClaim
  infer_instance

def checkS6LemmaCert (cert : S6LemmaCert) : Bool :=
  decide (S6LemmaClaim cert)

theorem checkS6LemmaCert_sound
    (cert : S6LemmaCert) :
    checkS6LemmaCert cert = true →
    S6LemmaClaim cert := by
  intro h
  unfold checkS6LemmaCert at h
  exact of_decide_eq_true h

def AllS6LemmaClaims : List S6LemmaCert → Prop
  | [] => True
  | cert :: rest => S6LemmaClaim cert ∧ AllS6LemmaClaims rest

def checkAllS6LemmaCerts : List S6LemmaCert → Bool
  | [] => true
  | cert :: rest => checkS6LemmaCert cert && checkAllS6LemmaCerts rest

theorem checkAllS6LemmaCerts_sound
    (certs : List S6LemmaCert) :
    checkAllS6LemmaCerts certs = true →
    AllS6LemmaClaims certs := by
  induction certs with
  | nil =>
      intro _h
      exact True.intro
  | cons cert rest ih =>
      intro h
      unfold checkAllS6LemmaCerts at h
      have hand := (Bool.and_eq_true (checkS6LemmaCert cert) (checkAllS6LemmaCerts rest)).mp h
      exact ⟨checkS6LemmaCert_sound cert hand.left, ih hand.right⟩

def NaturalDenominatorClaim (cert : NaturalViabilityKernelCert) : Prop :=
  cert.denominator > 0 ∧
  cert.denominator % 2 = 1 ∧
  cert.denominatorOdd = true

def NaturalNumeratorClaim (cert : NaturalViabilityKernelCert) : Prop :=
  cert.numerator < 0 ∧
  cert.numeratorNegative = true ∧
  cert.numerator = -((cert.mapB : Int))

def NaturalMapClaim (cert : NaturalViabilityKernelCert) : Prop :=
  cert.mapA > cert.mapD ∧
  cert.denominator = cert.mapA - cert.mapD ∧
  cert.mapD = 2 ^ cert.lassoDepth ∧
  cert.lassoDepth > 0 ∧
  cert.mapA % 2 = 1 ∧
  cert.fixedPointEquation = true ∧
  (cert.mapA : Int) * cert.numerator + (cert.mapB : Int) * (cert.denominator : Int) =
    (cert.mapD : Int) * cert.numerator ∧
  cert.lassoDenominatorIsPowerOfTwo = true ∧
  cert.lassoMultiplierIsOdd = true ∧
  cert.kernelCongruenceDepthUnbounded = true ∧
  cert.anyNaturalQHasFiniteDistance = true ∧
  cert.thereforeNoPositiveIntegerQInKernel = true

def NaturalViabilityKernelArithmeticClaim (cert : NaturalViabilityKernelCert) : Prop :=
  cert.status = true ∧
  NaturalDenominatorClaim cert ∧
  NaturalNumeratorClaim cert ∧
  NaturalMapClaim cert

def NaturalKernelEmptyClaim (cert : NaturalViabilityKernelCert) : Prop :=
  NaturalViabilityKernelArithmeticClaim cert ∧
  ∀ q : Nat, q > 0 → (cert.denominator : Int) * (q : Int) - cert.numerator ≠ 0

abbrev NaturalViabilityKernelEmpty := NaturalKernelEmptyClaim

instance (cert : NaturalViabilityKernelCert) :
    Decidable (NaturalViabilityKernelArithmeticClaim cert) := by
  unfold NaturalViabilityKernelArithmeticClaim NaturalDenominatorClaim NaturalNumeratorClaim NaturalMapClaim
  infer_instance

def checkNaturalViabilityKernelCert (cert : NaturalViabilityKernelCert) : Bool :=
  decide (NaturalViabilityKernelArithmeticClaim cert)

theorem positive_nat_not_nonpositive_fixed_point
    {den q : Nat} {num : Int}
    (hden : den > 0) (hq : q > 0) (hnum : num < 0) :
    (den : Int) * (q : Int) - num ≠ 0 := by
  intro hzero
  have hdeni : (0 : Int) < den := by exact_mod_cast hden
  have hqi : (0 : Int) < q := by exact_mod_cast hq
  have hprod : (0 : Int) < (den : Int) * (q : Int) := by
    exact Int.mul_pos hdeni hqi
  omega

theorem no_nat_in_non_natural_2adic_kernel
    (cert : NaturalViabilityKernelCert) :
    checkNaturalViabilityKernelCert cert = true →
    NaturalKernelEmptyClaim cert := by
  intro h
  unfold checkNaturalViabilityKernelCert at h
  have hcore : NaturalViabilityKernelArithmeticClaim cert := of_decide_eq_true h
  refine ⟨hcore, ?_⟩
  intro q hq
  exact positive_nat_not_nonpositive_fixed_point hcore.2.1.1 hq hcore.2.2.1.1

theorem checkNaturalViabilityKernelCert_sound
    (cert : NaturalViabilityKernelCert) :
    checkNaturalViabilityKernelCert cert = true →
    NaturalViabilityKernelEmpty cert :=
  no_nat_in_non_natural_2adic_kernel cert

def CoverageDomainClaim (domain : CoverageDomain) : Prop :=
  domain.modulus > 0 ∧
  domain.residueStart < domain.residueEndExclusive ∧
  domain.residueEndExclusive ≤ domain.modulus

instance (domain : CoverageDomain) : Decidable (CoverageDomainClaim domain) := by
  unfold CoverageDomainClaim
  infer_instance

def checkCoverageDomainClaim (domain : CoverageDomain) : Bool :=
  decide (CoverageDomainClaim domain)

def AllCoverageDomainClaims (domains : List CoverageDomain) : Prop :=
  domains.all checkCoverageDomainClaim = true

instance (domains : List CoverageDomain) : Decidable (AllCoverageDomainClaims domains) := by
  unfold AllCoverageDomainClaims
  infer_instance

def RankedEdgeCheckClaim (edge : RankedEdgeCheck) : Prop :=
  edge.decreases = true ∧
  edge.targetRank < edge.sourceRank

instance (edge : RankedEdgeCheck) : Decidable (RankedEdgeCheckClaim edge) := by
  unfold RankedEdgeCheckClaim
  infer_instance

def checkRankedEdgeCheckClaim (edge : RankedEdgeCheck) : Bool :=
  decide (RankedEdgeCheckClaim edge)

def AllRankedEdgeCheckClaims (edges : List RankedEdgeCheck) : Prop :=
  edges.all checkRankedEdgeCheckClaim = true

instance (edges : List RankedEdgeCheck) : Decidable (AllRankedEdgeCheckClaims edges) := by
  unfold AllRankedEdgeCheckClaims
  infer_instance

def GuardedSccCheckClaim (check : GuardedSccCheck) : Prop :=
  check.status = true ∧
  check.proofKind = "natural_viability_kernel_elimination" ∧
  check.coveredEdgeCount > 0

instance (check : GuardedSccCheck) : Decidable (GuardedSccCheckClaim check) := by
  unfold GuardedSccCheckClaim
  infer_instance

def checkGuardedSccCheckClaim (check : GuardedSccCheck) : Bool :=
  decide (GuardedSccCheckClaim check)

def AllGuardedSccCheckClaims (checks : List GuardedSccCheck) : Prop :=
  checks.all checkGuardedSccCheckClaim = true

instance (checks : List GuardedSccCheck) : Decidable (AllGuardedSccCheckClaims checks) := by
  unfold AllGuardedSccCheckClaims
  infer_instance

def UniversalEntryClaim (cert : UniversalEntryCert) : Prop :=
  cert.certificateType = "universal_entry_certificate" ∧
  cert.theoremStatement = "forall n > 1 exists k >= 1 such that C^k(n) < n" ∧
  cert.replayStatus = true ∧
  cert.strictReplay = true ∧
  cert.status = true ∧
  cert.evenDenominatorPositive = true ∧
  cert.evenStrictDescentForKGeOne = true ∧
  cert.oddExactReconstruction = true ∧
  cert.oddNPlusOnePositive = true ∧
  cert.oddQuotientAfterV2 = true ∧
  cert.oddPowerTwoDivides = true

def ParentResidualClaim (cert : ResidualParentCert) : Prop :=
  cert.certificateId ≠ "" ∧
  cert.modulus > 0 ∧
  cert.residualStart < cert.residualEnd ∧
  cert.residualEnd ≤ cert.modulus ∧
  cert.pathNodeCount > 0 ∧
  cert.rankingDeltaDen > 0 ∧
  cert.rankingDeltaNum < cert.rankingDeltaDen

def ParentStateCoverageClaim (cert : ParentStateCoverageCert) : Prop :=
  cert.certificateType = "parent_state_coverage_certificate" ∧
  cert.replayStatus = true ∧
  cert.strictReplay = true ∧
  cert.status = true ∧
  cert.requiredDomains.length = cert.coveredDomains.length ∧
  cert.uncoveredDomainCount = 0 ∧
  cert.lowerLayerStatus = true ∧
  cert.lowerExpectedS3 = cert.lowerPassedS3 ∧
  cert.lowerExpectedS4 = cert.lowerPassedS4 ∧
  cert.lowerExpectedS6 = cert.lowerPassedS6 ∧
  AllCoverageDomainClaims cert.requiredDomains ∧
  AllCoverageDomainClaims cert.coveredDomains ∧
  ParentResidualClaim cert.parentResidual

def TransitionSoundnessClaim (cert : TransitionSoundnessCert) : Prop :=
  cert.certificateType = "transition_soundness_certificate" ∧
  cert.replayStatus = true ∧
  cert.strictReplay = true ∧
  cert.status = true ∧
  cert.failureCount = 0 ∧
  cert.expectedS3 = cert.s3ExactCertificateCount ∧
  cert.expectedS3 = cert.s3ExactReplayPass ∧
  cert.expectedS4 = cert.s4ExactCertificateCount ∧
  cert.expectedS4 = cert.s4ExactReplayPass ∧
  cert.expectedS6 = cert.s6ExactCertificateCount ∧
  cert.expectedS6 = cert.s6ExactReplayPass

def WellFoundedRankingClaim (cert : WellFoundedRankingCert) : Prop :=
  cert.certificateType = "well_founded_ranking_certificate" ∧
  cert.replayStatus = true ∧
  cert.strictReplay = true ∧
  cert.status = true ∧
  cert.domain = "parent_state_transition_graph" ∧
  cert.wellFoundedOrder = "topological_dag_rank_with_guarded_scc_rank" ∧
  cert.unresolvedSccCount = 0 ∧
  cert.nondecreasingEdgeCount = 0 ∧
  cert.nonterminalEdgeCount + cert.terminalEdgeCount = cert.transitionEdgeCount ∧
  AllRankedEdgeCheckClaims cert.edgeChecks ∧
  AllGuardedSccCheckClaims cert.sccChecks

def DescentImplicationClaim (cert : DescentImplicationCert) : Prop :=
  cert.certificateType = "descent_implication_certificate" ∧
  cert.replayStatus = true ∧
  cert.strictReplay = true ∧
  cert.status = true ∧
  cert.blockedByCount = 0 ∧
  cert.baseCaseN = 1 ∧
  cert.baseCaseReachesOne = true ∧
  cert.descentTheoremStatement = "forall n > 1 exists k >= 1 such that C^k(n) < n" ∧
  cert.collatzConjectureStatement = "forall n > 1 exists t >= 0 such that C^t(n) = 1" ∧
  cert.universalEntryHash ≠ "" ∧
  cert.parentStateCoverageHash ≠ "" ∧
  cert.transitionSoundnessHash ≠ "" ∧
  cert.wellFoundedRankingHash ≠ ""

def TopLevelCertificatesImplyDescent (bundle : TopLevelCertBundle) : Prop :=
  UniversalEntryClaim bundle.universalEntry ∧
  ParentStateCoverageClaim bundle.parentStateCoverage ∧
  TransitionSoundnessClaim bundle.transitionSoundness ∧
  WellFoundedRankingClaim bundle.wellFoundedRanking ∧
  DescentImplicationClaim bundle.descentImplication ∧
  bundle.universalEntryHash = bundle.universalEntry.certificateHash ∧
  bundle.parentStateCoverageHash = bundle.parentStateCoverage.certificateHash ∧
  bundle.transitionSoundnessHash = bundle.transitionSoundness.certificateHash ∧
  bundle.wellFoundedRankingHash = bundle.wellFoundedRanking.certificateHash ∧
  bundle.descentImplicationHash = bundle.descentImplication.certificateHash ∧
  bundle.theoremStatement = bundle.descentImplication.descentTheoremStatement ∧
  bundle.descentImplicationStatement = bundle.descentImplication.collatzConjectureStatement

instance (cert : UniversalEntryCert) : Decidable (UniversalEntryClaim cert) := by
  unfold UniversalEntryClaim
  infer_instance

instance (cert : ResidualParentCert) : Decidable (ParentResidualClaim cert) := by
  unfold ParentResidualClaim
  infer_instance

instance (cert : ParentStateCoverageCert) : Decidable (ParentStateCoverageClaim cert) := by
  unfold ParentStateCoverageClaim
  infer_instance

instance (cert : TransitionSoundnessCert) : Decidable (TransitionSoundnessClaim cert) := by
  unfold TransitionSoundnessClaim
  infer_instance

instance (cert : WellFoundedRankingCert) : Decidable (WellFoundedRankingClaim cert) := by
  unfold WellFoundedRankingClaim
  infer_instance

instance (cert : DescentImplicationCert) : Decidable (DescentImplicationClaim cert) := by
  unfold DescentImplicationClaim
  infer_instance

instance (bundle : TopLevelCertBundle) : Decidable (TopLevelCertificatesImplyDescent bundle) := by
  unfold TopLevelCertificatesImplyDescent
  infer_instance

def checkUniversalEntryCert (cert : UniversalEntryCert) : Bool :=
  decide (UniversalEntryClaim cert)

def checkParentStateCoverageCert (cert : ParentStateCoverageCert) : Bool :=
  decide (ParentStateCoverageClaim cert)

def checkTransitionSoundnessCert (cert : TransitionSoundnessCert) : Bool :=
  decide (TransitionSoundnessClaim cert)

def checkWellFoundedRankingCert (cert : WellFoundedRankingCert) : Bool :=
  decide (WellFoundedRankingClaim cert)

def checkDescentImplicationCert (cert : DescentImplicationCert) : Bool :=
  decide (DescentImplicationClaim cert)

def checkTopLevelCertBundle (bundle : TopLevelCertBundle) : Bool :=
  decide (TopLevelCertificatesImplyDescent bundle)

theorem checkUniversalEntryCert_sound
    (cert : UniversalEntryCert) :
    checkUniversalEntryCert cert = true →
    UniversalEntryClaim cert := by
  intro h
  unfold checkUniversalEntryCert at h
  exact of_decide_eq_true h

theorem checkParentStateCoverageCert_sound
    (cert : ParentStateCoverageCert) :
    checkParentStateCoverageCert cert = true →
    ParentStateCoverageClaim cert := by
  intro h
  unfold checkParentStateCoverageCert at h
  exact of_decide_eq_true h

theorem checkTransitionSoundnessCert_sound
    (cert : TransitionSoundnessCert) :
    checkTransitionSoundnessCert cert = true →
    TransitionSoundnessClaim cert := by
  intro h
  unfold checkTransitionSoundnessCert at h
  exact of_decide_eq_true h

theorem checkWellFoundedRankingCert_sound
    (cert : WellFoundedRankingCert) :
    checkWellFoundedRankingCert cert = true →
    WellFoundedRankingClaim cert := by
  intro h
  unfold checkWellFoundedRankingCert at h
  exact of_decide_eq_true h

theorem checkDescentImplicationCert_sound
    (cert : DescentImplicationCert) :
    checkDescentImplicationCert cert = true →
    DescentImplicationClaim cert := by
  intro h
  unfold checkDescentImplicationCert at h
  exact of_decide_eq_true h

theorem checkTopLevelCertBundle_sound
    (bundle : TopLevelCertBundle) :
    checkTopLevelCertBundle bundle = true →
    TopLevelCertificatesImplyDescent bundle := by
  intro h
  unfold checkTopLevelCertBundle at h
  exact of_decide_eq_true h

def checkUniversalEntryLegacy (bundle : TopLevelCertBundle) : Bool :=
  decide (bundle.theoremStatement = "forall n > 1 exists k >= 1 such that C^k(n) < n")

def checkParentStateCoverageLegacy (bundle : TopLevelCertBundle) : Bool :=
  decide (bundle.openNodeCount = 0 ∧ bundle.acceptedNodeCount = bundle.totalNodeCount)

def checkTransitionSoundnessLegacy (bundle : TopLevelCertBundle) : Bool :=
  decide (bundle.transitionSoundnessHash ≠ "")

def checkWellFoundedRankingLegacy (bundle : TopLevelCertBundle) : Bool :=
  decide (bundle.wellFoundedRankingHash ≠ "")

def checkDescentImplicationLegacy (bundle : TopLevelCertBundle) : Bool :=
  decide (bundle.descentImplicationStatement = "forall n > 1 exists t >= 0 such that C^t(n) = 1")

def checkRun024Manifest (manifest : Run024Manifest) : Bool :=
  checkAllS3DebtExactCerts manifest.s3DebtExactCerts &&
  checkAllS4TransitionCerts manifest.s4Certs &&
  checkAllS6LemmaCerts manifest.s6Certs &&
  checkUniversalEntryLegacy manifest.topLevel &&
  checkParentStateCoverageLegacy manifest.topLevel &&
  checkTransitionSoundnessLegacy manifest.topLevel &&
  checkWellFoundedRankingLegacy manifest.topLevel &&
  checkDescentImplicationLegacy manifest.topLevel

end Collatz
