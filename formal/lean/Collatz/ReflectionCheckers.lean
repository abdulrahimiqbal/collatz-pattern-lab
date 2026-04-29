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

def checkS6Dependency
    (b : CertifiedSystemBundle NodeId EdgeId CertId)
    (expectedClaim : S6ClaimKind)
    (dep : S6DependencyCert CertId) : Bool :=
  decide (dep.certId ∈ b.certs) &&
  decide (dep.claimKind = expectedClaim)

def checkS6ProofStep (step : S6ProofStepCert) : Bool :=
  decide (step.inputCount > 0)

def proofRuleClosesClaim (rule : ProofRule) (claim : S6ClaimKind) : Prop :=
  match claim, rule with
  | S6ClaimKind.coverage, ProofRule.applyCoverage => True
  | S6ClaimKind.coverage, ProofRule.applyResidualParent => True
  | S6ClaimKind.noEscape, ProofRule.applyNoEscape => True
  | S6ClaimKind.noEscape, ProofRule.composeTransition => True
  | S6ClaimKind.induction, ProofRule.applyInduction => True
  | S6ClaimKind.induction, ProofRule.applyRanking => True
  | S6ClaimKind.ranking, ProofRule.applyRanking => True
  | S6ClaimKind.ranking, ProofRule.applyInduction => True
  | S6ClaimKind.transitionComposition, ProofRule.composeTransition => True
  | S6ClaimKind.residualParent, ProofRule.applyResidualParent => True
  | S6ClaimKind.residualParent, ProofRule.applyCoverage => True
  | _, _ => False

instance (rule : ProofRule) (claim : S6ClaimKind) :
    Decidable (proofRuleClosesClaim rule claim) := by
  cases claim <;> cases rule <;> simp [proofRuleClosesClaim] <;> infer_instance

def checkS6ClosingStep (claim : S6ClaimKind) (step : S6ProofStepCert) : Bool :=
  checkS6ProofStep step && decide (proofRuleClosesClaim step.rule claim)

def checkS6ProofTree
    (b : CertifiedSystemBundle NodeId EdgeId CertId)
    (tree : S6ProofTreeCert CertId) : Bool :=
  tree.closesBlocker &&
  decide (tree.dependencies.length > 0) &&
  tree.dependencies.all (checkS6Dependency b tree.claimKind) &&
  decide (tree.proofSteps.length > 0) &&
  tree.proofSteps.all checkS6ProofStep &&
  tree.proofSteps.any (checkS6ClosingStep tree.claimKind)

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

def checkCertifiedEntryMap (_b : CertifiedSystemBundle NodeId EdgeId CertId) : Bool :=
  false

def checkCertifiedCoverageMap (_b : CertifiedSystemBundle NodeId EdgeId CertId) : Bool :=
  false

def checkTransitionTargetNode
    (b : CertifiedSystemBundle NodeId EdgeId CertId) (edge : EdgeId) : Bool :=
  decide (b.edgeTarget edge ∈ b.nodes) &&
  decide (b.nodeLevel (b.edgeTarget edge) = (b.edgeSystem edge).target.id)

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
        decide (cert.sourceResidue < 2 ^ cert.sourceDepth) &&
        decide (cert.mapA = 3 ^ cert.sourceParent) &&
        decide (cert.mapB = 2 ^ cert.baseBurstDivisionExponent - 1) &&
        decide (cert.mapD = 2 ^ (cert.baseBurstDivisionExponent + cert.targetParent)) &&
        decide (cert.mapA * cert.sourceResidue + cert.mapB =
          cert.branchC * 2 ^ cert.sourceDepth) &&
        decide (cert.mapD = 2 ^ cert.sourceDepth * 2 ^ cert.valuation) &&
        decide (cert.standardStepCount > 0) &&
        decide (cert.sourceParent > 0) &&
        decide (cert.targetParent > 0)
  | EdgeKind.s3Debt =>
      false

