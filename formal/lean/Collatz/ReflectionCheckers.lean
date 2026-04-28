import Collatz.TransitionSemantics

/-!
Computable reflection checkers for typed finite RUN-053 bundles.

These checkers inspect finite typed fields.  RUN-054 supplies the transition
soundness bridge for actual reflected S4 transition edges; entry, coverage,
no-escape, and well-foundedness remain separate semantic obligations.
-/

namespace Collatz

namespace Reflection

variable {NodeId EdgeId CertId : Type}
variable [DecidableEq NodeId] [DecidableEq EdgeId] [DecidableEq CertId]

def checkCoverageDomain (domain : CoverageDomainCert CertId) : Bool :=
  decide (domain.modulus > 0) &&
  decide (domain.residueStart ≤ domain.residueEndExclusive) &&
  decide (domain.residueEndExclusive ≤ domain.modulus)

def checkS3RoleCert (role : S3RoleCert CertId NodeId) : Bool :=
  match role.role with
  | S3SemanticRole.supportingDebtEdge =>
      decide (role.gainDen > 0) && decide (role.gainNum < role.gainDen)
  | S3SemanticRole.rankingDecrease =>
      decide (role.gainDen > 0) && decide (role.gainNum < role.gainDen)
  | S3SemanticRole.directDescent =>
      false
  | S3SemanticRole.exitCertificate =>
      false

def checkS6Dependency (_dep : S6DependencyCert CertId) : Bool :=
  true

def checkS6ProofStep (step : S6ProofStepCert) : Bool :=
  decide (step.inputCount > 0)

def checkS6ProofTree (tree : S6ProofTreeCert CertId) : Bool :=
  tree.closesBlocker &&
  decide (tree.dependencies.length > 0) &&
  tree.dependencies.all checkS6Dependency &&
  decide (tree.proofSteps.length > 0) &&
  tree.proofSteps.all checkS6ProofStep

def checkEdgeCert
    (b : CertifiedSystemBundle NodeId EdgeId CertId) (edge : EdgeId) : Bool :=
  let cert := b.edgeCert edge
  boolEq cert.sourceNode (b.edgeSource edge) &&
  boolEq cert.targetNode (b.edgeTarget edge) &&
  match cert.kind with
  | EdgeKind.s4ParentTransition =>
      cert.hasIterateWitness &&
      decide (cert.standardStepCount > 0) &&
      decide (cert.sourceParent > 0) &&
      decide (cert.targetParent > 0)
  | EdgeKind.s3Debt =>
      decide (cert.gainDen > 0) &&
      decide (cert.gainNum < cert.gainDen) &&
      cert.rankingDecrease

def checkTransitionEdgeCert
    (b : CertifiedSystemBundle NodeId EdgeId CertId) (edge : EdgeId) : Bool :=
  let cert := b.edgeCert edge
  boolEq cert.sourceNode (b.edgeSource edge) &&
  boolEq cert.targetNode (b.edgeTarget edge) &&
  match cert.kind with
  | EdgeKind.s4ParentTransition =>
      decide (cert.role = EdgeRole.actualCollatzTransition) &&
      cert.hasIterateWitness &&
      decide (cert.standardStepCount = 2 * cert.sourceParent + cert.baseBurstDivisionExponent) &&
      decide (cert.standardStepCount > 0) &&
      decide (cert.sourceParent > 0) &&
      decide (cert.targetParent > 0)
  | EdgeKind.s3Debt =>
      false

def checkEntry (b : CertifiedSystemBundle NodeId EdgeId CertId) : Bool :=
  b.entryCert.evenDenominatorPositive &&
  b.entryCert.evenStrictDescentForKGeOne &&
  b.entryCert.oddExactReconstruction &&
  b.entryCert.oddNPlusOnePositive &&
  b.entryCert.oddQuotientAfterV2 &&
  b.entryCert.oddPowerTwoDivides

