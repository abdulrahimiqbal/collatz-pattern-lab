"""Build verifier-shaped proof-action datasets for the v2 action agent."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

from rich.console import Console

from .collatz import collatz_step, first_descent_time, parity_prefix
from .proof_action_dsl import serialize_action
from .proof_action_decode import legal_action_candidates_from_state, verify_action_for_state
from .proof_action_outcome import outcome_rank, classify_action_outcome
from .proof_action_state import (
    parse_state_facts,
    state_from_debt_transition,
    state_from_finite_certificate,
    state_from_high_parent_successor,
    state_from_replay_record,
    state_from_residue_task,
)
from .proof_action_trap_states import labelled_candidates_for_state, trap_state_row
from .verifier import affine_for_parity_prefix


PROOF_ACTION_DATASET_SCHEMA = "collatz_lab.proof_action_dataset_row"
PROOF_ACTION_DATASET_REPORT_SCHEMA = "collatz_lab.proof_action_dataset_report"


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(data: Any, size: int = 16) -> str:
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()[:size]


def _split(example_id: str, seed: int) -> str:
    value = int(hashlib.sha256(f"{seed}:{example_id}".encode("utf-8")).hexdigest()[:8], 16) % 100
    if value < 80:
        return "train"
    if value < 90:
        return "val"
    if value < 97:
        return "test"
    return "challenge"


def _difficulty(gate: str, action: dict[str, Any], source: str) -> str:
    if source == "negative_mutation":
        return "medium"
    if gate == "S1":
        return "easy"
    if gate == "S2":
        steps = int(action.get("steps", 0) or 0)
        if steps <= 8:
            return "easy"
        if steps <= 12:
            return "medium"
        return "hard"
    if gate in {"S3", "S4"}:
        return "challenge"
    if gate == "S6":
        return "hard"
    return "medium"


def _modulus_bucket(action: dict[str, Any]) -> str:
    modulus = int(action.get("modulus") or action.get("from_modulus") or 0)
    if modulus <= 0:
        return "none"
    k = modulus.bit_length() - 1 if modulus & (modulus - 1) == 0 else 0
    if k <= 10:
        return "train_modulus_range"
    if k <= 13:
        return "held_out_modulus_range"
    return "challenge_modulus_range"


def _row(
    *,
    state: str,
    action: dict[str, Any],
    gate: str,
    verifier_status: str,
    reward: float,
    source: str,
    seed: int,
    next_state: str | None = None,
    closed_obligation: bool = False,
    eventually_closed: bool = False,
    distance_to_close: int | None = None,
    split: str | None = None,
) -> dict[str, Any]:
    action_text = serialize_action(action)
    payload = {"state": state, "target_action_text": action_text, "source": source}
    example_id = f"{source}:{_digest(payload)}"
    check = verify_action_for_state(action, state)
    outcome = classify_action_outcome(
        action,
        state,
        check,
        eventually_closed=eventually_closed,
        distance_to_close=distance_to_close,
    ).to_dict()
    status = "ACCEPT" if check.accepted else "REJECT"
    closure_reward = float(outcome["closure_reward"])
    return {
        "schema": PROOF_ACTION_DATASET_SCHEMA,
        "version": 2,
        "example_id": example_id,
        "split": split or _split(example_id, seed),
        "gate": gate,
        "state": state,
        "target_action": action,
        "target_action_text": action_text,
        "verifier_status": status,
        "reward": closure_reward if status == "ACCEPT" else min(float(reward), closure_reward),
        "next_state": next_state,
        "closed_obligation": bool(outcome["closed_obligation"] or closed_obligation),
        "closed_branch": bool(outcome["closed_branch"]),
        "eventually_closed": bool(eventually_closed),
        "distance_to_close": None if distance_to_close is None else int(distance_to_close),
        "outcome_class": outcome["outcome_class"],
        "closure_reward": closure_reward,
        "gate_progress_delta": float(outcome["gate_progress_delta"]),
        "net_goal_delta": int(outcome["net_goal_delta"]),
        "strict_progress": bool(outcome["strict_progress"]),
        "num_goals_before": int(outcome["num_goals_before"]),
        "num_goals_after": int(outcome["num_goals_after"]),
        "goals_closed": int(outcome["goals_closed"]),
        "goals_created": int(outcome["goals_created"]),
        "difficulty": _difficulty(gate, action, source),
        "modulus_bucket": _modulus_bucket(action),
        "source": source,
    }


def _trajectory_until(n: int, steps: int) -> list[int]:
    values = [n]
    current = n
    for _ in range(steps):
        current = collatz_step(current)
        values.append(current)
    return values


def finite_descent_certificate(n: int, *, max_steps: int = 10000) -> dict[str, Any] | None:
    descent = first_descent_time(n, max_steps=max_steps)
    if descent is None:
        return None
    values = _trajectory_until(n, descent)
    parity = "".join(str(bit) for bit in parity_prefix(n, descent))
    digest = hashlib.sha256(",".join(str(value) for value in values).encode("utf-8")).hexdigest()
    return {
        "n": n,
        "first_descent_below_n": values[-1],
        "steps_to_descent": descent,
        "parity_word": parity,
        "max_value": max(values),
        "reaches_terminal_cycle": values[-1] == 1 or n in {1, 2, 4},
        "trajectory_hash": digest,
    }


def _affine_descent_passes(modulus: int, residue: int, steps: int) -> tuple[bool, str, int, int]:
    representative = residue if residue > 0 else modulus
    bits = parity_prefix(representative, steps)
    affine_a, affine_b, affine_d = affine_for_parity_prefix(bits)
    passed = modulus % (1 << steps) == 0 and affine_d > affine_a and affine_a * representative + affine_b < affine_d * representative
    return passed, "".join(str(bit) for bit in bits), sum(bits), affine_b


def residue_descent_rows(
    *,
    k_min: int,
    k_max: int,
    max_examples: int | None,
    seed: int,
    split: str | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for k in range(k_min, k_max + 1):
        modulus = 1 << k
        for residue in range(1, modulus, 2):
            passed, parity_word, odd_count, affine_b = _affine_descent_passes(modulus, residue, k)
            if not passed:
                continue
            state = state_from_residue_task(
                modulus=modulus,
                residue=residue,
                steps=k,
                parity_word=parity_word,
                gate="S2_RESIDUE_AFFINE_DESCENT",
            )
            action = {
                "type": "PROVE_AFFINE_DESCENT",
                "target": "goal_0",
                "modulus": modulus,
                "residue": residue,
                "steps": k,
                "odd_count": odd_count,
                "affine_b": affine_b,
            }
            rows.append(
                _row(
                    state=state,
                    action=action,
                    gate="S2",
                    verifier_status="ACCEPT",
                    reward=1.0,
                    source="residue_generator",
                    seed=seed,
                    closed_obligation=True,
                    eventually_closed=True,
                    distance_to_close=1,
                    split=split,
                )
            )
            if max_examples is not None and len(rows) >= max_examples:
                return rows
    return rows


def finite_descent_rows(*, max_n: int, limit: int | None, seed: int, split: str | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rng = random.Random(seed)
    candidates = list(range(3, max(4, max_n + 1), 2))
    rng.shuffle(candidates)
    for n in candidates:
        cert = finite_descent_certificate(n)
        if cert is None:
            continue
        state = state_from_finite_certificate(cert)
        action = {"type": "CHECK_FINITE_DESCENT", "target": "goal_0", "certificate": cert}
        rows.append(
            _row(
                state=state,
                action=action,
                gate="S1",
                verifier_status="ACCEPT",
                reward=1.0,
                source="finite_descent",
                seed=seed,
                closed_obligation=True,
                eventually_closed=True,
                distance_to_close=1,
                split=split,
            )
        )
        if limit is not None and len(rows) >= limit:
            return rows
    return rows


def _load_json(path: str | Path) -> dict[str, Any] | None:
    source = Path(path)
    if not source.exists():
        return None
    return json.loads(source.read_text(encoding="utf-8"))


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    return [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def mixed_modulus_rows(path: str | Path, *, seed: int, limit: int | None = None) -> list[dict[str, Any]]:
    report = _load_json(path)
    if not report:
        return []
    rows = []
    for transition in list(report.get("transitions") or [])[:limit]:
        target = transition.get("target_state") or {}
        gain = transition.get("gain_bound") or {}
        state = state_from_debt_transition(transition)
        action = {
            "type": "CHECK_DEBT_DECREASE",
            "target": "goal_0",
            "branch_id": str(transition.get("branch_id")),
            "gain_num": int(gain.get("numerator", 0)),
            "gain_den": int(gain.get("denominator", 1)),
            "valuation": int(target.get("valuation", 0)),
        }
        accepted = bool(transition.get("exact_congruence_passed")) and bool(transition.get("local_descent_passed"))
        rows.append(
            _row(
                state=state,
                action=action,
                gate="S3",
                verifier_status="ACCEPT" if accepted else "REJECT",
                reward=1.0 if accepted else -0.5,
                source="mixed_modulus_debt",
                seed=seed,
                closed_obligation=accepted,
                eventually_closed=accepted,
                distance_to_close=1 if accepted else None,
            )
        )
        if not accepted:
            introduce = {
                "type": "INTRODUCE_DEBT_FUNCTION",
                "target": "goal_0",
                "function_id": "mixed_log_gain_rank",
                "variables": ["parent_level", "rho_mod_3a", "log2_gain_bound"],
            }
            rows.append(
                _row(
                    state=state,
                    action=introduce,
                    gate="S3",
                    verifier_status="ACCEPT",
                    reward=0.25,
                    source="mixed_modulus_debt",
                    seed=seed,
                    closed_obligation=False,
                    eventually_closed=False,
                    distance_to_close=None,
                )
            )
    return rows


def high_parent_rows(path: str | Path, *, seed: int, limit: int | None = None) -> list[dict[str, Any]]:
    report = _load_json(path)
    if not report:
        return []
    rows = []
    families = list(report.get("mixed_successor_families") or [])
    if limit is not None:
        families = families[:limit]
    for family in families:
        for valuation_family in list(family.get("valuation_family_samples") or [])[:2]:
            transition_certificate = (
                valuation_family.get("transition_certificate")
                or valuation_family.get("symbolic_transition_certificate")
                or valuation_family.get("high_parent_successor_exact_certificate")
            )
            if not isinstance(transition_certificate, dict):
                continue
            state = state_from_high_parent_successor(family, valuation_family)
            action = {
                "type": "DERIVE_PARENT_TRANSITION",
                "target": "goal_0",
                "branch_id": str(family.get("branch_id")),
                "source_parent": int(family.get("a", 0)),
                "target_parent": int(valuation_family.get("target_parent_level", 0)),
                "valuation": int(valuation_family.get("valuation", 0)),
                "transition_certificate": transition_certificate,
            }
            rows.append(
                _row(
                    state=state,
                    action=action,
                    gate="S4",
                    verifier_status="ACCEPT" if valuation_family.get("sample_checks_passed") else "REJECT",
                    reward=0.8 if valuation_family.get("sample_checks_passed") else -0.5,
                    source="exact_high_parent_successor",
                    seed=seed,
                    closed_obligation=False,
                    eventually_closed=False,
                )
            )
    return rows


def replay_rows(paths: list[str | Path], *, seed: int, limit: int | None = None) -> list[dict[str, Any]]:
    source_rows: list[dict[str, Any]] = []
    for path in paths:
        source_rows.extend(_load_jsonl(path))
    if limit is not None:
        source_rows = source_rows[:limit]
    rows = []
    for record in source_rows:
        state = state_from_replay_record(record)
        repair = str((record.get("target") or {}).get("repair_action") or "STRICT_THEOREM_COMPILER_REPAIR")
        action = {"type": "APPLY_LEMMA", "target": "goal_0", "lemma_id": repair, "bindings": {"source": "proof_replay"}}
        rows.append(
            _row(
                state=state,
                action=action,
                gate="S6",
                verifier_status="ACCEPT",
                reward=0.1,
                source="proof_replay",
                seed=seed,
                closed_obligation=False,
                eventually_closed=False,
            )
        )
    return rows


def mutate_action(action: dict[str, Any], rng: random.Random) -> dict[str, Any] | None:
    mutated = json.loads(json.dumps(action))
    kind = mutated.get("type")
    if kind == "PROVE_AFFINE_DESCENT":
        choice = rng.choice(["residue", "steps", "odd_count"])
        if choice == "residue":
            mutated["residue"] = (int(mutated["residue"]) + 2) % int(mutated["modulus"])
            if mutated["residue"] % 2 == 0:
                mutated["residue"] = (mutated["residue"] + 1) % int(mutated["modulus"])
        elif choice == "steps":
            mutated["steps"] = int(mutated["steps"]) + 1
        else:
            mutated["odd_count"] = max(0, int(mutated["odd_count"]) - 1)
    elif kind == "CHECK_FINITE_DESCENT":
        mutated["certificate"]["parity_word"] = mutated["certificate"]["parity_word"][::-1]
    elif kind == "UNROLL_PARITY":
        parity = str(mutated["parity_word"])
        mutated["parity_word"] = ("1" if parity[:1] == "0" else "0") + parity[1:]
    elif kind == "CHECK_DEBT_DECREASE":
        mutated["gain_num"] = int(mutated["gain_den"]) + abs(int(mutated["gain_num"])) + 1
    elif kind == "DERIVE_PARENT_TRANSITION":
        mutated["valuation"] = int(mutated["valuation"]) + 1
    else:
        return None
    try:
        serialize_action(mutated)
    except Exception:
        return None
    return mutated


def add_negative_mutations(rows: list[dict[str, Any]], *, per_positive: int, seed: int) -> list[dict[str, Any]]:
    if per_positive <= 0:
        return rows
    rng = random.Random(seed)
    out = list(rows)
    positives = [row for row in rows if row.get("verifier_status") == "ACCEPT" and row.get("closed_obligation")]
    for row in positives:
        for _ in range(per_positive):
            mutated = mutate_action(dict(row["target_action"]), rng)
            if mutated is None:
                continue
            out.append(
                _row(
                    state=row["state"],
                    action=mutated,
                    gate=row["gate"],
                    verifier_status="REJECT",
                    reward=-1.0,
                    source="negative_mutation",
                    seed=seed,
                    closed_obligation=False,
                    eventually_closed=False,
                    split=row["split"],
                )
            )
    return out


def _split_for_state_rows(rows: list[dict[str, Any]], seed: int) -> dict[str, str]:
    split_by_state: dict[str, str] = {}
    for row in rows:
        state = str(row["state"])
        if state in split_by_state:
            continue
        gate = str(row.get("gate", ""))
        action = row.get("target_action") or {}
        source = str(row.get("source", ""))
        value = int(hashlib.sha256(f"{seed}:{state}".encode("utf-8")).hexdigest()[:8], 16) % 100
        split = _split(str(row.get("example_id", state)), seed)
        if gate == "S2":
            steps = int(action.get("steps", 0) or parse_state_facts(state).get("steps", 0) or 0)
            if steps <= 10:
                split = "train"
            elif steps == 11:
                split = "val"
            elif steps in {12, 13}:
                split = "test"
            else:
                split = "challenge"
        elif gate in {"S3", "S4", "S6"} or source in {"mixed_modulus_debt", "exact_high_parent_successor", "proof_replay"}:
            if value < 60:
                split = "train"
            elif value < 75:
                split = "val"
            elif value < 90:
                split = "test"
            else:
                split = "challenge"
        split_by_state[state] = split
    return split_by_state


def apply_stratified_splits(rows: list[dict[str, Any]], *, seed: int) -> list[dict[str, Any]]:
    split_by_state = _split_for_state_rows(rows, seed)
    out = []
    for row in rows:
        copied = dict(row)
        copied["split"] = split_by_state.get(str(row["state"]), str(row.get("split", "train")))
        out.append(copied)
    return out


def _dedupe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    out = []
    for row in rows:
        key = (str(row["state"]), str(row["target_action_text"]), str(row["source"]))
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def _candidate_row_from_action(row: dict[str, Any], action: dict[str, Any], *, seed: int, source: str) -> dict[str, Any]:
    check = verify_action_for_state(action, str(row["state"]))
    return _row(
        state=str(row["state"]),
        action=action,
        gate=str(row.get("gate", "S2")),
        verifier_status="ACCEPT" if check.accepted else "REJECT",
        reward=1.0 if check.accepted else -0.5,
        source=source,
        seed=seed,
        closed_obligation=check.closed_obligation,
        eventually_closed=bool(check.closed_obligation),
        distance_to_close=1 if check.closed_obligation else None,
        split=str(row.get("split", "train")),
    )


def pairwise_examples(rows: list[dict[str, Any]], *, seed: int, max_pairs_per_state: int = 8) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["state"]), []).append(row)
    pairs: list[dict[str, Any]] = []
    for state, state_rows in grouped.items():
        enriched: dict[str, dict[str, Any]] = {str(row["target_action_text"]): row for row in state_rows}
        anchor = state_rows[0]
        for candidate in legal_action_candidates_from_state(state, max_candidates=24):
            text = serialize_action(candidate)
            if text not in enriched:
                enriched[text] = _candidate_row_from_action(anchor, candidate, seed=seed, source="ranker_candidate")
        ordered = sorted(enriched.values(), key=outcome_rank, reverse=True)
        if len(ordered) < 2:
            continue
        emitted = 0
        for better in ordered:
            for worse in reversed(ordered):
                if outcome_rank(better) <= outcome_rank(worse):
                    continue
                reason = "closed_vs_reduced" if better.get("closed_obligation") and not worse.get("closed_obligation") else "accepted_vs_rejected"
                if float(better.get("gate_progress_delta", 0.0) or 0.0) > float(worse.get("gate_progress_delta", 0.0) or 0.0):
                    reason = "gate_progress"
                if better.get("distance_to_close") is not None and worse.get("distance_to_close") is not None:
                    if int(better["distance_to_close"]) < int(worse["distance_to_close"]):
                        reason = "distance_to_close"
                pairs.append(
                    {
                        "schema": "collatz_lab.proof_action_pair",
                        "version": 1,
                        "example_id": f"pair:{_digest({'state': state, 'better': better['target_action_text'], 'worse': worse['target_action_text']})}",
                        "split": str(anchor.get("split", "train")),
                        "gate": str(anchor.get("gate", "UNKNOWN")),
                        "state": state,
                        "better_action": str(better["target_action_text"]),
                        "worse_action": str(worse["target_action_text"]),
                        "better_outcome_class": str(better.get("outcome_class")),
                        "worse_outcome_class": str(worse.get("outcome_class")),
                        "better_closure_reward": float(better.get("closure_reward", better.get("reward", 0.0)) or 0.0),
                        "worse_closure_reward": float(worse.get("closure_reward", worse.get("reward", 0.0)) or 0.0),
                        "reason": reason,
                    }
                )
                emitted += 1
                if emitted >= max_pairs_per_state:
                    break
            if emitted >= max_pairs_per_state:
                break
    return pairs


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def _state_hash(state: str) -> str:
    return hashlib.sha256(state.encode("utf-8")).hexdigest()


def _frontier_row_from_dataset_row(row: dict[str, Any], *, frontier_kind: str, difficulty: str, path_length: int | None = None) -> dict[str, Any]:
    state = str(row["state"])
    candidates = labelled_candidates_for_state(state)
    return {
        "schema": "collatz_lab.proof_action_frontier_row",
        "version": 1,
        "example_id": f"{frontier_kind}:{_digest({'state': state, 'kind': frontier_kind})}",
        "split": "challenge",
        "gate": str(row.get("gate", "UNKNOWN")),
        "source": str(row.get("source", frontier_kind)),
        "frontier_kind": frontier_kind,
        "difficulty": difficulty,
        "state": state,
        "target_action_text": row.get("target_action_text"),
        "candidates": candidates,
        "known_min_steps_to_close": path_length,
        "known_min_steps_to_progress": path_length,
    }


def _sample_residue_frontier(
    *,
    k_min: int,
    k_max: int,
    seed: int,
    max_rows: int,
    frontier_kind: str,
    difficulty: str,
    train_hashes: set[str],
) -> list[dict[str, Any]]:
    rng = random.Random(seed + k_min * 1009 + k_max)
    rows: list[dict[str, Any]] = []
    for k in range(k_min, k_max + 1):
        modulus = 1 << k
        attempts = 0
        while attempts < 300 and len(rows) < max_rows:
            attempts += 1
            residue = rng.randrange(1, modulus, 2)
            passed, parity_word, odd_count, affine_b = _affine_descent_passes(modulus, residue, k)
            if not passed:
                continue
            state = state_from_residue_task(
                modulus=modulus,
                residue=residue,
                steps=k,
                parity_word=parity_word,
                gate="S2_HELDOUT_RESIDUE_FRONTIER",
            )
            if _state_hash(state) in train_hashes:
                continue
            action = {
                "type": "PROVE_AFFINE_DESCENT",
                "target": "goal_0",
                "modulus": modulus,
                "residue": residue,
                "steps": k,
                "odd_count": odd_count,
                "affine_b": affine_b,
            }
            base = _row(
                state=state,
                action=action,
                gate="S2",
                verifier_status="ACCEPT",
                reward=1.0,
                source="heldout_residue_frontier",
                seed=seed,
                closed_obligation=True,
                eventually_closed=True,
                distance_to_close=1,
                split="challenge",
            )
            rows.append(_frontier_row_from_dataset_row(base, frontier_kind=frontier_kind, difficulty=difficulty, path_length=1))
        if len(rows) >= max_rows:
            break
    return rows


def _frontier_candidates_from_rows(rows: list[dict[str, Any]], *, train_hashes: set[str], limit: int, frontier_kind: str, difficulty: str, path_range: tuple[int, int]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        state = str(row.get("state", ""))
        state_hash = _state_hash(state)
        if not state or state_hash in train_hashes or state_hash in seen:
            continue
        seen.add(state_hash)
        path_length = path_range[0] + (index % max(1, path_range[1] - path_range[0] + 1))
        out.append(_frontier_row_from_dataset_row(row, frontier_kind=frontier_kind, difficulty=difficulty, path_length=path_length))
        if len(out) >= limit:
            break
    return out


def build_frontier_eval_dataset(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    train_rows = _load_jsonl(getattr(args, "train_rows", "data/proof_action_v2_ranker/train.jsonl"))
    train_hashes = {_state_hash(str(row.get("state", ""))) for row in train_rows}

    finite = finite_descent_rows(max_n=min(args.max_n, 100000), limit=120, seed=args.seed, split="challenge")
    residue_easy = residue_descent_rows(k_min=10, k_max=min(12, args.residue_k_max), max_examples=120, seed=args.seed, split="challenge")
    s3_rows = mixed_modulus_rows(args.mixed_modulus_debt, seed=args.seed, limit=1200)
    s4_rows = high_parent_rows(args.high_parent_bypass, seed=args.seed, limit=600)
    s6_rows = replay_rows([args.proof_replay, args.proof_attempts_log], seed=args.seed, limit=200)

    easy = _frontier_candidates_from_rows(
        finite + residue_easy,
        train_hashes=train_hashes,
        limit=160,
        frontier_kind="easy_one_step",
        difficulty="easy",
        path_range=(1, 1),
    )
    medium = _frontier_candidates_from_rows(
        s3_rows + s4_rows + s6_rows,
        train_hashes=train_hashes,
        limit=180,
        frontier_kind="medium_3_to_5_step",
        difficulty="medium",
        path_range=(3, 5),
    )
    hard = _frontier_candidates_from_rows(
        list(reversed(s3_rows + s4_rows + s6_rows)),
        train_hashes=train_hashes,
        limit=180,
        frontier_kind="hard_10_to_30_step",
        difficulty="hard",
        path_range=(10, 30),
    )
    s3_frontier = _frontier_candidates_from_rows(
        s3_rows,
        train_hashes=train_hashes,
        limit=220,
        frontier_kind="s3_frontier",
        difficulty="challenge",
        path_range=(5, 20),
    )
    s4_frontier = _frontier_candidates_from_rows(
        s4_rows,
        train_hashes=train_hashes,
        limit=220,
        frontier_kind="s4_lifting_frontier",
        difficulty="challenge",
        path_range=(5, 20),
    )
    s6_frontier = _frontier_candidates_from_rows(
        s6_rows,
        train_hashes=train_hashes,
        limit=120,
        frontier_kind="s6_strict_frontier",
        difficulty="challenge",
        path_range=(5, 20),
    )
    heldout = _sample_residue_frontier(
        k_min=max(args.residue_k_min, 15),
        k_max=args.residue_k_max,
        seed=args.seed,
        max_rows=220,
        frontier_kind="heldout_modulus_challenge",
        difficulty="challenge",
        train_hashes=train_hashes,
    )
    trap_source = s4_frontier + s3_frontier + heldout
    traps: list[dict[str, Any]] = []
    if args.trap_states:
        for row in trap_source:
            trap = trap_state_row(
                state=str(row["state"]),
                gate=str(row["gate"]),
                source=str(row.get("source", "frontier")),
                difficulty="trap",
            )
            if trap and _state_hash(str(trap["state"])) not in train_hashes:
                traps.append(trap)
            if len(traps) >= 160:
                break

    files = {
        "easy_one_step.jsonl": easy,
        "medium_3_to_5_step.jsonl": medium if args.multi_step_states else [],
        "hard_10_to_30_step.jsonl": hard if args.multi_step_states else [],
        "trap_states.jsonl": traps,
        "s3_frontier.jsonl": s3_frontier if args.s3_s4_s6_focus else [],
        "s4_lifting_frontier.jsonl": s4_frontier if args.s3_s4_s6_focus else [],
        "s6_strict_frontier.jsonl": s6_frontier if args.s3_s4_s6_focus else [],
        "heldout_modulus_challenge.jsonl": heldout,
    }
    for name, rows in files.items():
        _write_jsonl(out_dir / name, rows)
    all_rows = [row for rows in files.values() for row in rows]
    summary = {
        "schema": "collatz_lab.proof_action_frontier_eval_build_summary",
        "version": 1,
        "status": "BUILT_FRONTIER_EVAL",
        "row_count": len(all_rows),
        "file_counts": {name: len(rows) for name, rows in files.items()},
        "gate_counts": dict(Counter(str(row.get("gate", "UNKNOWN")) for row in all_rows)),
        "train_state_hashes_excluded": len(train_hashes),
        "paths": {name: str(out_dir / name) for name in files},
    }
    (out_dir / "frontier_eval_build_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def build_hard_frontier_dataset_from_args(args: argparse.Namespace) -> dict[str, Any]:
    from .proof_action_frontier_generator import build_hard_frontier_dataset

    return build_hard_frontier_dataset(
        out=args.out,
        residue_k_min=args.residue_k_min,
        residue_k_max=args.residue_k_max,
        max_frontier_states=args.max_frontier_states,
        s3=args.s3,
        s4=args.s4,
        s6=args.s6,
        seed=args.seed,
        train_rows=args.train_rows,
    )


def write_dataset(rows: list[dict[str, Any]], out: str | Path, *, pairwise_ranker_examples: bool = True, seed: int = 1337) -> dict[str, Any]:
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = _dedupe(rows)
    all_path = out_dir / "rows.jsonl"
    _write_jsonl(all_path, rows)
    for split in ("train", "val", "test", "challenge"):
        split_rows = [row for row in rows if row["split"] == split]
        _write_jsonl(out_dir / f"{split}.jsonl", split_rows)
    train_rows = [row for row in rows if row["split"] == "train"]
    train_policy = [
        row
        for row in train_rows
        if row.get("verifier_status") == "ACCEPT" and float(row.get("closure_reward", row.get("reward", 0.0)) or 0.0) > 0
    ]
    train_value = train_rows
    pairs = pairwise_examples(rows, seed=seed) if pairwise_ranker_examples else []
    train_pairs = [pair for pair in pairs if pair.get("split") == "train"] or pairs[: max(1, min(len(pairs), 2000))]
    _write_jsonl(out_dir / "train_policy.jsonl", train_policy)
    _write_jsonl(out_dir / "train_value.jsonl", train_value)
    _write_jsonl(out_dir / "train_pairs.jsonl", train_pairs)
    _write_jsonl(out_dir / "val_stratified.jsonl", [row for row in rows if row["split"] == "val"])
    _write_jsonl(out_dir / "test_stratified.jsonl", [row for row in rows if row["split"] == "test"])
    challenge_s3_s4 = [
        row
        for row in rows
        if row["split"] == "challenge" and str(row.get("gate")) in {"S3", "S4", "S6"}
    ]
    if not challenge_s3_s4:
        challenge_s3_s4 = [row for row in rows if str(row.get("gate")) in {"S3", "S4", "S6"}]
    _write_jsonl(out_dir / "challenge_s3_s4.jsonl", challenge_s3_s4)
    source_counts = Counter(row["source"] for row in rows)
    status_counts = Counter(row["verifier_status"] for row in rows)
    split_counts = Counter(row["split"] for row in rows)
    gate_counts = Counter(row["gate"] for row in rows)
    outcome_counts = Counter(row.get("outcome_class") for row in rows)
    report = {
        "schema": PROOF_ACTION_DATASET_REPORT_SCHEMA,
        "version": 2,
        "status": "BUILT_PROOF_ACTION_V2_DATASET",
        "row_count": len(rows),
        "train_policy_rows": len(train_policy),
        "train_value_rows": len(train_value),
        "train_pair_rows": len(train_pairs),
        "source_counts": dict(source_counts),
        "verifier_status_counts": dict(status_counts),
        "split_counts": dict(split_counts),
        "gate_counts": dict(gate_counts),
        "outcome_counts": dict(outcome_counts),
        "paths": {split: str(out_dir / f"{split}.jsonl") for split in ("train", "val", "test", "challenge")}
        | {
            "rows": str(all_path),
            "train_policy": str(out_dir / "train_policy.jsonl"),
            "train_value": str(out_dir / "train_value.jsonl"),
            "train_pairs": str(out_dir / "train_pairs.jsonl"),
            "val_stratified": str(out_dir / "val_stratified.jsonl"),
            "test_stratified": str(out_dir / "test_stratified.jsonl"),
            "challenge_s3_s4": str(out_dir / "challenge_s3_s4.jsonl"),
        },
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def build_dataset(args: argparse.Namespace) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    rows.extend(
        residue_descent_rows(
            k_min=args.residue_k_min,
            k_max=args.residue_k_max,
            max_examples=None,
            seed=args.seed,
        )
    )
    rows.extend(finite_descent_rows(max_n=args.max_n, limit=min(args.max_n, 2000), seed=args.seed))
    rows.extend(mixed_modulus_rows(args.mixed_modulus_debt, seed=args.seed, limit=2000))
    rows.extend(high_parent_rows(args.high_parent_bypass, seed=args.seed, limit=500))
    rows.extend(replay_rows([args.proof_replay, args.proof_attempts_log], seed=args.seed, limit=2000))
    rows = add_negative_mutations(rows, per_positive=args.negatives_per_positive, seed=args.seed)
    if getattr(args, "stratified_splits", False):
        rows = apply_stratified_splits(rows, seed=args.seed)
    return write_dataset(
        rows,
        args.out,
        pairwise_ranker_examples=getattr(args, "pairwise_ranker_examples", True),
        seed=args.seed,
    )


def build_tiny_dataset(args: argparse.Namespace) -> dict[str, Any]:
    finite = finite_descent_rows(max_n=200, limit=max(1, args.num_traces // 2), seed=args.seed, split="train")
    residue = residue_descent_rows(k_min=4, k_max=8, max_examples=args.num_traces - len(finite), seed=args.seed, split="train")
    rows = (finite + residue)[: args.num_traces]
    # Tiny overfit evaluates replay of the same accepted traces; all splits are
    # train by design so the gate checks memorized action syntax and verifier IO.
    return write_dataset(rows, args.out, pairwise_ranker_examples=True, seed=args.seed)


def _bool_arg(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    lowered = value.lower()
    if lowered in {"1", "true", "yes", "y", "on"}:
        return True
    if lowered in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"expected boolean, got {value!r}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build v2 typed proof-action datasets.")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--out", required=True)
    build.add_argument("--max-n", type=int, default=100000)
    build.add_argument("--residue-k-min", type=int, default=4)
    build.add_argument("--residue-k-max", type=int, default=14)
    build.add_argument("--negatives-per-positive", type=int, default=3)
    build.add_argument("--seed", type=int, default=1337)
    build.add_argument("--mixed-modulus-debt", default="reports/debt_induction/mixed_modulus_debt_verifier.json")
    build.add_argument("--high-parent-bypass", default="reports/debt_induction/high_parent_bypass_report.json")
    build.add_argument("--proof-replay", default="reports/proof_replay_training.jsonl")
    build.add_argument("--proof-attempts-log", default="proof_attempts.jsonl")
    build.add_argument("--pairwise-ranker-examples", type=_bool_arg, default=True)
    build.add_argument("--stratified-splits", type=_bool_arg, default=False)

    tiny = sub.add_parser("build-tiny")
    tiny.add_argument("--out", required=True)
    tiny.add_argument("--num-traces", type=int, default=10)
    tiny.add_argument("--seed", type=int, default=1337)

    frontier = sub.add_parser("build-frontier-eval")
    frontier.add_argument("--out", required=True)
    frontier.add_argument("--max-n", type=int, default=1000000)
    frontier.add_argument("--residue-k-min", type=int, default=10)
    frontier.add_argument("--residue-k-max", type=int, default=22)
    frontier.add_argument("--trap-states", type=_bool_arg, default=True)
    frontier.add_argument("--multi-step-states", type=_bool_arg, default=True)
    frontier.add_argument("--s3-s4-s6-focus", type=_bool_arg, default=True)
    frontier.add_argument("--seed", type=int, default=1337)
    frontier.add_argument("--train-rows", default="data/proof_action_v2_ranker/train.jsonl")
    frontier.add_argument("--mixed-modulus-debt", default="reports/debt_induction/mixed_modulus_debt_verifier.json")
    frontier.add_argument("--high-parent-bypass", default="reports/debt_induction/high_parent_bypass_report.json")
    frontier.add_argument("--proof-replay", default="reports/proof_replay_training.jsonl")
    frontier.add_argument("--proof-attempts-log", default="proof_attempts.jsonl")

    hard = sub.add_parser("build-hard-frontier")
    hard.add_argument("--out", required=True)
    hard.add_argument("--residue-k-min", type=int, default=16)
    hard.add_argument("--residue-k-max", type=int, default=30)
    hard.add_argument("--max-frontier-states", type=int, default=50000)
    hard.add_argument("--s3", type=_bool_arg, default=True)
    hard.add_argument("--s4", type=_bool_arg, default=True)
    hard.add_argument("--s6", type=_bool_arg, default=True)
    hard.add_argument("--seed", type=int, default=1337)
    hard.add_argument("--train-rows", default="data/proof_action_v2_ranker/train.jsonl")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    if args.command == "build-tiny":
        report = build_tiny_dataset(args)
    elif args.command == "build-frontier-eval":
        report = build_frontier_eval_dataset(args)
    elif args.command == "build-hard-frontier":
        report = build_hard_frontier_dataset_from_args(args)
    else:
        report = build_dataset(args)
    Console().print(report)


if __name__ == "__main__":
    main()
