import re

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")
MIN_TOKEN_LENGTH = 3


def tokenize(text: str) -> list[str]:
    if not text:
        return []
    raw_tokens = _TOKEN_PATTERN.findall(text)
    lowercase_tokens = [tok.lower() for tok in raw_tokens]
    return [tok for tok in lowercase_tokens if len(tok) >= MIN_TOKEN_LENGTH]