def checkCoverage (b : CertifiedSystemBundle NodeId EdgeId CertId) : Bool :=
  b.coverageCert.noUncoveredDomains &&
  b.coverageCert.hasResidualDomain &&
  decide (b.coverageCert.domains.length > 0) &&
  b.coverageCert.domains.all checkCoverageDomain

def checkTransitionSoundness
    (b : CertifiedSystemBundle NodeId EdgeId CertId) : Bool :=
  b.transitionEdges.all (checkTransitionEdgeCert b) &&
  checkAllS4ParentMapCerts b.s4Certs &&
  checkAllS6LemmaCerts b.s6Certs

def checkNoEscape (b : CertifiedSystemBundle NodeId EdgeId CertId) : Bool :=
  decide (b.noEscapeCert.noEscapeTreeCount > 0) &&
  b.noEscapeCert.proofTrees.all checkS6ProofTree &&
  b.s6ProofTrees.all checkS6ProofTree

def edgeRankOrGuarded
    (b : CertifiedSystemBundle NodeId EdgeId CertId) (edge : EdgeId) : Bool :=
  let cert := b.edgeCert edge
  match cert.kind with
  | EdgeKind.s3Debt => cert.rankingDecrease
  | EdgeKind.s4ParentTransition =>
      decide (b.nodeRank (b.edgeTarget edge) < b.nodeRank (b.edgeSource edge)) ||
      (cert.guardedKernel &&
        b.kernelCert.kernelCongruenceDepthUnbounded &&
        b.kernelCert.thereforeNoPositiveIntegerQInKernel)

def checkWellFounded (b : CertifiedSystemBundle NodeId EdgeId CertId) : Bool :=
  b.wellFoundedCert.unresolvedSccCount == 0 &&
  decide (b.wellFoundedCert.rankedEdges.length > 0) &&
  b.wellFoundedCert.rankedEdges.all (edgeRankOrGuarded b) &&
  checkAllS3DebtExactCerts b.s3Certs &&
  b.s3Roles.all checkS3RoleCert

def checkDescentImplication
    (b : CertifiedSystemBundle NodeId EdgeId CertId) : Bool :=
  b.descentImplicationCert.blockedByCount == 0 &&
  b.descentImplicationCert.baseCaseN == 1 &&
  b.descentImplicationCert.baseCaseReachesOne

def checkCertifiedSystemBundle
    (b : CertifiedSystemBundle NodeId EdgeId CertId) : Bool :=
  checkEntry b &&
  checkCoverage b &&
  checkTransitionSoundness b &&
  checkNoEscape b &&
  checkWellFounded b &&
  checkDescentImplication b

omit [DecidableEq CertId] in
theorem checkTransitionSoundness_sound
    (b : CertifiedSystemBundle NodeId EdgeId CertId) :
    checkTransitionSoundness b = true →
    TransitionSoundnessSemantics b.system := by
  intro _hcheck edge hedge
  rcases hedge with ⟨edgeId, _hedge_mem, hedge_eq⟩
  rw [hedge_eq]
  exact EdgeCert.toSystemEdge_semantics (b.edgeCert edgeId)

def MissingReflectionSoundnessTheorems : List String :=
  [
    "checkEntry_sound: MISSING_ENTRY_TO_COVERAGE_LINK; reflected entry booleans must construct UniversalEntrySemantics b.system, but the current system projection has no entry states",
    "checkCoverage_sound: MISSING_COVERAGE_DOMAIN_MEMBERSHIP_THEOREM; typed coverage domains must construct CoverageSemantics b.system",
    "checkNoEscape_sound: MISSING_NO_ESCAPE_PROOF_TREE_SEMANTICS; typed S6 no-escape proof trees must construct NoEscapeSemantics b.system",
    "checkWellFounded_sound: MISSING_KERNEL_TO_PATH_LINK / MISSING_WELL_FOUNDED_RANK_BRIDGE; ranked and guarded-kernel reflected edges must construct WellFoundedSystem b.system"
  ]

end Reflection

end Collatz
