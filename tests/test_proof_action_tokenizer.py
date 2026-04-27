from collatz_lab.proof_action_tokenizer import BOS, EOS, ProofActionTokenizer, build_tokenizer, tokenize


def test_tokenizer_uses_structured_tokens_not_characters() -> None:
    text = '{"type":"UNROLL_PARITY","target":"goal_0","steps":4,"parity_word":"1010"}'
    tokens = tokenize(text)

    assert '"UNROLL_PARITY"' in tokens
    assert '"1010"' in tokens
    assert "UNROLL_PARITY" not in list("UNROLL_PARITY")


def test_tokenizer_round_trips_canonical_action_json() -> None:
    rows = [
        {
            "state": "<GATE>S2</GATE>",
            "target_action_text": '{"type":"UNROLL_PARITY","target":"goal_0","steps":4,"parity_word":"1010"}',
        }
    ]
    tokenizer = build_tokenizer(rows)
    ids = tokenizer.encode(rows[0]["target_action_text"], max_len=32)
    decoded = tokenizer.decode(ids)

    assert ids[0].item() == BOS
    assert ids[-1].item() == EOS
    assert decoded == rows[0]["target_action_text"]


def test_tokenizer_json_payload_loads() -> None:
    tokenizer = build_tokenizer([{"state": "x", "target_action_text": '{"type":"ABANDON_BRANCH","target":"goal_0","reason":"x"}'}])
    loaded = ProofActionTokenizer.from_json(tokenizer.to_json())

    assert loaded.vocab_size == tokenizer.vocab_size
