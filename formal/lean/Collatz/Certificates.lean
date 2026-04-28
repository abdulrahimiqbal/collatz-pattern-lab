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
deriving Repr, DecidableEq

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
deriving Repr, DecidableEq

structure Run024Manifest where
  s3DebtExactCerts : List S3DebtExactCert
  s4Certs : List S4TransitionCert
  s6Certs : List S6LemmaCert
  topLevel : TopLevelCertBundle
deriving Repr, DecidableEq

end Collatz
