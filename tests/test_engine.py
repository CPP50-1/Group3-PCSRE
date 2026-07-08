from engine.ranking import search
from engine.tokenize import tokenize


def test_tokenize():
    assert tokenize("Convert a text into a list of normalized tokens.") == ["convert", "text", "into", "list", "normalized", "tokens"]


def test_search():
    assert search("wireless keyboard mechanic") == []


test_tokenize()
test_search()