def checkEntry (b : CertifiedSystemBundle NodeId EdgeId CertId) : Bool :=
  checkCertifiedEntryMap b &&
  (
    b.entryCert.evenDenominatorPositive &&
    b.entryCert.evenStrictDescentForKGeOne &&
    b.entryCert.oddExactReconstruction &&
    b.entryCert.oddNPlusOnePositive &&
    b.entryCert.oddQuotientAfterV2 &&
    b.entryCert.oddPowerTwoDivides
  )

def checkCoverage (b : CertifiedSystemBundle NodeId EdgeId CertId) : Bool :=
  checkCertifiedCoverageMap b &&
  b.coverageCert.hasUniversalDomain &&
  (
      b.coverageCert.noUncoveredDomains &&
      b.coverageCert.hasResidualDomain &&
      decide (b.coverageCert.domains.length > 0) &&
      b.coverageCert.domains.all checkCoverageDomain &&
      b.transitionEdges.all (checkTransitionTargetNode b)
    )

def checkTransitionSoundness
    (b : CertifiedSystemBundle NodeId EdgeId CertId) : Bool :=
  b.transitionEdges.all (checkTransitionEdgeCert b) &&
  checkAllS4ParentMapCerts b.s4Certs &&
  checkAllS6LemmaCerts b.s6Certs

def checkNoEscape (b : CertifiedSystemBundle NodeId EdgeId CertId) : Bool :=
  decide (b.noEscapeCert.noEscapeTreeCount > 0) &&
  b.noEscapeCert.proofTrees.all (checkS6ProofTree b) &&
  b.s6ProofTrees.all (checkS6ProofTree b)

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

def S6DependencySemantics
    (b : CertifiedSystemBundle NodeId EdgeId CertId)
    (expectedClaim : S6ClaimKind)
    (dep : S6DependencyCert CertId) : Prop :=
  dep.certId ∈ b.certs ∧ dep.claimKind = expectedClaim

def S6ProofStepSemantics (step : S6ProofStepCert) : Prop :=
  step.inputCount > 0

def S6ClosingStepSemantics
    (claim : S6ClaimKind) (step : S6ProofStepCert) : Prop :=
  S6ProofStepSemantics step ∧ proofRuleClosesClaim step.rule claim

def S6ProofTreeSemantics
    (b : CertifiedSystemBundle NodeId EdgeId CertId)
    (tree : S6ProofTreeCert CertId) : Prop :=
  tree.closesBlocker = true ∧
  tree.dependencies.length > 0 ∧
  (∀ dep ∈ tree.dependencies,
    S6DependencySemantics b tree.claimKind dep) ∧
  tree.proofSteps.length > 0 ∧
  (∀ step ∈ tree.proofSteps, S6ProofStepSemantics step) ∧
  ∃ step ∈ tree.proofSteps, S6ClosingStepSemantics tree.claimKind step

def S3RoleSupportSemantics (role : S3RoleCert CertId NodeId) : Prop :=
  (role.role = S3SemanticRole.supportingDebtEdge ∨
    role.role = S3SemanticRole.rankingDecrease) ∧
  role.gainDen > 0 ∧
  role.gainNum < role.gainDen

def DescentImplicationMetadata
    (b : CertifiedSystemBundle NodeId EdgeId CertId) : Prop :=
  b.descentImplicationCert.blockedByCount = 0 ∧
  b.descentImplicationCert.baseCaseN = 1 ∧
  b.descentImplicationCert.baseCaseReachesOne = true

omit [DecidableEq NodeId] [DecidableEq CertId] in
theorem checkS3RoleCert_sound
    (role : S3RoleCert CertId NodeId) :
    checkS3RoleCert role = true →
    S3RoleSupportSemantics role := by
  intro h
  cases hrole : role.role <;>
    simp [checkS3RoleCert, S3RoleSupportSemantics, hrole] at h ⊢
  · exact h
  · exact h

