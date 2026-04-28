import Collatz.TransitionSystem
import Collatz.Run046Data

/-!
Semantic vocabulary for RUN-047B.

This module connects certificate records to propositions about the actual
Collatz map where the current payloads make that possible.  The full bridge to
`DescentTheorem` is not declared here, because the generated certificates do
not yet contain enough iterate-level witnesses.
-/

namespace Collatz

def S4ExactDomain (c : S4ParentMapCert) (q : Nat) : Prop :=
  parentQPositive q ∧
  q ≥ c.minimumQ ∧
  q % c.domainModulus = c.domainResidue

def S4TargetCoordinate (c : S4ParentMapCert) (q q' : Nat) : Prop :=
  c.mapA * q + c.mapB = c.mapD * q'

def SemanticParentTransition (c : S4ParentMapCert) : Prop :=
  ∀ q : Nat,
    S4ExactDomain c q →
    ∃ q' t : Nat,
      parentQPositive q' ∧
      t > 0 ∧
      S4TargetCoordinate c q q' ∧
      iter t (parentStateNat c.sourceParent q) = parentStateNat c.targetParent q'

def S4ParentTransitionSemanticWitness.Valid
    (w : S4ParentTransitionSemanticWitness) : Prop :=
  w.mapA = 3 ^ w.sourceParent ∧
  w.mapB = 2 ^ w.baseBurstDivisionExponent - 1 ∧
  w.mapD = 2 ^ (w.baseBurstDivisionExponent + w.targetParent) ∧
  w.sourceDepth + w.valuation = w.baseBurstDivisionExponent + w.targetParent ∧
  w.mapD = 2 ^ w.sourceDepth * 2 ^ w.valuation ∧
  w.mapA * w.sourceResidue + w.mapB = w.c * 2 ^ w.sourceDepth ∧
  w.standardStepCount = 2 * w.sourceParent + w.baseBurstDivisionExponent

instance (w : S4ParentTransitionSemanticWitness) : Decidable w.Valid := by
  unfold S4ParentTransitionSemanticWitness.Valid
  infer_instance

def S4SemanticWitnessMatchesCert
    (c : S4ParentMapCert) (w : S4ParentTransitionSemanticWitness) : Prop :=
  w.certificateId = c.transitionId ∧
  w.sourceParent = c.sourceParent ∧
  w.targetParent = c.targetParent ∧
  w.valuation = c.valuation ∧
  w.sourceDepth = c.sourceDepth ∧
  w.sourceResidue = c.sourceResidue ∧
  w.baseBurstDivisionExponent = c.baseBurstDivisionExponent ∧
  w.mapA = c.mapA ∧
  w.mapB = c.mapB ∧
  w.mapD = c.mapD ∧
  w.c = c.c

namespace S4ParentTransitionSemanticWitness

theorem parent_coordinate_formula
    {w : S4ParentTransitionSemanticWitness}
    (hw : w.Valid) (k : Nat) :
    w.mapA * (w.sourceResidue + 2 ^ w.sourceDepth * k) + w.mapB =
      2 ^ w.sourceDepth * (w.c + w.mapA * k) := by
  rcases hw with ⟨_hA, _hB, _hD, _hexp, _hden, hconst, _hsteps⟩
  have hmul :
      w.mapA * (2 ^ w.sourceDepth * k) =
        (w.mapA * k) * 2 ^ w.sourceDepth := by
    rw [Nat.mul_assoc]
    rw [Nat.mul_comm (2 ^ w.sourceDepth) k]
  calc
    w.mapA * (w.sourceResidue + 2 ^ w.sourceDepth * k) + w.mapB =
        (w.mapA * w.sourceResidue + w.mapB) +
          w.mapA * (2 ^ w.sourceDepth * k) := by
      simp [Nat.mul_add, Nat.add_assoc, Nat.add_comm]
    _ = w.c * 2 ^ w.sourceDepth +
          w.mapA * (2 ^ w.sourceDepth * k) := by
      rw [hconst]
    _ = w.c * 2 ^ w.sourceDepth +
          (w.mapA * k) * 2 ^ w.sourceDepth := by
      rw [hmul]
    _ = (w.c + w.mapA * k) * 2 ^ w.sourceDepth := by
      rw [Nat.add_mul]
    _ = 2 ^ w.sourceDepth * (w.c + w.mapA * k) := by
      rw [Nat.mul_comm]

theorem collatz_iter_from_target_factor
    {w : S4ParentTransitionSemanticWitness} {q q' : Nat}
    (hw : w.Valid)
    (hq : q > 0)
    (htarget : 3 ^ w.sourceParent * q - 1 =
      2 ^ w.baseBurstDivisionExponent * (2 ^ w.targetParent * q' - 1)) :
    iter w.standardStepCount (parentStateNat w.sourceParent q) =
      parentStateNat w.targetParent q' := by
  rcases hw with ⟨_hA, _hB, _hD, _hexp, _hden, _hconst, hsteps⟩
  unfold parentStateNat
  rw [hsteps]
  rw [iter_add]
  rw [forced_burst_semantics w.sourceParent q hq]
  rw [htarget]
  rw [iter_div2_power]

end S4ParentTransitionSemanticWitness

def SemanticDescentOrExit (c : S3DebtExactCert) : Prop :=
  ∀ q : Nat,
    parentQPositive q →
    ∃ t : Nat,
      t > 0 ∧
      (iter t (parentStateNat c.sourceParent q) < parentStateNat c.sourceParent q ∨
       parentLevelRelation c.targetParent (iter t (parentStateNat c.sourceParent q)))

def UniversalParentCoverage : Prop :=
  ∀ n : Nat, n > 1 → ∃ a q : Nat, exactParentState a q n

def TransitionSystemSound : Prop :=
  ∀ c : S4ParentMapCert, c ∈ run046S4ParentMapCerts → SemanticParentTransition c

def S3ExitsSound : Prop :=
  ∀ c : S3DebtExactCert, c ∈ run046S3DebtCerts → SemanticDescentOrExit c

def S6LemmaSemanticClaim (c : S6LemmaCert) : Prop :=
  match c.blockerType with
  | "coverage" => UniversalParentCoverage
  | "global_descent" => DescentTheorem
  | "induction" => DescentTheorem
  | "no_escape" => TransitionSystemSound
  | "strict_verifier_gap" => UniversalParentCoverage ∧ TransitionSystemSound ∧ S3ExitsSound
  | _ => False

def AllS6SemanticClaims : List S6LemmaCert → Prop
  | [] => True
  | c :: rest => S6LemmaSemanticClaim c ∧ AllS6SemanticClaims rest

def InternalAffineStep (cert : NaturalViabilityKernelCert) (q q' : Nat) : Prop :=
  cert.mapA * q + cert.mapB = cert.mapD * q'

def InfiniteInternalParentPathOverNat
    (cert : NaturalViabilityKernelCert) (path : Nat → Nat) : Prop :=
  (∀ i : Nat, parentQPositive (path i)) ∧
  (∀ i : Nat, InternalAffineStep cert (path i) (path (i + 1)))

def NoInfiniteInternalParentPathOverNat : Prop :=
  ¬ ∃ path : Nat → Nat, InfiniteInternalParentPathOverNat run046NaturalKernelCert path

def TopLevelSemanticHypotheses : Prop :=
  UniversalParentCoverage ∧
  TransitionSystemSound ∧
  S3ExitsSound ∧
  AllS6SemanticClaims run046S6LemmaCerts ∧
  NoInfiniteInternalParentPathOverNat

inductive S3SemanticRole where
  | directDescent
  | rankingDecrease
  | exitCertificate
  | supportingDebtEdge
deriving Repr, DecidableEq

def S3SemanticRoleFieldPresent (_c : S3DebtExactCert) : Prop :=
  False

inductive S6SemanticClaimType where
  | coverage
  | noEscape
  | induction
  | transitionComposition
  | rankingWellFoundedness
  | residualParentCoverage
deriving Repr, DecidableEq

def S6ProofTreeSemantics (_c : S6LemmaCert) : Prop :=
  False

def S6BlockerClosed (c : S6LemmaCert) : Prop :=
  S6ProofTreeSemantics c

structure S3SemanticConsumerPayload where
  consumerType : String
  consumerId : String
  dependencyType : String := ""
deriving Repr, DecidableEq

structure S3SemanticRolePayload where
  certificateId : String
  branchId : String
  semanticRole : String
  sourceNode : String
  targetNode : String
  measureId : String
  measureSourceExpr : String
  measureTargetExpr : String
  decreaseCertificateId : String
  decreaseInequality : String
  gainNum : Nat
  gainDen : Nat
  consumedBy : List S3SemanticConsumerPayload
  collatzIterateWitnessPresent : Bool := false
  semanticPayloadHash : String
deriving Repr, DecidableEq

def validS3SemanticRoleString (role : String) : Bool :=
  role == "DIRECT_DESCENT" ||
  role == "RANKING_DECREASE" ||
  role == "EXIT_CERTIFICATE" ||
  role == "SUPPORTING_DEBT_EDGE"

def stringPresent (value : String) : Bool :=
  decide (value ≠ "")

def S3SemanticConsumerPayload.validBool (payload : S3SemanticConsumerPayload) : Bool :=
  stringPresent payload.consumerType && stringPresent payload.consumerId

def S3SemanticRolePayload.validBool (payload : S3SemanticRolePayload) : Bool :=
  stringPresent payload.certificateId &&
  validS3SemanticRoleString payload.semanticRole &&
  stringPresent payload.measureId &&
  stringPresent payload.decreaseCertificateId &&
  stringPresent payload.semanticPayloadHash &&
  (if payload.semanticRole == "DIRECT_DESCENT" then payload.collatzIterateWitnessPresent else true)

def S3SemanticRolePayload.Valid (payload : S3SemanticRolePayload) : Prop :=
  payload.validBool = true

instance (payload : S3SemanticRolePayload) : Decidable payload.Valid := by
  unfold S3SemanticRolePayload.Valid
  infer_instance

structure S6ProofTreeDependencyPayload where
  dependencyType : String
  certificateId : String
  semanticRole : String
  usedFor : String
deriving Repr, DecidableEq

structure S6ProofStepPayload where
  stepId : String
  rule : String
  inputCount : Nat
  output : String
deriving Repr, DecidableEq

structure S6ProofTreePayload where
  lemmaId : String
  blockerId : String
  semanticClaimType : String
  conclusion : String
  dependencies : List S6ProofTreeDependencyPayload
  proofSteps : List S6ProofStepPayload
  closesBlocker : Bool
  semanticPayloadHash : String
deriving Repr, DecidableEq

def validS6SemanticClaimTypeString (claimType : String) : Bool :=
  claimType == "coverage" ||
  claimType == "no_escape" ||
  claimType == "induction" ||
  claimType == "ranking" ||
  claimType == "transition_composition" ||
  claimType == "residual_parent"

def validS6ProofRuleString (rule : String) : Bool :=
  rule == "compose_transition" ||
  rule == "apply_coverage" ||
  rule == "apply_no_escape" ||
  rule == "apply_ranking" ||
  rule == "apply_induction" ||
  rule == "apply_residual_parent"

def S6ProofTreeDependencyPayload.validBool (payload : S6ProofTreeDependencyPayload) : Bool :=
  stringPresent payload.dependencyType &&
  stringPresent payload.certificateId &&
  stringPresent payload.semanticRole &&
  stringPresent payload.usedFor

def S6ProofStepPayload.validBool (payload : S6ProofStepPayload) : Bool :=
  stringPresent payload.stepId &&
  validS6ProofRuleString payload.rule &&
  stringPresent payload.output

def S6ProofTreePayload.expectedConclusion (payload : S6ProofTreePayload) : String :=
  payload.semanticClaimType ++ " blocker " ++ payload.blockerId ++ " closed"

def S6ProofTreePayload.validBool (payload : S6ProofTreePayload) : Bool :=
  stringPresent payload.lemmaId &&
  stringPresent payload.blockerId &&
  validS6SemanticClaimTypeString payload.semanticClaimType &&
  payload.conclusion == payload.expectedConclusion &&
  decide (payload.dependencies.length > 0) &&
  payload.dependencies.all S6ProofTreeDependencyPayload.validBool &&
  decide (payload.proofSteps.length > 0) &&
  payload.proofSteps.all S6ProofStepPayload.validBool &&
  payload.closesBlocker &&
  stringPresent payload.semanticPayloadHash

def S6ProofTreePayload.Valid (payload : S6ProofTreePayload) : Prop :=
  payload.validBool = true

instance (payload : S6ProofTreePayload) : Decidable payload.Valid := by
  unfold S6ProofTreePayload.Valid
  infer_instance

structure KernelFixedPointPayload where
  numerator : Int
  denominator : Nat
deriving Repr, DecidableEq

structure KernelDivisibilityFamilyPayload where
  statement : String
  source : String
  distanceForm : String
  repeatForcesDivisibilityBy : String
  kernelCongruenceDepthUnbounded : Bool
deriving Repr, DecidableEq

structure NaturalKernelToPathLinkPayload where
  kernelCertificateId : String
  sccId : String
  statement : String
  fixedPoint : KernelFixedPointPayload
  divisibilityFamily : KernelDivisibilityFamilyPayload
  noNatReason : String
  noPositiveIntegerQInKernel : Bool
  conclusion : String
  semanticPayloadHash : String
deriving Repr, DecidableEq

def NaturalKernelToPathLinkPayload.validBool (payload : NaturalKernelToPathLinkPayload) : Bool :=
  stringPresent payload.kernelCertificateId &&
  stringPresent payload.sccId &&
  payload.statement == "Any infinite internal guarded path over Nat induces membership in the surviving viability kernel." &&
  decide (payload.fixedPoint.denominator > 0) &&
  payload.fixedPoint.denominator % 2 == 1 &&
  decide (payload.fixedPoint.numerator < 0) &&
  payload.divisibilityFamily.statement == "for every N, 2^N divides denominator*q - numerator" &&
  payload.divisibilityFamily.source == "guarded viability kernel refinement" &&
  payload.divisibilityFamily.distanceForm == "denominator*q - numerator" &&
  payload.divisibilityFamily.kernelCongruenceDepthUnbounded &&
  stringPresent payload.noNatReason &&
  payload.noPositiveIntegerQInKernel &&
  payload.conclusion == "NoInfiniteInternalParentPathOverNat" &&
  stringPresent payload.semanticPayloadHash

def NaturalKernelToPathLinkPayload.Valid (payload : NaturalKernelToPathLinkPayload) : Prop :=
  payload.validBool = true

instance (payload : NaturalKernelToPathLinkPayload) : Decidable payload.Valid := by
  unfold NaturalKernelToPathLinkPayload.Valid
  infer_instance

structure TopLevelCoverageDomainMapEntry where
  domainId : String
  parentState : String
  coverageCertificateId : String
  residualCertificateId : String
  coveredPredicate : String
  kind : String
  modulus : Nat
  residueStart : Nat
  residueEndExclusive : Nat
deriving Repr, DecidableEq

structure NaturalKernelReferencePayload where
  kernelCertificateId : String
  sccId : String
  conclusion : String
deriving Repr, DecidableEq

structure TopLevelCoverageDomainMapPayload where
  evenCase : String
  oddCase : String
  oddValuationDefinition : String
  parentStateDomains : List TopLevelCoverageDomainMapEntry
  noUncoveredDomains : Bool
  naturalKernelReference : NaturalKernelReferencePayload
  conclusion : String
  semanticPayloadHash : String
deriving Repr, DecidableEq

def TopLevelCoverageDomainMapEntry.validBool (payload : TopLevelCoverageDomainMapEntry) : Bool :=
  stringPresent payload.domainId &&
  stringPresent payload.coveredPredicate &&
  decide (payload.modulus > 0) &&
  decide (payload.residueStart ≤ payload.residueEndExclusive) &&
  decide (payload.residueEndExclusive ≤ payload.modulus)

def TopLevelCoverageDomainMapPayload.hasResidualDomainBool
    (payload : TopLevelCoverageDomainMapPayload) : Bool :=
  payload.parentStateDomains.any (fun domain => stringPresent domain.residualCertificateId)

def TopLevelCoverageDomainMapPayload.validBool
    (payload : TopLevelCoverageDomainMapPayload) : Bool :=
  stringPresent payload.evenCase &&
  stringPresent payload.oddCase &&
  decide (payload.parentStateDomains.length > 0) &&
  payload.parentStateDomains.all TopLevelCoverageDomainMapEntry.validBool &&
  payload.hasResidualDomainBool &&
  payload.noUncoveredDomains &&
  stringPresent payload.naturalKernelReference.kernelCertificateId &&
  payload.naturalKernelReference.conclusion == "NoInfiniteInternalParentPathOverNat" &&
  payload.conclusion == "Every n>1 either descends immediately or enters a covered certified parent-state domain." &&
  stringPresent payload.semanticPayloadHash

def TopLevelCoverageDomainMapPayload.Valid
    (payload : TopLevelCoverageDomainMapPayload) : Prop :=
  payload.validBool = true

instance (payload : TopLevelCoverageDomainMapPayload) : Decidable payload.Valid := by
  unfold TopLevelCoverageDomainMapPayload.Valid
  infer_instance

theorem self_lt_two_pow_succ (n : Nat) : n < 2 ^ (n + 1) := by
  induction n with
  | zero => decide
  | succ n ih =>
      have hle : n.succ ≤ 2 ^ (n + 1) := Nat.succ_le_of_lt ih
      have hp : 0 < 2 ^ (n + 1) := Nat.pow_pos (by decide : 0 < 2)
      have hlt : 2 ^ (n + 1) < 2 ^ (n + 1) * 2 := by omega
      have hpow : 2 ^ (n.succ + 1) = 2 ^ (n + 1) * 2 := by
        rw [show n.succ + 1 = Nat.succ (n + 1) by omega]
        rw [Nat.pow_succ]
      rw [hpow]
      exact Nat.lt_of_le_of_lt hle hlt

theorem no_positive_int_divisible_by_all_powers_two
    (m : Nat) (hm : m > 0) :
    ¬ (∀ N : Nat, 2 ^ N ∣ m) := by
  intro hall
  have hdiv : 2 ^ (m + 1) ∣ m := hall (m + 1)
  have hle : 2 ^ (m + 1) ≤ m := Nat.le_of_dvd hm hdiv
  have hlt : m < 2 ^ (m + 1) := self_lt_two_pow_succ m
  omega

theorem even_semantic_descent
    (n : Nat) (hn : n > 1) (heven : n % 2 = 0) :
    eventually_descends n := by
  refine ⟨1, by decide, ?_⟩
  simp [iter, C, heven]
  exact Nat.div_lt_self (by omega) (by decide : 1 < 2)

namespace S4ParentMapClaim

theorem to_parent_map_payload
    {c : S4ParentMapCert}
    (hc : S4ParentMapClaim c)
    (hpresent : c.hasParentMapPayload = true) :
    S4ParentMapPayloadClaim c := by
  rcases hc with
    ⟨_hcoeff, _hodd, _hval, _hkmod, _hexcl, _hinv, _hres, _hfloor, _hmember, hpayload⟩
  rcases hpayload with hmissing | hpayload
  · rw [hpresent] at hmissing
    cases hmissing
  · exact hpayload

end S4ParentMapClaim

namespace S3DebtClaim

theorem to_debt_arithmetic
    {c : S3DebtExactCert}
    (hc : S3DebtClaim c) :
    c.gainDen > 0 ∧ c.gainNum < c.gainDen := by
  rcases hc with
    ⟨_h0, _h1, _h2, _h3, _h4, _h5, _h6, _h7, _h8, _h9, _h10, _h11,
      _h12, _h13, _h14, _h15, _h16, _h17, _h18, _h19, _h20, _h21, hden, hlt⟩
  exact ⟨hden, hlt⟩

end S3DebtClaim

namespace NaturalViabilityKernelEmpty

theorem no_positive_fixed_point_coordinate
    {cert : NaturalViabilityKernelCert}
    (hcert : NaturalViabilityKernelEmpty cert) :
    ∀ q : Nat, q > 0 → (cert.denominator : Int) * (q : Int) - cert.numerator ≠ 0 :=
  hcert.2

end NaturalViabilityKernelEmpty

def MissingS4SemanticFields : List String :=
  [
    "positive Collatz iterate step count for each S4 edge",
    "parity or iterate witness proving the affine parent map equals iter C t",
    "proof that computed q' is positive for every q in the exact domain"
  ]

def MissingS3SemanticFields : List String :=
  [
    "positive Collatz iterate step count for each S3 debt edge",
    "target iterate value or parent exit consumed by the graph",
    "theorem connecting debt decrease to eventual descent of n"
  ]

def MissingS6SemanticFields : List String :=
  [
    "semantic statement for each blocker id",
    "coverage interval theorem over parent-state domains",
    "no-escape theorem for certified branches",
    "induction and lifting theorem payloads over the actual Collatz map"
  ]

def MissingTopLevelSemanticFields : List String :=
  [
    "theorem that required coverage domains include every odd n greater than one",
    "theorem that checked transition edges cover every nonterminal parent state",
    "theorem turning ranked graph metadata plus natural-kernel emptiness into termination over Nat"
  ]

end Collatz
