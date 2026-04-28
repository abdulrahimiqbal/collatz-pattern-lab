import Collatz.ParentState

/-!
Abstract transition-system semantics for certificate replay.

This file is deliberately independent of RUN-specific data.  It proves the
central bridge: if a certified parent-state transition system has semantic
entry, coverage, sound edges, no escape, and a decreasing node rank, then it
implies the Collatz descent theorem.
-/

namespace Collatz

structure ParentCoord where
  level : Nat
  q : Nat
deriving Repr, DecidableEq

abbrev ParentState := Nat

structure SystemNode where
  id : Nat
deriving Repr, DecidableEq

structure InternalState where
  node : SystemNode
  root : Nat
  current : Nat
deriving Repr, DecidableEq

structure SystemEdge where
  id : Nat
  source : SystemNode
  target : SystemNode
  sourceDomain : InternalState → Prop
  targetDomain : InternalState → Nat → Prop
  exitCertificate : InternalState → Nat → Prop

def SystemEdge.targetState (edge : SystemEdge) (state : InternalState) (m : Nat) :
    InternalState :=
  { node := edge.target, root := state.root, current := m }

inductive TargetOrDescent (edge : SystemEdge) (state : InternalState) (m : Nat) : Prop
  | descends : m < state.root → TargetOrDescent edge state m
  | internal : edge.targetDomain state m → TargetOrDescent edge state m
  | exitsCertified :
      edge.exitCertificate state m → m < state.root → TargetOrDescent edge state m

def SourceDomain (edge : SystemEdge) (state : InternalState) : Prop :=
  edge.sourceDomain state

def EdgeSemantics (edge : SystemEdge) : Prop :=
  ∀ state : InternalState,
    SourceDomain edge state →
    ∃ t m : Nat,
      t > 0 ∧
      iter t state.current = m ∧
      TargetOrDescent edge state m

structure CertifiedTransitionSystem where
  isEdge : SystemEdge → Prop
  entryState : Nat → InternalState → Prop
  covered : InternalState → Prop
  rank : SystemNode → Nat

def EntrySemantics (system : CertifiedTransitionSystem) : Prop :=
  ∀ n : Nat,
    n > 1 →
    n % 2 ≠ 0 →
    ∃ state : InternalState,
      system.entryState n state ∧
      state.root = n ∧
      state.current = n ∧
      system.covered state

abbrev UniversalEntrySemantics := EntrySemantics

def CoverageSemantics (system : CertifiedTransitionSystem) : Prop :=
  ∀ (edge : SystemEdge) (state : InternalState) (m : Nat),
    system.isEdge edge →
    system.covered state →
    SourceDomain edge state →
    edge.targetDomain state m →
    system.covered (edge.targetState state m)

def TransitionSoundnessSemantics (system : CertifiedTransitionSystem) : Prop :=
  ∀ edge : SystemEdge, system.isEdge edge → EdgeSemantics edge

def NoEscapeSemantics (system : CertifiedTransitionSystem) : Prop :=
  ∀ state : InternalState,
    system.covered state →
    ∃ edge : SystemEdge,
      system.isEdge edge ∧
      edge.source = state.node ∧
      SourceDomain edge state

def WellFoundedSystem (system : CertifiedTransitionSystem) : Prop :=
  ∀ edge : SystemEdge,
    system.isEdge edge →
    system.rank edge.target < system.rank edge.source

def SystemImpliesDescent (_system : CertifiedTransitionSystem) : Prop :=
  DescentTheorem

theorem covered_state_eventually_descends_below_root
    (system : CertifiedTransitionSystem)
    (coverage : CoverageSemantics system)
    (sound : TransitionSoundnessSemantics system)
    (noEscape : NoEscapeSemantics system)
    (wf : WellFoundedSystem system) :
    ∀ state : InternalState,
      system.covered state →
      ∃ k : Nat, k > 0 ∧ iter k state.current < state.root := by
  intro state
  let r := system.rank state.node
  have hmain :
      ∀ r : Nat,
        ∀ state : InternalState,
          system.rank state.node = r →
          system.covered state →
          ∃ k : Nat, k > 0 ∧ iter k state.current < state.root := by
    intro r
    induction r using Nat.strongRecOn with
    | ind r ih =>
        intro state hrank hcovered
        obtain ⟨edge, hedge, hsource, hdomain⟩ := noEscape state hcovered
        obtain ⟨t, m, htpos, hiter, htarget⟩ := sound edge hedge state hdomain
        cases htarget with
        | descends hlt =>
            refine ⟨t, htpos, ?_⟩
            rw [hiter]
            exact hlt
        | exitsCertified _hexit hlt =>
            refine ⟨t, htpos, ?_⟩
            rw [hiter]
            exact hlt
        | internal htargetDomain =>
            let nextState := edge.targetState state m
            have hnextCovered : system.covered nextState :=
              coverage edge state m hedge hcovered hdomain htargetDomain
            have hrankDecrease : system.rank edge.target < system.rank state.node :=
              by
                have h := wf edge hedge
                rwa [hsource] at h
            have hnextRank : system.rank nextState.node < r := by
              simpa [nextState, SystemEdge.targetState, hrank] using hrankDecrease
            obtain ⟨k, hkpos, hkdesc⟩ :=
              ih (system.rank nextState.node) hnextRank nextState rfl hnextCovered
            refine ⟨t + k, by omega, ?_⟩
            rw [iter_add, hiter]
            exact hkdesc
  exact hmain r state rfl

theorem certified_transition_system_implies_descent
    (system : CertifiedTransitionSystem)
    (entry : UniversalEntrySemantics system)
    (coverage : CoverageSemantics system)
    (sound : TransitionSoundnessSemantics system)
    (noEscape : NoEscapeSemantics system)
    (wf : WellFoundedSystem system) :
    DescentTheorem := by
  intro n hn
  by_cases heven : n % 2 = 0
  · refine ⟨1, by decide, ?_⟩
    simp [iter, C, heven]
    exact Nat.div_lt_self (by omega) (by decide : 1 < 2)
  · obtain ⟨state, _hentry, hroot, hcurrent, hcovered⟩ := entry n hn heven
    obtain ⟨k, hkpos, hkdesc⟩ :=
      covered_state_eventually_descends_below_root
        system coverage sound noEscape wf state hcovered
    refine ⟨k, by omega, ?_⟩
    rw [hcurrent, hroot] at hkdesc
    exact hkdesc

end Collatz
