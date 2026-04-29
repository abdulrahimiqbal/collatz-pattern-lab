import Collatz.ReflectionCheckers

/-!
Global semantic projection facts for the reflected RUN-051 transition system.

RUN-056 replaces the empty `entryState`/`covered` projection with typed
predicates.  This module records what the new projection actually means.  It
does not claim the remaining RUN-057/RUN-058/RUN-059 soundness theorems.
-/

namespace Collatz

namespace GlobalSemantics

variable {NodeId EdgeId CertId : Type}
variable [DecidableEq NodeId] [DecidableEq EdgeId] [DecidableEq CertId]

theorem bool_and_true_right {a b : Bool} :
    a && b = true → b = true := by
  cases a <;> cases b <;> simp

theorem bool_and_true_left {a b : Bool} :
    a && b = true → a = true := by
  cases a <;> cases b <;> simp

theorem list_any_decide_exists {α : Type} (p : α → Prop)
    [DecidablePred p] :
    ∀ xs : List α,
      xs.any (fun x => decide (p x)) = true →
      ∃ x ∈ xs, p x
  | [], h => by simp at h
  | x :: xs, h => by
      by_cases hx : p x
      · exact ⟨x, by simp, hx⟩
      · have htail : xs.any (fun x => decide (p x)) = true := by
          simpa [List.any, hx] using h
        obtain ⟨y, hy_mem, hy⟩ :=
          list_any_decide_exists p xs htail
        exact ⟨y, by simp [hy_mem], hy⟩

omit [DecidableEq CertId] in
theorem hasUniversalDomain_sound
    (cert : CoverageCert CertId) :
    cert.hasUniversalDomain = true →
    ∃ domain ∈ cert.domains, domain.Universal := by
  intro h
  simpa [CoverageCert.hasUniversalDomain, checkUniversalCoverageDomain] using
    (list_any_decide_exists
      (fun domain : CoverageDomainCert CertId => domain.Universal)
      cert.domains
      h)

omit [DecidableEq CertId] in
theorem CoverageDomainCert.universal_coversParentCoordinate
    {domain : CoverageDomainCert CertId}
    (hdomain : domain.Universal)
    (level q : Nat) :
    domain.coversParentCoordinate level q := by
  rcases hdomain with ⟨hresidual, hmod, hstart, hend⟩
  constructor
  · simp [CoverageDomainCert.matchesLevel, hresidual]
  · constructor
    · exact hmod
    · constructor
      · rw [hstart]
        exact Nat.zero_le _
      · rw [hend]
        exact Nat.mod_lt q hmod

omit [DecidableEq EdgeId] [DecidableEq CertId] in
theorem checkCoverage_hasUniversalDomain
    (b : CertifiedSystemBundle NodeId EdgeId CertId) :
    Reflection.checkCoverage b = true →
    b.coverageCert.hasUniversalDomain = true := by
  intro h
  have hsimp : (Reflection.checkCertifiedCoverageMap b = true ∧
      b.coverageCert.hasUniversalDomain = true) ∧
      ((((b.coverageCert.noUncoveredDomains = true ∧
          b.coverageCert.hasResidualDomain = true) ∧
          0 < b.coverageCert.domains.length) ∧
          (∀ domain ∈ b.coverageCert.domains,
            Reflection.checkCoverageDomain domain = true)) ∧
          (∀ edgeId ∈ b.transitionEdges,
            b.edgeTarget edgeId ∈ b.nodes ∧
              b.nodeLevel (b.edgeTarget edgeId) =
                (b.edgeSystem edgeId).target.id)) := by
    simpa [Reflection.checkCoverage, Reflection.checkTransitionTargetNode] using h
  exact hsimp.1.2

