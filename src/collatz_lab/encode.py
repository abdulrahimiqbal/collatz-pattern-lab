"""Integer digit encoders used by the sequence models."""

from __future__ import annotations

from collections.abc import Iterable

PAD = 0
BOS = 1
EOS = 2
DIGIT_OFFSET = 3
SUPPORTED_BASES = {2, 8, 10, 16, 24, 32}


def validate_base(base: int) -> None:
    if base not in SUPPORTED_BASES:
        supported = ", ".join(str(b) for b in sorted(SUPPORTED_BASES))
        raise ValueError(f"Unsupported base {base}; supported bases: {supported}")


def int_to_digits(
    n: int,
    base: int,
    max_len: int | None = None,
    lsb_first: bool = True,
) -> list[int]:
    """Convert a non-negative integer to raw base-``base`` digits.

    The returned digits are not special-token shifted. Use ``encode_int`` for
    model-ready token ids.
    """

    validate_base(base)
    if n < 0:
        raise ValueError("Only non-negative integers can be encoded")
    if n == 0:
        digits = [0]
    else:
        digits: list[int] = []
        current = n
        while current:
            current, digit = divmod(current, base)
            digits.append(digit)
        if not lsb_first:
            digits.reverse()
    if max_len is not None:
        if len(digits) > max_len:
            raise ValueError(f"{n} requires {len(digits)} digits, max_len={max_len}")
        digits = pad_digits(digits, max_len=max_len, pad_token=0)
    return digits


def digits_to_int(digits: list[int], base: int, lsb_first: bool = True) -> int:
    """Convert raw base-``base`` digits back to an integer."""

    validate_base(base)
    ordered = digits if not lsb_first else list(reversed(digits))
    value = 0
    for digit in ordered:
        if digit < 0 or digit >= base:
            raise ValueError(f"Digit {digit} is outside base {base}")
        value = value * base + digit
    return value


def pad_digits(digits: Iterable[int], max_len: int, pad_token: int) -> list[int]:
    """Pad a digit or token sequence on the right."""

    values = list(digits)
    if len(values) > max_len:
        raise ValueError(f"Cannot pad length {len(values)} to shorter max_len={max_len}")
    return values + [pad_token] * (max_len - len(values))


def digit_to_token(digit: int, base: int) -> int:
    validate_base(base)
    if digit < 0 or digit >= base:
        raise ValueError(f"Digit {digit} is outside base {base}")
    return digit + DIGIT_OFFSET


def token_to_digit(token: int, base: int) -> int:
    validate_base(base)
    digit = token - DIGIT_OFFSET
    if digit < 0 or digit >= base:
        raise ValueError(f"Token {token} is not a digit token for base {base}")
    return digit


def neg_token_for_base(base: int) -> int:
    """Return the optional sign token for signed encodings in ``base``."""

    validate_base(base)
    return DIGIT_OFFSET + base


def encode_digits(
    digits: Iterable[int],
    base: int,
    add_bos: bool = True,
    add_eos: bool = True,
) -> list[int]:
    tokens = [digit_to_token(digit, base) for digit in digits]
    if add_bos:
        tokens.insert(0, BOS)
    if add_eos:
        tokens.append(EOS)
    return tokens


def decode_tokens(tokens: Iterable[int], base: int, lsb_first: bool = True) -> int:
    """Decode a token sequence that may contain BOS/EOS/PAD."""

    raw_digits: list[int] = []
    sign = 1
    neg_token = neg_token_for_base(base)
    for token in tokens:
        token = int(token)
        if token in {PAD, BOS, EOS}:
            continue
        if token == neg_token:
            sign = -1
            continue
        raw_digits.append(token_to_digit(token, base))
    return sign * digits_to_int(raw_digits, base=base, lsb_first=lsb_first)


def encode_int(
    n: int,
    base: int,
    max_len: int | None = None,
    lsb_first: bool = True,
    add_bos: bool = True,
    add_eos: bool = True,
) -> list[int]:
    digits = int_to_digits(n, base=base, max_len=max_len, lsb_first=lsb_first)
    return encode_digits(digits, base=base, add_bos=add_bos, add_eos=add_eos)


def encode_signed_int(
    n: int,
    base: int,
    max_len: int | None = None,
    lsb_first: bool = True,
    add_bos: bool = True,
    add_eos: bool = True,
) -> list[int]:
    """Encode a signed integer with an explicit negative sign token."""

    digits = int_to_digits(abs(n), base=base, max_len=max_len, lsb_first=lsb_first)
    tokens = [digit_to_token(digit, base) for digit in digits]
    if n < 0:
        tokens.insert(0, neg_token_for_base(base))
    if add_bos:
        tokens.insert(0, BOS)
    if add_eos:
        tokens.append(EOS)
    return tokens


def vocab_size_for_base(base: int, signed: bool = False) -> int:
    validate_base(base)
    return DIGIT_OFFSET + base + (1 if signed else 0)
