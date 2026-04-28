(** Collatz proof-candidate bridge.

    This Rocq/Coq file proves the same theorem bridge as the Lean file:
    assuming a descent theorem for the Collatz map, every positive integer
    reaches 1.  It does not trust or import the Python verifier.  The finite
    RUN-024 certificate replay payloads still need to be ported into Rocq
    before this is a full Rocq proof of Collatz.
*)

From Coq Require Import Arith Arith.Wf_nat Lia.

Module CollatzProofCandidate.

Definition C (n : nat) : nat :=
  if Nat.eqb (n mod 2) 0 then n / 2 else 3 * n + 1.

Fixpoint iter (k n : nat) : nat :=
  match k with
  | 0 => n
  | S k' => iter k' (C n)
  end.

Lemma iter_add : forall a b n,
  iter (a + b) n = iter b (iter a n).
Proof.
  induction a as [|a IHa]; intros b n; simpl.
  - reflexivity.
  - rewrite IHa. reflexivity.
Qed.

Definition reaches_one (n : nat) : Prop :=
  exists t : nat, iter t n = 1.

Definition positive_iterates : Prop :=
  forall n k : nat, n > 0 -> iter k n > 0.

Definition descent_theorem : Prop :=
  forall n : nat, n > 1 -> exists k : nat, k >= 1 /\ iter k n < n.

Theorem descent_implies_convergence :
  positive_iterates ->
  descent_theorem ->
  forall n : nat, n > 0 -> reaches_one n.
Proof.
  intros Hpositive Hdescent.
  apply (well_founded_induction
    lt_wf
    (fun n => n > 0 -> reaches_one n)).
  intros n IH Hn_pos.
  destruct n as [|n']; [lia|].
  destruct n' as [|n''].
  - exists 0. reflexivity.
  - assert (Hgt : S (S n'') > 1) by lia.
    destruct (Hdescent (S (S n'')) Hgt) as [k [Hk_ge_one Hdesc]].
    assert (Hm_pos : iter k (S (S n'')) > 0) by
      (apply Hpositive; lia).
    destruct (IH (iter k (S (S n''))) Hdesc Hm_pos) as [t Ht].
    exists (k + t).
    rewrite iter_add.
    exact Ht.
Qed.

End CollatzProofCandidate.