omit [DecidableEq NodeId] [DecidableEq EdgeId] [DecidableEq CertId] in
theorem checkDescentImplication_sound
    (b : CertifiedSystemBundle NodeId EdgeId CertId) :
    checkDescentImplication b = true →
    DescentImplicationMetadata b := by
  intro h
  unfold checkDescentImplication at h
  unfold DescentImplicationMetadata
  simp at h
  exact ⟨h.1.1, h.1.2, h.2⟩

omit [DecidableEq NodeId] [DecidableEq EdgeId] in
theorem checkS6Dependency_sound
    (b : CertifiedSystemBundle NodeId EdgeId CertId)
    (expectedClaim : S6ClaimKind)
    (dep : S6DependencyCert CertId) :
    checkS6Dependency b expectedClaim dep = true →
    S6DependencySemantics b expectedClaim dep := by
  intro h
  simpa [checkS6Dependency, S6DependencySemantics] using h

theorem checkS6ProofStep_sound
    (step : S6ProofStepCert) :
    checkS6ProofStep step = true →
    S6ProofStepSemantics step := by
  intro h
  simpa [checkS6ProofStep, S6ProofStepSemantics] using h

theorem checkS6ClosingStep_sound
    (claim : S6ClaimKind) (step : S6ProofStepCert) :
    checkS6ClosingStep claim step = true →
    S6ClosingStepSemantics claim step := by
  intro h
  simpa [
    checkS6ClosingStep,
    checkS6ProofStep,
    S6ClosingStepSemantics,
    S6ProofStepSemantics
  ] using h

theorem list_any_checkS6ClosingStep_sound
    (claim : S6ClaimKind) :
    ∀ steps : List S6ProofStepCert,
      steps.any (checkS6ClosingStep claim) = true →
      ∃ step ∈ steps, S6ClosingStepSemantics claim step
  | [], h => by simp at h
  | step :: steps, h => by
      by_cases hstep : checkS6ClosingStep claim step = true
      · exact ⟨step, by simp, checkS6ClosingStep_sound claim step hstep⟩
      · have htail : steps.any (checkS6ClosingStep claim) = true := by
          have hraw : checkS6ClosingStep claim step = false := by
            cases hraw : checkS6ClosingStep claim step <;>
              simp [hraw] at hstep ⊢
          simpa [List.any, hraw] using h
        obtain ⟨found, hfound_mem, hfound⟩ :=
          list_any_checkS6ClosingStep_sound claim steps htail
        exact ⟨found, by simp [hfound_mem], hfound⟩

omit [DecidableEq NodeId] [DecidableEq EdgeId] in
theorem checkS6ProofTree_sound
    (b : CertifiedSystemBundle NodeId EdgeId CertId)
    (tree : S6ProofTreeCert CertId) :
    checkS6ProofTree b tree = true →
    S6ProofTreeSemantics b tree := by
  intro h
  have hsimp := (by
    simpa [
      checkS6ProofTree,
      checkS6Dependency,
      checkS6ProofStep,
      S6DependencySemantics,
      S6ProofStepSemantics
    ] using h)
  rcases hsimp with
    ⟨⟨⟨⟨⟨hcloses, hdepsLen⟩, hdeps⟩, hstepsLen⟩, hsteps⟩, hclosing⟩
  obtain ⟨closingStep, hclosing_mem, hclosing_check⟩ := hclosing
  exact
    ⟨hcloses, hdepsLen, hdeps, hstepsLen, hsteps,
      closingStep, hclosing_mem,
      checkS6ClosingStep_sound tree.claimKind closingStep hclosing_check⟩

def MissingReflectionSoundnessTheorems : List String :=
  [
    "checkNoEscape_sound: MISSING_NO_ESCAPE_PROOF_TREE_SEMANTICS; typed S6 no-escape proof trees must construct NoEscapeSemantics b.system",
    "checkWellFounded_sound: MISSING_KERNEL_TO_PATH_LINK / MISSING_WELL_FOUNDED_RANK_BRIDGE; ranked and guarded-kernel reflected edges must construct WellFoundedSystem b.system"
  ]

end Reflection

end Collatz
