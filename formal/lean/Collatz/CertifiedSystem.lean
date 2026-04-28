import Collatz.Run051Data

/-!
Typed finite certificate-system vocabulary for RUN-053.

The structures in this file replace string-oriented semantic payloads with
finite typed IDs and numeric/checkable fields.  RUN-054 classifies reflected
edges by role and projects actual transition edges to concrete semantic
`SystemEdge` values.
-/

namespace Collatz

inductive EdgeKind where
  | s3Debt
  | s4ParentTransition
deriving Repr, DecidableEq

inductive EdgeRole where
  | actualCollatzTransition
  | directDescentEdge
  | rankingSupportOnly
  | coverageOnly
  | noEscapeOnly
  | s6ProofTreeOnly
deriving Repr, DecidableEq

inductive S6ClaimKind where
  | coverage
  | noEscape
  | induction
  | ranking
  | transitionComposition
  | residualParent
deriving Repr, DecidableEq

inductive DependencyKind where
  | s3Debt
  | s4ParentMap
  | residualParent
  | coverage
  | noEscape
  | naturalKernel
  | topLevel
deriving Repr, DecidableEq

inductive ProofRule where
  | composeTransition
  | applyCoverage
  | applyNoEscape
  | applyRanking
  | applyInduction
  | applyResidualParent
deriving Repr, DecidableEq

structure EdgeCert (CertId NodeId : Type) where
  certId : CertId
  kind : EdgeKind
  role : EdgeRole
  sourceNode : NodeId
  targetNode : NodeId
  sourceParent : Nat
  targetParent : Nat
  valuation : Nat
  baseBurstDivisionExponent : Nat
  standardStepCount : Nat
  gainNum : Nat
  gainDen : Nat
  hasIterateWitness : Bool
  rankingDecrease : Bool
  guardedKernel : Bool
deriving Repr

structure S3RoleCert (CertId NodeId : Type) where
  certId : CertId
  role : S3SemanticRole
  sourceNode : NodeId
  targetNode : NodeId
  gainNum : Nat
  gainDen : Nat
  consumedByCount : Nat
deriving Repr

structure S6DependencyCert (CertId : Type) where
  certId : CertId
  kind : DependencyKind
  claimKind : S6ClaimKind
deriving Repr

structure S6ProofStepCert where
  rule : ProofRule
  inputCount : Nat
deriving Repr, DecidableEq

structure S6ProofTreeCert (CertId : Type) where
  certId : CertId
  claimKind : S6ClaimKind
  dependencies : List (S6DependencyCert CertId)
  proofSteps : List S6ProofStepCert
  closesBlocker : Bool
deriving Repr

structure CoverageDomainCert (CertId : Type) where
  certId : CertId
  modulus : Nat
  residueStart : Nat
  residueEndExclusive : Nat
  parentLevel : Nat
  isResidual : Bool
deriving Repr

structure CoverageCert (CertId : Type) where
  domains : List (CoverageDomainCert CertId)
  noUncoveredDomains : Bool
  hasResidualDomain : Bool
deriving Repr

structure NoEscapeCert (CertId : Type) where
  proofTrees : List (S6ProofTreeCert CertId)
  noEscapeTreeCount : Nat
deriving Repr

structure WellFoundedCert (CertId EdgeId : Type) where
  rankedEdges : List EdgeId
  guardedKernelCertId : CertId
  unresolvedSccCount : Nat
deriving Repr

structure DescentBridgeCert (CertId : Type) where
  certId : CertId
  blockedByCount : Nat
  baseCaseN : Nat
  baseCaseReachesOne : Bool
deriving Repr

structure CertifiedSystemBundle (NodeId EdgeId CertId : Type) where
  nodes : List NodeId
  edges : List EdgeId
  supportEdges : List EdgeId
  transitionEdges : List EdgeId
  certs : List CertId
  edgeSource : EdgeId → NodeId
  edgeTarget : EdgeId → NodeId
  edgeCert : EdgeId → EdgeCert CertId NodeId
  nodeRank : NodeId → Nat
  entryCert : UniversalEntryCert
  coverageCert : CoverageCert CertId
  transitionSoundnessCert : TransitionSoundnessCert
  noEscapeCert : NoEscapeCert CertId
  wellFoundedCert : WellFoundedCert CertId EdgeId
  descentImplicationCert : DescentBridgeCert CertId
  s3Certs : List S3DebtExactCert
  s4Certs : List S4ParentMapCert
  s6Certs : List S6LemmaCert
  kernelCert : NaturalViabilityKernelCert
  s3Roles : List (S3RoleCert CertId NodeId)
  s6ProofTrees : List (S6ProofTreeCert CertId)

def EdgeCert.toSystemEdge {CertId NodeId : Type}
    (cert : EdgeCert CertId NodeId) : SystemEdge :=
  {
    id := cert.sourceParent * 1000 + cert.targetParent,
    source := { id := cert.sourceParent },
    target := { id := cert.targetParent },
    sourceDomain := fun state =>
      cert.sourceParent > 0 ∧
      ∃ q q' : Nat,
        q > 0 ∧
        state.node = { id := cert.sourceParent } ∧
        state.current = parentStateNat cert.sourceParent q ∧
        3 ^ cert.sourceParent * q - 1 =
          2 ^ cert.baseBurstDivisionExponent *
            parentStateNat cert.targetParent q',
    targetDomain := fun _state m =>
      ∃ q' : Nat, m = parentStateNat cert.targetParent q',
    exitCertificate := fun _ _ => False
  }

def CertifiedSystemBundle.edgeSystem {NodeId EdgeId CertId : Type}
    (bundle : CertifiedSystemBundle NodeId EdgeId CertId) (edge : EdgeId) :
    SystemEdge :=
  (bundle.edgeCert edge).toSystemEdge

def CertifiedSystemBundle.system {NodeId EdgeId CertId : Type}
    [DecidableEq EdgeId]
    (bundle : CertifiedSystemBundle NodeId EdgeId CertId) :
    CertifiedTransitionSystem :=
  {
    isEdge := fun edge =>
      ∃ edgeId : EdgeId,
        edgeId ∈ bundle.transitionEdges ∧
        edge = bundle.edgeSystem edgeId,
    entryState := fun _ _ => False,
    covered := fun _ => False,
    rank := fun node => node.id
  }

def boolEq {α : Type} [DecidableEq α] (a b : α) : Bool :=
  decide (a = b)

end Collatz
