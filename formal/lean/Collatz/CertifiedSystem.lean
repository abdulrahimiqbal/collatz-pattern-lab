import Collatz.Run051Data

/-!
Typed finite certificate-system vocabulary for RUN-053.

The structures in this file replace string-oriented semantic payloads with
finite typed IDs and numeric/checkable fields.  RUN-054 classifies reflected
edges by role and projects actual transition edges to concrete semantic
`SystemEdge` values.  RUN-056 adds the first non-empty global projection:
entry and coverage are now typed predicates over parent coordinates and the
coverage-domain map rather than `False`.
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
  sourceDepth : Nat
  sourceResidue : Nat
  mapA : Nat
  mapB : Nat
  mapD : Nat
  branchC : Nat
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
  nodeLevel : NodeId → Nat
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
        cert.sourceResidue < 2 ^ cert.sourceDepth ∧
        cert.mapA = 3 ^ cert.sourceParent ∧
        cert.mapB = 2 ^ cert.baseBurstDivisionExponent - 1 ∧
        cert.mapD = 2 ^ (cert.baseBurstDivisionExponent + cert.targetParent) ∧
        cert.mapA * cert.sourceResidue + cert.mapB =
          cert.branchC * 2 ^ cert.sourceDepth ∧
        cert.mapD = 2 ^ cert.sourceDepth * 2 ^ cert.valuation ∧
        ∃ q q' : Nat,
          q > 0 ∧
          q % 2 = 1 ∧
          q' > 0 ∧
          (∃ k : Nat, q = cert.sourceResidue + 2 ^ cert.sourceDepth * k) ∧
          cert.mapD * q' = cert.mapA * q + cert.mapB ∧
          state.node = { id := cert.sourceParent } ∧
          state.current = parentStateNat cert.sourceParent q ∧
          3 ^ cert.sourceParent * q - 1 =
          2 ^ cert.baseBurstDivisionExponent *
            parentStateNat cert.targetParent q',
    targetDomain := fun _state m =>
      ∃ q' : Nat, q' > 0 ∧ m = parentStateNat cert.targetParent q',
    exitCertificate := fun _ _ => False
  }

def CertifiedSystemBundle.edgeSystem {NodeId EdgeId CertId : Type}
    (bundle : CertifiedSystemBundle NodeId EdgeId CertId) (edge : EdgeId) :
    SystemEdge :=
  (bundle.edgeCert edge).toSystemEdge

def CoverageDomainCert.matchesLevel {CertId : Type}
    (domain : CoverageDomainCert CertId) (level : Nat) : Prop :=
  if domain.isResidual then
    domain.parentLevel = level
  else
    True

def CoverageDomainCert.coversQ {CertId : Type}
    (domain : CoverageDomainCert CertId) (q : Nat) : Prop :=
  domain.modulus > 0 ∧
  domain.residueStart ≤ q % domain.modulus ∧
  q % domain.modulus < domain.residueEndExclusive

def CoverageDomainCert.coversParentCoordinate {CertId : Type}
    (domain : CoverageDomainCert CertId) (level q : Nat) : Prop :=
  domain.matchesLevel level ∧ domain.coversQ q

def CoverageDomainCert.Universal {CertId : Type}
    (domain : CoverageDomainCert CertId) : Prop :=
  domain.isResidual = false ∧
  domain.modulus > 0 ∧
  domain.residueStart = 0 ∧
  domain.residueEndExclusive = domain.modulus

instance {CertId : Type} (domain : CoverageDomainCert CertId) :
    Decidable domain.Universal := by
  unfold CoverageDomainCert.Universal
  infer_instance

def checkUniversalCoverageDomain {CertId : Type}
    (domain : CoverageDomainCert CertId) : Bool :=
  decide domain.Universal

def CoverageCert.hasUniversalDomain {CertId : Type}
    (cert : CoverageCert CertId) : Bool :=
  cert.domains.any checkUniversalCoverageDomain

def CertifiedSystemBundle.hasSystemNode {NodeId EdgeId CertId : Type}
    (bundle : CertifiedSystemBundle NodeId EdgeId CertId)
    (node : SystemNode) : Prop :=
  ∃ nodeId ∈ bundle.nodes, bundle.nodeLevel nodeId = node.id

def CertifiedSystemBundle.coveredPredicate {NodeId EdgeId CertId : Type}
    (bundle : CertifiedSystemBundle NodeId EdgeId CertId)
    (state : InternalState) : Prop :=
  bundle.hasSystemNode state.node ∧
    ∃ q : Nat,
      q > 0 ∧
      state.current = parentStateNat state.node.id q ∧
      ∃ domain ∈ bundle.coverageCert.domains,
        domain.coversParentCoordinate state.node.id q

def CertifiedSystemBundle.entryPredicate {NodeId EdgeId CertId : Type}
    (bundle : CertifiedSystemBundle NodeId EdgeId CertId)
    (n : Nat) (state : InternalState) : Prop :=
  n > 1 ∧
  n % 2 ≠ 0 ∧
  state.root = n ∧
  state.current = n ∧
  bundle.hasSystemNode state.node ∧
  ∃ q : Nat,
    q > 0 ∧
    q % 2 = 1 ∧
    state.current = parentStateNat state.node.id q

def CertifiedSystemBundle.system {NodeId EdgeId CertId : Type}
    [DecidableEq EdgeId]
    (bundle : CertifiedSystemBundle NodeId EdgeId CertId) :
    CertifiedTransitionSystem :=
  {
    isEdge := fun edge =>
      ∃ edgeId : EdgeId,
        edgeId ∈ bundle.transitionEdges ∧
        edge = bundle.edgeSystem edgeId,
    entryState := bundle.entryPredicate,
    covered := bundle.coveredPredicate,
    rank := fun node => node.id
  }

def boolEq {α : Type} [DecidableEq α] (a b : α) : Bool :=
  decide (a = b)

end Collatz
