import Collatz.ParentState

namespace Collatz

structure S4TransitionCert where
  transitionId : String
  branchId : String
  sourceParent : Nat
  targetParent : Nat
  valuation : Nat
  c : Nat
  coefficient : Nat
  divValuation : Nat
  kDivisibilityModulus : Nat
  kDivisibilityResidue : Nat
  excludedNextPowerModulus : Nat
  excludedNextPowerResidue : Nat
  oddModulus : Nat
  inversePowerTwoMod3a : Nat
  targetOddResidueMod3a : Nat
  parentFloor : Nat
  membershipTargetParent : Nat
  certificateHash : String
  hasParentMapPayload : Bool := false
  mapA : Nat := 0
  mapB : Nat := 0
  mapD : Nat := 0
  baseBurstDivisionExponent : Nat := 0
  domainModulus : Nat := 0
  domainResidue : Nat := 0
  minimumQ : Nat := 0
  sourceDepth : Nat := 0
  sourceResidue : Nat := 0
  parentCoordinateMapCertificateHash : String := ""
  parentCoordinateMapCertificateId : String := ""
  parentCoordinateMapReplays : Bool := false
  parentCoordinateIntegralityProven : Bool := false
  parentCoordinatePositivityProven : Bool := false
deriving Repr, DecidableEq

abbrev S4ParentMapCert := S4TransitionCert

structure S4ParentTransitionSemanticWitness where
  certificateId : String
  sourceParent : Nat
  targetParent : Nat
  valuation : Nat
  sourceDepth : Nat
  sourceResidue : Nat
  baseBurstDivisionExponent : Nat
  standardStepCount : Nat
  mapA : Nat
  mapB : Nat
  mapD : Nat
  c : Nat
  semanticWitnessHash : String
deriving Repr, DecidableEq

structure S3ExactCongruenceCert where
  typeName : String
  branchId : String
  sourceParent : Nat
  targetParent : Nat
  valuation : Nat
  branchResidue : Nat
  branchDepth : Nat
  sourceModulus : Nat
  theoremName : String
  statement : String
deriving Repr, DecidableEq

structure S3DebtMeasureDefinition where
  typeName : String
  measureId : String
  branchId : String
  sourceParent : Nat
  targetParent : Nat
  valuation : Nat
  gainNum : Nat
  gainDen : Nat
  decreaseInequality : String
deriving Repr, DecidableEq

structure S3LocalDescentCert where
  typeName : String
  branchId : String
  gainNum : Nat
  gainDen : Nat
  rule : String
deriving Repr, DecidableEq

structure S3DebtExactCert where
  nodeId : String
  branchId : String
  sourceParent : Nat
  targetParent : Nat
  valuation : Nat
  gainNum : Nat
  gainDen : Nat
  exactCongruenceCertificate : S3ExactCongruenceCert
  debtMeasureDefinition : S3DebtMeasureDefinition
  localDescentCertificate : S3LocalDescentCert
  certificateHash : String
deriving Repr, DecidableEq

structure S6LemmaCert where
  certificateId : String
  lemmaId : String
  blockerId : String
  blockerType : String
  dependencyIds : List String
  certificateHash : String
  hasExactPayload : Bool := false
  dependencyHashCount : Nat := 0
  dependencyReplayPayloadCount : Nat := 0
  coverageCertificateCount : Nat := 0
  noEscapeCertificateCount : Nat := 0
  rankingOrInductionCertificateCount : Nat := 0
  residualParentCertificateCount : Nat := 0
  s3DebtExactCertificateCount : Nat := 0
  s4ParentTransitionCertificateCount : Nat := 0
  allDependenciesPresent : Bool := false
  allDependenciesHashMatch : Bool := false
  allDependenciesReplayPass : Bool := false
  closesTargetBlocker : Bool := false
  statementMatchesBlocker : Bool := false
  status : Bool := false
deriving Repr, DecidableEq

structure ResidualParentCert where
  certificateId : String
  parentLevel : Nat
  modulus : Nat
  residualStart : Nat
  residualEnd : Nat
  pathNodeCount : Nat
  rankingDeltaNum : Nat
  rankingDeltaDen : Nat
  certificateHash : String
deriving Repr, DecidableEq, Inhabited

structure NaturalViabilityKernelCert where
  numerator : Int
  denominator : Nat
  denominatorOdd : Bool
  numeratorNegative : Bool
  status : Bool
  mapA : Nat := 0
  mapB : Nat := 0
  mapD : Nat := 0
  lassoDepth : Nat := 0
  fixedPointEquation : Bool := false
  lassoDenominatorIsPowerOfTwo : Bool := false
  lassoMultiplierIsOdd : Bool := false
  kernelCongruenceDepthUnbounded : Bool := false
  anyNaturalQHasFiniteDistance : Bool := false
  thereforeNoPositiveIntegerQInKernel : Bool := false
  certificateHash : String := ""
deriving Repr, DecidableEq

