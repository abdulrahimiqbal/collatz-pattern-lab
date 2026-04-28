import Collatz.Core

/-!
Parent-state vocabulary used by the RUN-024 replay port.

These are mathematical predicates, not trusted statements about the Python
artifacts.
-/

namespace Collatz

def parentState (a q n : Nat) : Prop :=
  q > 0 ∧ n = 2 ^ a * q - 1

def residualClass (a n : Nat) : Prop :=
  n % (2 ^ a) = (2 ^ a - 1) % (2 ^ a)

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