omit [DecidableEq EdgeId] [DecidableEq CertId] in
theorem checkCoverage_targetsInNodes
    (b : CertifiedSystemBundle NodeId EdgeId CertId) :
    Reflection.checkCoverage b = true →
    ∀ edgeId ∈ b.transitionEdges,
      b.edgeTarget edgeId ∈ b.nodes ∧
        b.nodeLevel (b.edgeTarget edgeId) = (b.edgeSystem edgeId).target.id := by
  intro h
  have hsimp : (Reflection.checkCertifiedCoverageMap b = true ∧
      b.coverageCert.hasUniversalDomain = true) ∧
      ((((b.coverageCert.noUncoveredDomains = true ∧
          b.coverageCert.hasResidualDomain = true) ∧
          0 < b.coverageCert.domains.length) ∧
          (∀ domain ∈ b.coverageCert.domains,
            Reflection.checkCoverageDomain domain = true)) ∧
          (∀ edgeId ∈ b.transitionEdges,
            b.edgeTarget edgeId ∈ b.nodes ∧
              b.nodeLevel (b.edgeTarget edgeId) =
                (b.edgeSystem edgeId).target.id)) := by
    simpa [Reflection.checkCoverage, Reflection.checkTransitionTargetNode] using h
  exact hsimp.2.2

def EntryProjectionBuilt
    (b : CertifiedSystemBundle NodeId EdgeId CertId) : Prop :=
  ∀ n state,
    b.system.entryState n state →
      n > 1 ∧
        n % 2 ≠ 0 ∧
        state.root = n ∧
        state.current = n ∧
        b.hasSystemNode state.node ∧
        ∃ q : Nat,
          q > 0 ∧
          q % 2 = 1 ∧
          state.current = parentStateNat state.node.id q

def CoveredProjectionBuilt
    (b : CertifiedSystemBundle NodeId EdgeId CertId) : Prop :=
    ∀ state,
      b.system.covered state →
        b.hasSystemNode state.node ∧
        ∃ q : Nat,
          q > 0 ∧
          state.current = parentStateNat state.node.id q ∧
        ∃ domain ∈ b.coverageCert.domains,
          domain.coversParentCoordinate state.node.id q

omit [DecidableEq NodeId] [DecidableEq CertId] in
theorem entry_projection_built
    (b : CertifiedSystemBundle NodeId EdgeId CertId) :
    EntryProjectionBuilt b := by
  intro n state hentry
  change b.entryPredicate n state at hentry
  exact hentry

omit [DecidableEq NodeId] [DecidableEq CertId] in
theorem covered_projection_built
    (b : CertifiedSystemBundle NodeId EdgeId CertId) :
    CoveredProjectionBuilt b := by
  intro state hcovered
  change b.coveredPredicate state at hcovered
  exact hcovered

end GlobalSemantics

namespace Reflection

variable {NodeId EdgeId CertId : Type}
variable [DecidableEq NodeId] [DecidableEq EdgeId] [DecidableEq CertId]

omit [DecidableEq NodeId] [DecidableEq CertId] in
theorem checkEntry_sound
    (b : CertifiedSystemBundle NodeId EdgeId CertId) :
    checkEntry b = true →
    UniversalEntrySemantics b.system := by
  intro hcheck
  simp [checkEntry, checkCertifiedEntryMap] at hcheck

omit [DecidableEq CertId] in
theorem checkCoverage_sound
    (b : CertifiedSystemBundle NodeId EdgeId CertId) :
    checkCoverage b = true →
    CoverageSemantics b.system := by
  intro hcheck
  simp [checkCoverage, checkCertifiedCoverageMap] at hcheck

end Reflection

namespace GlobalSemantics

def MissingGlobalSemanticsGaps : List String :=
  [
    "MISSING_ENTRY_TO_CERTIFIED_NODE_MAP: RUN-051 does not provide a Lean-checkable map from arbitrary odd n via v2(n+1) into the finite generated NodeId/domain set.",
    "MISSING_COVERAGE_DOMAIN_MEMBERSHIP_THEOREM: RUN-051 does not provide a Lean-checkable coverage-domain map beyond structural domain metadata.",
    "MISSING_NO_ESCAPE_PROOF_TREE_SEMANTICS: S6 proof trees validate typed dependency shapes, but do not construct NoEscapeSemantics for covered states.",
    "MISSING_KERNEL_TO_PATH_LINK: the natural-kernel payload validates the divisibility story, but does not map every infinite internal path in b.system into that kernel.",
    "MISSING_WELL_FOUNDED_RANK_BRIDGE: checkWellFounded accepts ranked or guarded edges, but no theorem turns those checks into WellFoundedSystem b.system."
  ]

end GlobalSemantics

end Collatz