structure UniversalEntryCert where
  certificateId : String := ""
  certificateHash : String := ""
  certificateType : String := ""
  theoremStatement : String := ""
  replayStatus : Bool := false
  strictReplay : Bool := false
  status : Bool := false
  evenDenominatorPositive : Bool := false
  evenStrictDescentForKGeOne : Bool := false
  oddExactReconstruction : Bool := false
  oddNPlusOnePositive : Bool := false
  oddQuotientAfterV2 : Bool := false
  oddPowerTwoDivides : Bool := false
deriving Repr, DecidableEq, Inhabited

structure CoverageDomain where
  domainId : String := ""
  kind : String := ""
  modulus : Nat := 0
  residueStart : Nat := 0
  residueEndExclusive : Nat := 0
  parentLevel : Nat := 0
deriving Repr, DecidableEq, Inhabited

structure ParentStateCoverageCert where
  certificateId : String := ""
  certificateHash : String := ""
  certificateType : String := ""
  replayStatus : Bool := false
  strictReplay : Bool := false
  status : Bool := false
  requiredDomains : List CoverageDomain := []
  coveredDomains : List CoverageDomain := []
  uncoveredDomainCount : Nat := 0
  lowerExpectedS3 : Nat := 0
  lowerExpectedS4 : Nat := 0
  lowerExpectedS6 : Nat := 0
  lowerPassedS3 : Nat := 0
  lowerPassedS4 : Nat := 0
  lowerPassedS6 : Nat := 0
  lowerLayerStatus : Bool := false
  parentResidual : ResidualParentCert := {
    certificateId := "",
    parentLevel := 0,
    modulus := 0,
    residualStart := 0,
    residualEnd := 0,
    pathNodeCount := 0,
    rankingDeltaNum := 0,
    rankingDeltaDen := 0,
    certificateHash := ""
  }
deriving Repr, DecidableEq, Inhabited

structure TransitionSoundnessCert where
  certificateId : String := ""
  certificateHash : String := ""
  certificateType : String := ""
  replayStatus : Bool := false
  strictReplay : Bool := false
  status : Bool := false
  expectedS3 : Nat := 0
  expectedS4 : Nat := 0
  expectedS6 : Nat := 0
  s3ExactCertificateCount : Nat := 0
  s3ExactReplayPass : Nat := 0
  s4ExactCertificateCount : Nat := 0
  s4ExactReplayPass : Nat := 0
  s6ExactCertificateCount : Nat := 0
  s6ExactReplayPass : Nat := 0
  failureCount : Nat := 0
deriving Repr, DecidableEq, Inhabited

structure RankedEdgeCheck where
  edgeId : String := ""
  source : String := ""
  target : String := ""
  sourceRank : Nat := 0
  targetRank : Nat := 0
  decreases : Bool := false
deriving Repr, DecidableEq, Inhabited

structure GuardedSccCheck where
  sccId : String := ""
  proofKind : String := ""
  status : Bool := false
  coveredEdgeCount : Nat := 0
deriving Repr, DecidableEq, Inhabited

structure WellFoundedRankingCert where
  certificateId : String := ""
  certificateHash : String := ""
  certificateType : String := ""
  replayStatus : Bool := false
  strictReplay : Bool := false
  status : Bool := false
  domain : String := ""
  wellFoundedOrder : String := ""
  nonterminalEdgeCount : Nat := 0
  terminalEdgeCount : Nat := 0
  transitionEdgeCount : Nat := 0
  nondecreasingEdgeCount : Nat := 0
  unresolvedSccCount : Nat := 0
  edgeChecks : List RankedEdgeCheck := []
  sccChecks : List GuardedSccCheck := []
deriving Repr, DecidableEq, Inhabited

structure DescentImplicationCert where
  certificateId : String := ""
  certificateHash : String := ""
  certificateType : String := ""
  replayStatus : Bool := false
  strictReplay : Bool := false
  status : Bool := false
  descentTheoremStatement : String := ""
  collatzConjectureStatement : String := ""
  blockedByCount : Nat := 0
  baseCaseN : Nat := 0
  baseCaseReachesOne : Bool := false
  universalEntryHash : String := ""
  parentStateCoverageHash : String := ""
  transitionSoundnessHash : String := ""
  wellFoundedRankingHash : String := ""
deriving Repr, DecidableEq, Inhabited

structure TopLevelCertBundle where
  universalEntryHash : String
  parentStateCoverageHash : String
  transitionSoundnessHash : String
  wellFoundedRankingHash : String
  descentImplicationHash : String
  theoremStatement : String
  descentImplicationStatement : String
  acceptedNodeCount : Nat
  totalNodeCount : Nat
  openNodeCount : Nat
  universalEntry : UniversalEntryCert := {}
  parentStateCoverage : ParentStateCoverageCert := {}
  transitionSoundness : TransitionSoundnessCert := {}
  wellFoundedRanking : WellFoundedRankingCert := {}
  descentImplication : DescentImplicationCert := {}
deriving Repr, DecidableEq

structure Run024Manifest where
  s3DebtExactCerts : List S3DebtExactCert
  s4Certs : List S4TransitionCert
  s6Certs : List S6LemmaCert
  topLevel : TopLevelCertBundle
deriving Repr, DecidableEq

end Collatz
