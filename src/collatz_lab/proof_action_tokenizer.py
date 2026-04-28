"""Token vocabulary for proof-action states and canonical action JSON."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch


PAD = 0
BOS = 1
EOS = 2
UNK = 3
SPECIAL_TOKENS = {"PAD": PAD, "BOS": BOS, "EOS": EOS, "UNK": UNK}

_TOKEN_RE = re.compile(
    r'"[^"\\]*(?:\\.[^"\\]*)*"'
    r"|</?[A-Z_]+(?:\s+[A-Za-z_][A-Za-z0-9_]*=\"[^\"]*\")?\s*/?>"
    r"|[A-Z][A-Z0-9_:-]+"
    r"|goal_[0-9]+"
    r"|lemma_[A-Za-z0-9_.:-]+"
    r"|[01]{4,}"
    r"|-?\d+"
    r"|[A-Za-z_][A-Za-z0-9_.:-]*"
    r"|[{}\[\]:,=/;()<>]"
    r"|\S"
)


def tokenize(text: str) -> list[str]:
    """Return deterministic lexical tokens, never raw characters."""

    return _TOKEN_RE.findall(text)


def _join_json_tokens(tokens: list[str]) -> str:
    out: list[str] = []
    for token in tokens:
        if token in {",", ":", "}", "]"}:
            out.append(token)
        elif token in {"{", "["}:
            out.append(token)
        else:
            out.append(token)
    return "".join(out)


@dataclass
class ProofActionTokenizer:
    token_to_id: dict[str, int]

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> "ProofActionTokenizer":
        tokens = payload.get("tokens")
        if not isinstance(tokens, list):
            raise ValueError("tokenizer payload requires a tokens list")
        return cls({str(token): index + len(SPECIAL_TOKENS) for index, token in enumerate(tokens)})

    @property
    def id_to_token(self) -> dict[int, str]:
        return {index: token for token, index in self.token_to_id.items()}

    @property
    def vocab_size(self) -> int:
        return len(self.token_to_id) + len(SPECIAL_TOKENS)

    def encode(self, text: str, max_len: int, *, add_bos_eos: bool = True) -> torch.Tensor:
        pieces = tokenize(text)
        ids: list[int] = []
        if add_bos_eos:
            ids.append(BOS)
        budget = max_len - (1 if add_bos_eos else 0)
        if add_bos_eos:
            budget -= 1
        for token in pieces[: max(0, budget)]:
            ids.append(self.token_to_id.get(token, UNK))
        if add_bos_eos:
            ids.append(EOS)
        return torch.tensor(ids, dtype=torch.long)

    def decode(self, ids: list[int] | torch.Tensor, *, skip_special: bool = True) -> str:
        values = ids.tolist() if torch.is_tensor(ids) else list(ids)
        reverse = self.id_to_token
        tokens: list[str] = []
        for value in values:
            token_id = int(value)
            if skip_special and token_id in {PAD, BOS}:
                continue
            if token_id == EOS:
                break
            if token_id == UNK:
                tokens.append("<UNK>")
            elif token_id >= len(SPECIAL_TOKENS):
                tokens.append(reverse.get(token_id, "<UNK>"))
        return _join_json_tokens(tokens)

    def to_json(self) -> dict[str, Any]:
        tokens = [token for token, _ in sorted(self.token_to_id.items(), key=lambda item: item[1])]
        return {"tokens": tokens, "special_tokens": SPECIAL_TOKENS, "tokenizer": "proof_action_v2_regex"}

    def save(self, path: str | Path) -> None:
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(self.to_json(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "ProofActionTokenizer":
        return cls.from_json(json.loads(Path(path).read_text(encoding="utf-8")))


def build_tokenizer(
    rows: list[dict[str, Any]],
    *,
    max_vocab_size: int = 16384,
    min_freq: int = 1,
) -> ProofActionTokenizer:
    counts: Counter[str] = Counter()
    for row in rows:
        counts.update(tokenize(str(row.get("state", ""))))
        counts.update(tokenize(str(row.get("target_action_text", ""))))
    action_tokens = set()
    for name in (
        "SPLIT_RESIDUE",
        "UNROLL_PARITY",
        "APPLY_LEMMA",
        "PROVE_AFFINE_DESCENT",
        "LIFT_MODULUS",
        "DERIVE_PARENT_TRANSITION",
        "CHECK_FINITE_DESCENT",
        "CHECK_DEBT_DECREASE",
        "INTRODUCE_DEBT_FUNCTION",
        "GENERALIZE_FROM_RESIDUES",
        "CLOSE_BY_VERIFIER",
        "ABANDON_BRANCH",
        "PROVE_RESIDUE_COVERAGE",
        "PROVE_RESIDUAL_COVERAGE",
        "PROVE_PARENT_RESIDUAL_COVERAGE",
        "PROVE_GLOBAL_DESCENT_INDUCTION",
        "CLOSE_WELL_FOUNDED_INDUCTION",
        "CERTIFY_NO_ESCAPE_BRANCH",
        "LINK_LOCAL_DESCENT_TO_GLOBAL_THEOREM",
        "LIFT_LOCAL_TO_PARAMETRIC_FAMILY",
        "CLOSE_STRICT_THEOREM_BLOCKER",
        "PROPOSE_S6_LEMMA",
        "VERIFY_S6_LEMMA",
        "COMPOSE_GATE_PROOF",
    ):
        action_tokens.add(f'"{name}"')
        action_tokens.add(name)
    for token in '{}[]:,"type""target""modulus""residue""steps""parity_word"'.replace('"', ' "').split():
        counts[token] += 1000
    for token in action_tokens:
        counts[token] += 1000
    ordered = [
        token
        for token, count in counts.most_common(max_vocab_size)
        if count >= min_freq and token not in {"<PAD>", "<BOS>", "<EOS>", "<UNK>"}
    ]
    return ProofActionTokenizer({token: index + len(SPECIAL_TOKENS) for index, token in enumerate(ordered)})


def pad_1d(sequences: list[torch.Tensor], pad_value: int = PAD) -> torch.Tensor:
    max_len = max((seq.numel() for seq in sequences), default=0)
    if max_len == 0:
        return torch.empty((len(sequences), 0), dtype=torch.long)
    out = torch.full((len(sequences), max_len), pad_value, dtype=sequences[0].dtype)
    for index, seq in enumerate(sequences):
        if seq.numel():
            out[index, : seq.numel()] = seq
    return out


def _load_rows(path: str | Path) -> list[dict[str, Any]]:
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a proof-action tokenizer vocabulary.")
    parser.add_argument("--rows", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-vocab-size", type=int, default=16384)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    tokenizer = build_tokenizer(_load_rows(args.rows), max_vocab_size=args.max_vocab_size)
    tokenizer.save(args.out)
    print(json.dumps({"out": args.out, "vocab_size": tokenizer.vocab_size}, sort_keys=True))


if __name__ == "__main__":
    main()
