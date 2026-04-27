from collatz_lab.encode import SUPPORTED_BASES, decode_tokens, encode_int, encode_signed_int, neg_token_for_base, digits_to_int, int_to_digits, vocab_size_for_base


def test_round_trip_across_bases() -> None:
    values = [0, 1, 2, 7, 31, 255, 1024, 123456789]
    for base in SUPPORTED_BASES:
        for value in values:
            digits = int_to_digits(value, base=base, lsb_first=True)
            assert digits_to_int(digits, base=base, lsb_first=True) == value
            digits = int_to_digits(value, base=base, lsb_first=False)
            assert digits_to_int(digits, base=base, lsb_first=False) == value


def test_signed_round_trip_and_vocab() -> None:
    base = 24
    assert vocab_size_for_base(base) == 27
    assert vocab_size_for_base(base, signed=True) == 28
    assert encode_int(31, base=base) == encode_signed_int(31, base=base)
    negative = encode_signed_int(-31, base=base, lsb_first=True)
    assert neg_token_for_base(base) in negative
    assert decode_tokens(negative, base=base, lsb_first=True) == -31
