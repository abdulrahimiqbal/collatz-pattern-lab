"""Canonical proof-state serialization for the v2 proof-action agent."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

from .verifier import affine_for_parity_prefix


_ATTR_RE = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)="([^"]*)"')
_TAG_RE = re.compile(r"<(?P<tag>[A-Z_]+)(?P<attrs>[^>]*)>")
_GATE_RE = re.compile(r"<GATE>(?P<gate>[^<]+)</GATE>")


def _esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _tag(name: str, attrs: dict[str, Any] | None = None, body: str | None = None) -> str:
    attr_text = ""
    if attrs:
        attr_text = " " + " ".join(f'{key}="{_esc(value)}"' for key, value in attrs.items())
    if body is None:
        return f"<{name}{attr_text}/>"
    return f"<{name}{attr_text}>{body}</{name}>"


def _section(name: str, lines: list[str]) -> list[str]:
    return [f"<{name}>", *lines, f"</{name}>"]


def canonical_state(
    *,
    gate: str,
    goal: str,
    goal_id: str = "goal_0",
    goal_attrs: dict[str, Any] | None = None,
    assumptions: list[str] | None = None,
    affine_forms: list[str] | None = None,
    known_lemmas: list[str] | None = None,
    facts: list[dict[str, Any]] | None = None,
    open_obligations: list[str] | None = None,
) -> str:
    """Build the structured model input string used by action policies."""

    attrs = {"id": goal_id, **(goal_attrs or {})}
    lines = [_tag("GATE", body=_esc(gate)), _tag("GOAL", attrs, _esc(goal))]
    lines.extend(_section("ASSUMPTIONS", [_esc(line) for line in assumptions or []]))
    if affine_forms is not None:
        lines.extend(_section("AFFINE_FORMS", [_esc(line) for line in affine_forms]))
    if known_lemmas is not None:
        lines.extend(_section("KNOWN_LEMMAS", [_esc(line) for line in known_lemmas]))
    if facts is not None:
        lines.append("<FACTS>")
        for fact in facts:
            ordered = {key: fact[key] for key in sorted(fact)}
            lines.append(_tag("FACT", ordered))
        lines.append("</FACTS>")
    lines.extend(_section("OPEN_OBLIGATIONS", [_esc(item) for item in open_obligations or [goal_id]]))
    return "\n".join(lines)


def parse_state_facts(state: str) -> dict[str, Any]:
    """Extract machine-readable fields from a canonical state string."""

    facts: dict[str, Any] = {"known_lemmas": [], "open_obligations": []}
    gate = _GATE_RE.search(state)
    if gate:
        facts["gate"] = html.unescape(gate.group("gate"))
    for match in _TAG_RE.finditer(state):
        tag = match.group("tag")
        attrs = {key: html.unescape(value) for key, value in _ATTR_RE.findall(match.group("attrs"))}
        if tag == "GOAL":
            facts["target"] = attrs.get("id", "goal_0")
            facts["goal_kind"] = attrs.get("kind")
            for key, value in attrs.items():
                if key in {"modulus", "residue", "steps", "odd_count", "affine_b", "n", "max_value"}:
                    facts[key] = int(value)
                elif key in {"local_descent_passed", "sample_checks_passed", "exact_congruence_passed"}:
                    facts[key] = value.lower() == "true"
                else:
                    facts[key] = value
        elif tag == "FACT":
            kind = attrs.get("kind")
            if kind:
                facts.setdefault(f"{kind}_facts", []).append(attrs)
            for key, value in attrs.items():
                if key in {
                    "modulus",
                    "residue",
                    "steps",
                    "odd_count",
                    "affine_b",
                    "valuation",
                    "gain_num",
                    "gain_den",
                    "source_parent",
                    "target_parent",
                    "n",
                    "first_descent_below_n",
                    "steps_to_descent",
                    "max_value",
                    "coverage_modulus",
                    "covered_residue_count",
                    "residual_start",
                    "residual_end",
                    "leaf_certificate_count",
                }:
                    attrs[key] = int(value)
                elif key in {"reaches_terminal_cycle", "local_descent_passed", "sample_checks_passed", "exact_congruence_passed"}:
                    attrs[key] = value.lower() == "true"
            if kind == "residue_affine":
                facts.update({key: attrs[key] for key in attrs if key != "kind"})
            elif kind == "finite_certificate":
                facts["certificate"] = {key: attrs[key] for key in attrs if key != "kind"}
            elif kind == "debt_transition":
                facts["debt_transition"] = {key: attrs[key] for key in attrs if key != "kind"}
            elif kind == "high_parent_successor":
                facts["high_parent_successor"] = {key: attrs[key] for key in attrs if key != "kind"}
            elif kind == "lemma":
                facts.setdefault("known_lemmas", []).append(str(attrs.get("lemma_id", "")))
    in_known_lemmas = False
    for line in state.splitlines():
        clean = html.unescape(line.strip())
        if clean == "<KNOWN_LEMMAS>":
            in_known_lemmas = True
            continue
        if clean == "</KNOWN_LEMMAS>":
            in_known_lemmas = False
            continue
        if in_known_lemmas and clean and not clean.startswith("<"):
            facts.setdefault("known_lemmas", []).append(clean)
        if clean.startswith("lemma_id="):
            facts.setdefault("known_lemmas", []).append(clean.split("=", 1)[1])
        if clean.startswith("goal_"):
            facts.setdefault("open_obligations", []).append(clean)
    facts["known_lemmas"] = list(dict.fromkeys(item for item in facts.get("known_lemmas", []) if item))
    return facts


def state_from_residue_task(
    *,
    modulus: int,
    residue: int,
    steps: int,
    parity_word: str,
    gate: str = "S2_RESIDUE_AFFINE_DESCENT",
    target: str = "goal_0",
) -> str:
    prefix = [int(bit) for bit in parity_word]
    odd_count = sum(prefix)
    affine_a, affine_b, affine_d = affine_for_parity_prefix(prefix)
    return canonical_state(
        gate=gate,
        goal=f"prove descent for n == {residue} mod {modulus}",
        goal_id=target,
        goal_attrs={
            "kind": "residue_descent",
            "modulus": modulus,
            "residue": residue,
            "steps": steps,
            "odd_count": odd_count,
            "affine_b": affine_b,
        },
        assumptions=["n > 0", "n odd", f"n == {residue} mod {modulus}"],
        affine_forms=[
            f"candidate_0: T^{steps}(n) = ({affine_a}*n + {affine_b}) / {affine_d} ; parity={parity_word}"
        ],
        known_lemmas=["parity_prefix_stable_mod_2_power", "affine_descent_slope"],
        facts=[
            {
                "kind": "residue_affine",
                "target": target,
                "modulus": modulus,
                "residue": residue,
                "steps": steps,
                "odd_count": odd_count,
                "affine_b": affine_b,
                "parity_word": parity_word,
            }
        ],
    )


def state_from_finite_certificate(certificate: dict[str, Any], *, target: str = "goal_0") -> str:
    n = certificate["n"]
    return canonical_state(
        gate="S1_FINITE_DESCENT_CERTIFICATE",
        goal=f"check finite descent certificate for n={n}",
        goal_id=target,
        goal_attrs={"kind": "finite_descent", "n": n},
        assumptions=["n > 0", "terminal cycle is represented as TERMINAL_CYCLE"],
        known_lemmas=["finite_descent_implies_local_closure"],
        facts=[{"kind": "finite_certificate", "target": target, **certificate}],
    )


def state_from_debt_transition(row: dict[str, Any], *, target: str = "goal_0") -> str:
    source = row.get("source_state") or {}
    target_state = row.get("target_state") or {}
    gain = row.get("gain_bound") or {}
    gain_num = int(gain.get("numerator", 0))
    gain_den = int(gain.get("denominator", 1))
    branch_id = str(row.get("branch_id", "unknown_branch"))
    valuation = int(target_state.get("valuation", 0))
    local = bool(row.get("local_descent_passed"))
    return canonical_state(
        gate="S3_MIXED_MODULUS_DEBT_TRANSITION",
        goal=f"check debt decrease for {branch_id}",
        goal_id=target,
        goal_attrs={
            "kind": "debt_transition",
            "branch_id": branch_id,
            "valuation": valuation,
            "local_descent_passed": local,
        },
        assumptions=[
            f"source P{source.get('parent_level')} residue {source.get('odd_coordinate_residue')} mod {source.get('odd_coordinate_modulus')}",
            f"target P{target_state.get('parent_level')} valuation {valuation}",
            "exact congruence has priority over learned rank guesses",
        ],
        known_lemmas=["mixed_modulus_debt_transition_exactness"],
        facts=[
            {
                "kind": "debt_transition",
                "target": target,
                "branch_id": branch_id,
                "valuation": valuation,
                "source_parent": int(source.get("parent_level", 0)),
                "target_parent": int(target_state.get("parent_level", 0)),
                "gain_num": gain_num,
                "gain_den": gain_den,
                "local_descent_passed": local,
                "exact_congruence_passed": bool(row.get("exact_congruence_passed")),
            }
        ],
    )


def state_from_high_parent_successor(row: dict[str, Any], valuation_family: dict[str, Any], *, target: str = "goal_0") -> str:
    branch_id = str(row.get("branch_id", "unknown_branch"))
    valuation = int(valuation_family.get("valuation", 0))
    target_parent = int(valuation_family.get("target_parent_level", row.get("known_target_parent_floor", 0)))
    return canonical_state(
        gate="S4_HIGH_PARENT_SUCCESSOR_FACT",
        goal=f"derive parent transition for {branch_id} at valuation {valuation}",
        goal_id=target,
        goal_attrs={"kind": "high_parent_successor", "branch_id": branch_id, "valuation": valuation},
        assumptions=[
            str(row.get("successor_family_rule", "")),
            f"z_family={row.get('z_family')}",
            "actual trajectory samples are compressed into successor congruence facts",
        ],
        known_lemmas=["high_parent_successor_exactness", "odd_modular_inverse_lift"],
        facts=[
            {
                "kind": "high_parent_successor",
                "target": target,
                "branch_id": branch_id,
                "source_parent": int(row.get("a", 0)),
                "target_parent": target_parent,
                "valuation": valuation,
                "sample_checks_passed": bool(valuation_family.get("sample_checks_passed", row.get("sample_checks_passed"))),
            }
        ],
    )


def state_from_replay_record(record: dict[str, Any], *, target: str = "goal_0") -> str:
    blocker = str((record.get("target") or {}).get("first_blocker") or (record.get("blocking_steps") or ["UNKNOWN"])[0])
    repair = str((record.get("target") or {}).get("repair_action") or "SELF_CORRECT_PROOF_DSL")
    return canonical_state(
        gate="S6_PROOF_REPLAY_REPAIR",
        goal=f"repair failed proof attempt blocker {blocker}",
        goal_id=target,
        goal_attrs={"kind": "proof_replay", "blocker": blocker},
        assumptions=[
            f"run_id={record.get('run_id')}",
            f"proof_confidence={record.get('proof_confidence_percent', 0.0)}",
            "strict theorem verifier remains authoritative",
        ],
        known_lemmas=["strict_verifier_blocks_confidence", repair],
        facts=[{"kind": "lemma", "target": target, "lemma_id": repair}],
    )


def load_json(path: str | Path) -> dict[str, Any] | None:
    source = Path(path)
    if not source.exists():
        return None
    return json.loads(source.read_text(encoding="utf-8"))
