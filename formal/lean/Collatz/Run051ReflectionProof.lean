import Collatz.Run051Bundle
import Collatz.GlobalSemantics

/-!
RUN-053 reflection check over the typed RUN-051 bundle.

The finite bundle and component checkers are fully computable and the generated
bundle passes those checks.  RUN-054 proves the transition-soundness component
for reflected S4 parent transitions.  RUN-056 replaces the empty entry/coverage
projection with typed parent-coordinate predicates.  The final descent theorem
is not declared here because the remaining global soundness theorems are still
open.
-/

namespace Collatz

theorem run051Entry_check :
    Reflection.checkEntry run051Bundle = true := by
  native_decide

theorem run051Coverage_check :
    Reflection.checkCoverage run051Bundle = true := by
  native_decide

theorem run051TransitionSoundness_check :
    Reflection.checkTransitionSoundness run051Bundle = true := by
  native_decide

theorem run051NoEscape_check :
    Reflection.checkNoEscape run051Bundle = true := by
  native_decide

theorem run051WellFounded_check :
    Reflection.checkWellFounded run051Bundle = true := by
  native_decide

theorem run051DescentImplication_check :
    Reflection.checkDescentImplication run051Bundle = true := by
  native_decide

theorem run051Bundle_check :
    Reflection.checkCertifiedSystemBundle run051Bundle = true := by
  native_decide

theorem run051TransitionSoundness_sound :
    TransitionSoundnessSemantics run051Bundle.system :=
  Reflection.checkTransitionSoundness_sound
    run051Bundle
    run051TransitionSoundness_check

theorem run051EntryProjection_built :
    GlobalSemantics.EntryProjectionBuilt run051Bundle :=
  GlobalSemantics.entry_projection_built run051Bundle

theorem run051CoveredProjection_built :
    GlobalSemantics.CoveredProjectionBuilt run051Bundle :=
  GlobalSemantics.covered_projection_built run051Bundle

theorem run051Entry_sound :
    UniversalEntrySemantics run051Bundle.system :=
  Reflection.checkEntry_sound
    run051Bundle
    run051Entry_check

theorem run051Coverage_sound :
    CoverageSemantics run051Bundle.system :=
  Reflection.checkCoverage_sound
    run051Bundle
    run051Coverage_check

private theorem allS3RoleCerts_sound
    {roles : List (S3RoleCert CertId NodeId)}
    (h : roles.all Reflection.checkS3RoleCert = true) :
    ∀ role ∈ roles, Reflection.S3RoleSupportSemantics role := by
  induction roles with
  | nil =>
      intro role hmem
      cases hmem
  | cons head tail ih =>
      intro role hmem
      have hsplit :
          Reflection.checkS3RoleCert head = true ∧
            tail.all Reflection.checkS3RoleCert = true := by
        cases hhead : Reflection.checkS3RoleCert head <;>
          cases htail : tail.all Reflection.checkS3RoleCert <;>
          simp [List.all, hhead, htail] at h ⊢
      have hmem' : role = head ∨ role ∈ tail := by
        simpa using hmem
      rcases hmem' with hrole | hrole
      · subst role
        exact Reflection.checkS3RoleCert_sound head hsplit.1
      · exact ih hsplit.2 role hrole

theorem run051S3Roles_support_sound :
    ∀ role ∈ run051Bundle.s3Roles,
      Reflection.S3RoleSupportSemantics role := by
  apply allS3RoleCerts_sound
  native_decide

private theorem allS6ProofTrees_sound
    {trees : List (S6ProofTreeCert CertId)}
    (h : trees.all (Reflection.checkS6ProofTree run051Bundle) = true) :
    ∀ tree ∈ trees,
      Reflection.S6ProofTreeSemantics run051Bundle tree := by
  induction trees with
  | nil =>
      intro tree hmem
      cases hmem
  | cons head tail ih =>
      intro tree hmem
      have hsplit :
          Reflection.checkS6ProofTree run051Bundle head = true ∧
            tail.all (Reflection.checkS6ProofTree run051Bundle) = true := by
        cases hhead : Reflection.checkS6ProofTree run051Bundle head <;>
          cases htail : tail.all (Reflection.checkS6ProofTree run051Bundle) <;>
          simp [List.all, hhead, htail] at h ⊢
      have hmem' : tree = head ∨ tree ∈ tail := by
        simpa using hmem
      rcases hmem' with htree | htree
      · subst tree
        exact Reflection.checkS6ProofTree_sound run051Bundle head hsplit.1
      · exact ih hsplit.2 tree htree

theorem run051S6ProofTrees_structural_sound :
    ∀ tree ∈ run051Bundle.s6ProofTrees,
      Reflection.S6ProofTreeSemantics run051Bundle tree := by
  apply allS6ProofTrees_sound
  native_decide

theorem run051DescentImplication_metadata :
    Reflection.DescentImplicationMetadata run051Bundle :=
  Reflection.checkDescentImplication_sound
    run051Bundle
    run051DescentImplication_check

def Run053MissingReflectionGaps : List String :=
  Reflection.MissingReflectionSoundnessTheorems ++
    [
      "there is no theorem converting S3 SUPPORTING_DEBT_EDGE records into the ranking/no-escape assumptions consumed by WellFoundedSystem",
      "typed S6 proof trees now have structural rule/conclusion checks, but no theorem yet closes NoEscapeSemantics and CoverageSemantics"
    ]

def Run054RemainingReflectionGaps : List String :=
  [
    "checkNoEscape_sound: typed S6 proof trees do not yet construct NoEscapeSemantics run051Bundle.system",
    "checkWellFounded_sound: S3 ranking support and kernel path fields do not yet construct WellFoundedSystem run051Bundle.system"
  ]

def Run055MissingGlobalSemanticsGaps : List String :=
  GlobalSemantics.MissingGlobalSemanticsGaps

def Run056ProjectionStatus : List String :=
  [
    "ENTRY_PROJECTION_BUILT: run051Bundle.system.entryState is a typed parent-coordinate entry predicate",
    "COVERAGE_PROJECTION_BUILT: run051Bundle.system.covered is a typed coverage-domain membership predicate",
    "RUN057_COMPLETE: checkEntry_sound and checkCoverage_sound are proved from universal coverage-domain membership"
  ]

def Run057RemainingReflectionGaps : List String :=
    [
      "checkNoEscape_sound: S6 dependency/proof-step checks are structural and do not construct NoEscapeSemantics",
      "checkWellFounded_sound: guarded-kernel/ranking support still does not construct WellFoundedSystem",
      "checkCertifiedSystemBundle_sound: blocked on no-escape and well-foundedness soundness"
    ]

def Run058StructuralSemanticsStatus : List String :=
  [
      "S3_ROLE_SUPPORT_SOUND: all RUN-051 S3 roles are ranking/support facts, not transition edges",
      "S6_STRUCTURAL_PROOF_TREE_SOUND: S6 dependencies check typed certificate membership/matching claim kinds and proof trees contain a rule that closes their claim kind",
      "S4_GUARDED_SOURCE_DOMAIN_BUILT: reflected S4 source domains carry branch residue/depth and parent-coordinate map equalities",
      "DESCENT_IMPLICATION_METADATA_SOUND: descent implication checker is recorded only as metadata, not as a proof of DescentTheorem",
      "RUN058_REMAINING: no theorem yet turns S6 structural proof trees into NoEscapeSemantics"
    ]

end Collatz
