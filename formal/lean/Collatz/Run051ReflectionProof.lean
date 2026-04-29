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

theorem run051Entry_check_fails :
    Reflection.checkEntry run051Bundle = false := by
  native_decide

theorem run051Coverage_check_fails :
    Reflection.checkCoverage run051Bundle = false := by
  native_decide

theorem run051TransitionSoundness_check :
    Reflection.checkTransitionSoundness run051Bundle = true := by
  native_decide

theorem run051NoEscape_check_fails :
    Reflection.checkNoEscape run051Bundle = false := by
  native_decide

theorem run051WellFounded_check_fails :
    Reflection.checkWellFounded run051Bundle = false := by
  native_decide

theorem run051DescentImplication_check :
    Reflection.checkDescentImplication run051Bundle = true := by
  native_decide

theorem run051Bundle_check_fails :
    Reflection.checkCertifiedSystemBundle run051Bundle = false := by
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
      "checkEntry run051Bundle is now false because the payload has no real v2(n+1)-to-certified-node entry map",
      "checkCoverage run051Bundle is now false because the payload has no real certified coverage-domain map",
      "typed S6 proof trees now have structural rule/conclusion checks, but no theorem yet closes NoEscapeSemantics"
    ]

def Run054RemainingReflectionGaps : List String :=
  [
    "checkNoEscape run051Bundle is now false until S6 proof trees construct NoEscapeSemantics run051Bundle.system",
    "checkWellFounded run051Bundle is now false until S3 ranking support and kernel path fields construct WellFoundedSystem run051Bundle.system"
  ]

def Run055MissingGlobalSemanticsGaps : List String :=
  GlobalSemantics.MissingGlobalSemanticsGaps

def Run056ProjectionStatus : List String :=
  [
      "ENTRY_PROJECTION_BUILT: run051Bundle.system.entryState is a typed parent-coordinate entry predicate",
      "COVERAGE_PROJECTION_BUILT: run051Bundle.system.covered now requires typed generated-node membership",
      "RUN056A_ENTRY_GAP: checkEntry run051Bundle is false until an entry map from arbitrary odd n to certified nodes is generated",
      "RUN056A_COVERAGE_GAP: checkCoverage run051Bundle is false until a real coverage-domain membership theorem is generated"
    ]

def Run057RemainingReflectionGaps : List String :=
    [
      "checkEntry_sound: blocked for run051Bundle by MISSING_ENTRY_TO_CERTIFIED_NODE_MAP",
      "checkCoverage_sound: blocked for run051Bundle by MISSING_COVERAGE_DOMAIN_MEMBERSHIP_THEOREM",
      "checkNoEscape_sound: blocked by MISSING_NO_ESCAPE_PROOF_TREE_SEMANTICS; checkNoEscape run051Bundle is false",
      "checkWellFounded_sound: blocked by MISSING_KERNEL_TO_PATH_LINK and MISSING_WELL_FOUNDED_RANK_BRIDGE; checkWellFounded run051Bundle is false",
      "checkCertifiedSystemBundle_sound: blocked on entry, coverage, no-escape, and well-foundedness soundness"
    ]

def Run058StructuralSemanticsStatus : List String :=
  [
      "S3_ROLE_SUPPORT_SOUND: all RUN-051 S3 roles are ranking/support facts, not transition edges",
      "S6_STRUCTURAL_PROOF_TREE_SOUND: S6 dependencies check typed certificate membership/matching claim kinds and proof trees contain a rule that closes their claim kind",
      "S4_GUARDED_SOURCE_DOMAIN_BUILT: reflected S4 source domains carry branch residue/depth and parent-coordinate map equalities",
      "DESCENT_IMPLICATION_METADATA_SOUND: descent implication checker is recorded only as metadata, not as a proof of DescentTheorem",
      "RUN058_REMAINING: checkNoEscape run051Bundle is false; no theorem yet turns S6 structural proof trees into NoEscapeSemantics"
    ]

def Run056BGlobalSemanticMapGaps : List String :=
  [
    "MISSING_PARAMETRIC_ENTRY_COVERAGE: generated entry map cannot send arbitrary a = v2(n+1) into the finite reflected node/domain set",
    "MISSING_COVERAGE_DOMAIN_MEMBERSHIP_THEOREM: generated coverage map lists domains but cannot prove arbitrary membership",
    "MISSING_APPLICABLE_EDGE_PARTITION: generated no-escape map lacks a branch partition constructing full SourceDomain witnesses",
    "MISSING_KERNEL_TO_PATH_LINK: generated well-founded bridge does not map every infinite internal path into the eliminated kernel",
    "MISSING_WELL_FOUNDED_RANK_BRIDGE: generated well-founded bridge does not reconcile guarded-kernel elimination with the rank-based WellFoundedSystem"
  ]

end Collatz
