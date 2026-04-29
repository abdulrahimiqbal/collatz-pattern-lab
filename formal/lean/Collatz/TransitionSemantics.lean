import Collatz.CertifiedSystem

/-!
Semantic Collatz transition lemmas for reflected parent-state edges.

This module proves the part RUN-054 can honestly prove: if a reflected edge's
source-domain predicate contains the concrete parent-transition factorization,
then the corresponding `SystemEdge` has real `Collatz.iter` semantics.
-/

namespace Collatz

inductive EdgeOutcome (edge : SystemEdge) (state : InternalState) (m : Nat) : Prop
  | descends : m < state.root → EdgeOutcome edge state m
  | internal : edge.targetDomain state m → EdgeOutcome edge state m
  | exits : edge.exitCertificate state m → m < state.root → EdgeOutcome edge state m

def ReflectedEdgeSemantics (edge : SystemEdge) : Prop :=
  ∀ state : InternalState,
    edge.sourceDomain state →
    ∃ t m : Nat,
      t > 0 ∧
      iter t state.current = m ∧
      EdgeOutcome edge state m

theorem reflected_edge_semantics_to_abstract
    {edge : SystemEdge}
    (h : ReflectedEdgeSemantics edge) :
    EdgeSemantics edge := by
  intro state hsource
  obtain ⟨t, m, htpos, hiter, houtcome⟩ := h state hsource
  refine ⟨t, m, htpos, hiter, ?_⟩
  cases houtcome with
  | descends hlt => exact TargetOrDescent.descends hlt
  | internal htarget => exact TargetOrDescent.internal htarget
  | exits hexit hlt => exact TargetOrDescent.exitsCertified hexit hlt

theorem forced_burst_semantics_odd
    (a q : Nat)
    (hq_pos : q > 0)
    (_hq_odd : q % 2 = 1) :
    iter (2 * a) (2 ^ a * q - 1) = 3 ^ a * q - 1 :=
  forced_burst_semantics a q hq_pos

theorem halving_division_semantics (h y : Nat) :
    iter h (2 ^ h * y) = y :=
  iter_div2_power h y

theorem parent_reconstruction_semantics (b q' y : Nat)
    (hy : y = parentStateNat b q') :
    parentState b q' y := by
  rw [hy]
  exact parentStateNat_spec b q'

theorem parent_transition_iter_semantics
    (a b h q q' : Nat)
    (hq_pos : q > 0)
    (htarget :
      3 ^ a * q - 1 =
        2 ^ h * parentStateNat b q') :
    iter (2 * a + h) (parentStateNat a q) =
      parentStateNat b q' := by
  unfold parentStateNat
  rw [iter_add]
  rw [forced_burst_semantics a q hq_pos]
  rw [htarget]
  exact iter_div2_power h (2 ^ b * q' - 1)

theorem EdgeCert.toSystemEdge_reflected_semantics
    {CertId NodeId : Type}
    (cert : EdgeCert CertId NodeId) :
    ReflectedEdgeSemantics cert.toSystemEdge := by
  intro state hsource
  rcases hsource with
    ⟨hparent_pos, _hresidue_lt, _hmapA, _hmapB, _hmapD,
      _hbranchC, _hdenom, q, q', hq_pos, _hq_odd, hq'_pos,
      _hbranch, _hmap, _hnode, hcurrent, htarget⟩
  let t := 2 * cert.sourceParent + cert.baseBurstDivisionExponent
  let m := parentStateNat cert.targetParent q'
  have htpos : t > 0 := by
    dsimp [t]
    omega
  have hiter :
      iter t state.current = m := by
    dsimp [t, m]
    rw [hcurrent]
    exact parent_transition_iter_semantics
      cert.sourceParent
      cert.targetParent
      cert.baseBurstDivisionExponent
      q
      q'
      hq_pos
      htarget
  refine ⟨t, m, htpos, hiter, ?_⟩
  exact EdgeOutcome.internal ⟨q', hq'_pos, rfl⟩

theorem EdgeCert.toSystemEdge_semantics
    {CertId NodeId : Type}
    (cert : EdgeCert CertId NodeId) :
    EdgeSemantics cert.toSystemEdge :=
  reflected_edge_semantics_to_abstract
    (EdgeCert.toSystemEdge_reflected_semantics cert)

theorem S4EdgeCert_to_edge_semantics
    {CertId NodeId : Type}
    (cert : EdgeCert CertId NodeId)
    (_hkind : cert.kind = EdgeKind.s4ParentTransition) :
    EdgeSemantics cert.toSystemEdge :=
  EdgeCert.toSystemEdge_semantics cert

def RankingSupport {CertId NodeId : Type}
    (cert : EdgeCert CertId NodeId) : Prop :=
  cert.role = EdgeRole.rankingSupportOnly ∧
  cert.gainDen > 0 ∧
  cert.gainNum < cert.gainDen

def DebtDecreaseSupport {CertId NodeId : Type}
    (cert : EdgeCert CertId NodeId) : Prop :=
  cert.gainDen > 0 ∧ cert.gainNum < cert.gainDen

def DirectDescentSemantics {CertId NodeId : Type}
    (cert : EdgeCert CertId NodeId) : Prop :=
  cert.role = EdgeRole.directDescentEdge ∧
  EdgeSemantics cert.toSystemEdge

end Collatz
