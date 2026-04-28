import Collatz.Core

/-!
Parent-state vocabulary used by the certificate replay ports.

The definitions in this file are semantic: they talk about the actual Collatz
map from `Collatz.Core`, not about replay status.
-/

namespace Collatz

def parentState (a q n : Nat) : Prop :=
  n = 2 ^ a * q - 1

def parentStateNat (a q : Nat) : Nat :=
  2 ^ a * q - 1

def parentQPositive (q : Nat) : Prop :=
  q > 0

def parentQOdd (q : Nat) : Prop :=
  q % 2 = 1

def exactParentState (a q n : Nat) : Prop :=
  parentState a q n ∧ parentQPositive q ∧ parentQOdd q

def parentLevelRelation (a n : Nat) : Prop :=
  ∃ q : Nat, exactParentState a q n

def semanticParentTransitionRel (a q b q' : Nat) : Prop :=
  parentQPositive q ∧
  parentQPositive q' ∧
  ∃ t : Nat, t > 0 ∧ iter t (parentStateNat a q) = parentStateNat b q'

def residualClass (a n : Nat) : Prop :=
  n % (2 ^ a) = (2 ^ a - 1) % (2 ^ a)

theorem parentStateNat_spec (a q : Nat) :
    parentState a q (parentStateNat a q) := by
  rfl

theorem parent_entry_level_zero (n : Nat) :
    parentState 0 (n + 1) n := by
  unfold parentState
  omega

theorem parent_entry_level_zero_positive (n : Nat) :
    parentQPositive (n + 1) := by
  unfold parentQPositive
  omega

structure ExactTransitionStatement where
  sourceParent : Nat
  targetParent : Nat
  valuation : Nat
  c : Nat
  coefficient : Nat
  oddModulus : Nat
  targetOddResidue : Nat
deriving Repr, DecidableEq

def exactTransitionStatement (s : ExactTransitionStatement) : Prop :=
  s.coefficient = 3 ^ s.sourceParent ∧
  s.oddModulus = s.coefficient ∧
  s.targetParent ≥ s.valuation

structure CoverageStatement where
  totalNodeCount : Nat
  acceptedNodeCount : Nat
  openNodeCount : Nat
deriving Repr, DecidableEq

def coverageStatement (s : CoverageStatement) : Prop :=
  s.openNodeCount = 0 ∧ s.acceptedNodeCount = s.totalNodeCount

structure RankedEdge where
  source : String
  target : String
  sourceRank : Nat
  targetRank : Nat
deriving Repr, DecidableEq

def rankedEdgeDecreases (e : RankedEdge) : Prop :=
  e.targetRank < e.sourceRank

def wellFoundedGraphStatement (edges : List RankedEdge) : Prop :=
  ∀ edge ∈ edges, rankedEdgeDecreases edge

end Collatz
