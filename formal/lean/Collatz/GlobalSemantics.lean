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

omit [DecidableEq NodeId] [DecidableEq EdgeId] [DecidableEq CertId] in
theorem checkEntry_hasUniversalDomain
    (b : CertifiedSystemBundle NodeId EdgeId CertId) :
    Reflection.checkEntry b = true →
    b.coverageCert.hasUniversalDomain = true := by
  intro h
  have h' :
      b.coverageCert.hasUniversalDomain &&
        (
          b.entryCert.evenDenominatorPositive &&
          b.entryCert.evenStrictDescentForKGeOne &&
          b.entryCert.oddExactReconstruction &&
          b.entryCert.oddNPlusOnePositive &&
          b.entryCert.oddQuotientAfterV2 &&
          b.entryCert.oddPowerTwoDivides
        ) = true := by
    simpa [Reflection.checkEntry] using h
  exact bool_and_true_left h'

omit [DecidableEq NodeId] [DecidableEq EdgeId] [DecidableEq CertId] in
theorem checkCoverage_hasUniversalDomain
    (b : CertifiedSystemBundle NodeId EdgeId CertId) :
    Reflection.checkCoverage b = true →
    b.coverageCert.hasUniversalDomain = true := by
  intro h
  have h' :
      b.coverageCert.hasUniversalDomain &&
        (
          b.coverageCert.noUncoveredDomains &&
          b.coverageCert.hasResidualDomain &&
          decide (b.coverageCert.domains.length > 0) &&
          b.coverageCert.domains.all Reflection.checkCoverageDomain
        ) = true := by
    simpa [Reflection.checkCoverage] using h
  exact bool_and_true_left h'

def EntryProjectionBuilt
    (b : CertifiedSystemBundle NodeId EdgeId CertId) : Prop :=
  ∀ n state,
    b.system.entryState n state →
      n > 1 ∧
      n % 2 ≠ 0 ∧
      state.root = n ∧
      state.current = n ∧
      ∃ q : Nat,
        q > 0 ∧
        state.node = { id := 0 } ∧
        state.current = parentStateNat 0 q

def CoveredProjectionBuilt
    (b : CertifiedSystemBundle NodeId EdgeId CertId) : Prop :=
  ∀ state,
    b.system.covered state →
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
  simpa [
    EntryProjectionBuilt,
    CertifiedSystemBundle.system,
    CertifiedSystemBundle.entryPredicate
  ] using hentry

omit [DecidableEq NodeId] [DecidableEq CertId] in
theorem covered_projection_built
    (b : CertifiedSystemBundle NodeId EdgeId CertId) :
    CoveredProjectionBuilt b := by
  intro state hcovered
  simpa [
    CoveredProjectionBuilt,
    CertifiedSystemBundle.system,
    CertifiedSystemBundle.coveredPredicate
  ] using hcovered

end GlobalSemantics

namespace Reflection

variable {NodeId EdgeId CertId : Type}
variable [DecidableEq NodeId] [DecidableEq EdgeId] [DecidableEq CertId]

omit [DecidableEq NodeId] [DecidableEq CertId] in
theorem checkEntry_sound
    (b : CertifiedSystemBundle NodeId EdgeId CertId) :
    checkEntry b = true →
    UniversalEntrySemantics b.system := by
  intro hcheck n hn hodd
  have hunivBool :
      b.coverageCert.hasUniversalDomain = true :=
    GlobalSemantics.checkEntry_hasUniversalDomain b hcheck
  obtain ⟨domain, hdomain_mem, hdomain_univ⟩ :=
    GlobalSemantics.hasUniversalDomain_sound b.coverageCert hunivBool
  let state : InternalState := { node := { id := 0 }, root := n, current := n }
  refine ⟨state, ?_, rfl, rfl, ?_⟩
  · change b.entryPredicate n state
    unfold CertifiedSystemBundle.entryPredicate
    refine ⟨hn, hodd, rfl, rfl, n + 1, by omega, rfl, ?_⟩
    dsimp [state]
    unfold parentStateNat
    omega
  · change b.coveredPredicate state
    unfold CertifiedSystemBundle.coveredPredicate
    refine ⟨n + 1, by omega, ?_, domain, hdomain_mem, ?_⟩
    · dsimp [state]
      unfold parentStateNat
      omega
    · exact
        GlobalSemantics.CoverageDomainCert.universal_coversParentCoordinate
          hdomain_univ 0 (n + 1)

omit [DecidableEq NodeId] [DecidableEq CertId] in
theorem checkCoverage_sound
    (b : CertifiedSystemBundle NodeId EdgeId CertId) :
    checkCoverage b = true →
    CoverageSemantics b.system := by
  intro hcheck edge state m hedge _hcovered _hsource htarget
  have hunivBool :
      b.coverageCert.hasUniversalDomain = true :=
    GlobalSemantics.checkCoverage_hasUniversalDomain b hcheck
  obtain ⟨domain, hdomain_mem, hdomain_univ⟩ :=
    GlobalSemantics.hasUniversalDomain_sound b.coverageCert hunivBool
  rcases hedge with ⟨edgeId, _hedge_mem, hedge_eq⟩
  subst edge
  rcases htarget with ⟨q', hq'_pos, hm⟩
  change b.coveredPredicate ((b.edgeSystem edgeId).targetState state m)
  unfold CertifiedSystemBundle.coveredPredicate
  refine ⟨q', hq'_pos, ?_, domain, hdomain_mem, ?_⟩
  · dsimp [SystemEdge.targetState]
    exact hm
  · exact
      GlobalSemantics.CoverageDomainCert.universal_coversParentCoordinate
        hdomain_univ (b.edgeSystem edgeId).target.id q'

end Reflection

namespace GlobalSemantics

def MissingGlobalSemanticsGaps : List String :=
  [
    "MISSING_NO_ESCAPE_PROOF_TREE_SEMANTICS: S6 proof trees validate typed dependency shapes, but do not construct NoEscapeSemantics for covered states.",
    "MISSING_KERNEL_TO_PATH_LINK: the natural-kernel payload validates the divisibility story, but does not map every infinite internal path in b.system into that kernel.",
    "MISSING_WELL_FOUNDED_RANK_BRIDGE: checkWellFounded accepts ranked or guarded edges, but no theorem turns those checks into WellFoundedSystem b.system."
  ]

end GlobalSemantics

end Collatz
