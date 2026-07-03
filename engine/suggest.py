from __future__ import annotations

from typing import Protocol


class VocabularyProvider(Protocol):
    """
    Protocol taht provides available words for suggestion matching
    """

    def getVocabulary(self) -> set[str]:
        raise NotImplementedError


def _levenshteinEditDistance(a: str, b: str) -> int:
    """
    Compute de distance between the given 2 strings using Levenshtein Edit Distance. Case insensitive
    """
    lenA, lenB = len(a), len(b)
    distanceMatrix: list[list[int]] = [[0] * (lenB + 1) for _ in range(lenA + 1)]

    a = a.lower()
    b = b.lower()

    # Fill matric with base cases
    for index in range(1, lenA + 1):
        distanceMatrix[index][0] = index

    for index in range(1, lenB + 1):
        distanceMatrix[0][index] = index

    # Compute matrix
    for i in range(1, lenA + 1):
        for j in range(1, lenB + 1):
            cost: int = 0 if a[i - 1] == b[j - 1] else 1

            distanceMatrix[i][j] = min(
                distanceMatrix[i - 1][j] + 1,  # deletion
                distanceMatrix[i][j - 1] + 1,  # insertion
                distanceMatrix[i - 1][j - 1] + cost,  # substitution
            )

    return distanceMatrix[lenA][lenB]


def _hammingDistance(a: str, b: str, earlyOut: int = 0) -> int:
    """
    Compute de distance between the given 2 strings using Hamming Distance. Case insensitive
    string to compare should be the same lenght. it uses only substitution to compute distances
    """
    lenA, lenB = len(a), len(b)

    useEalyOut: bool = earlyOut > 0

    if lenA != lenB:
        raise ValueError(f"{a} and {b} does not have the same lenght")

    a = a.lower()
    b = b.lower()

    distance: int = 0

    for index in range(lenA):
        if a[index] != b[index]:
            distance += 1
            if useEalyOut and distance > earlyOut:
                return distance

    return distance


class SuggestionEngine:
    """
    Suggestion engine providing method to find a matching word
    """

    def __init__(
        self,
        vocabularyProvider: VocabularyProvider,
        discrdDistance=2,
    ) -> None:
        self._vocabularyProvider = vocabularyProvider
        self._discardDistance = discrdDistance

    def suggest(
        self,
        input: str,
        max_suggestions: int = 3,
    ) -> list[str]:
        """
        Return the closest matching words in vocabulary
        """

        vocabulary = self._vocabularyProvider.getVocabulary()
        suggestion: list[tuple[int, str]] = []
        input_len = len(input)

        for word in vocabulary:
            # because we discrd every suggestion if the disance is higher than 2, we can skip words that would lead to
            # an higher difference in lenght compared to the input. Levenshtein Edit Distance is costly in process so
            # we have an opportunity to save computation time here.
            word_len = len(word)
            if abs(word_len - input_len) > self._discardDistance:
                continue

            dist: int = (
                _hammingDistance(input, word, self._discardDistance)
                if word_len == input_len
                else _levenshteinEditDistance(input, word)
            )

            if dist <= self._discardDistance and (dist, word) not in suggestion:
                suggestion.append((dist, word))

        suggestion.sort(key=lambda x: (x[0], x[1]))

        result: list[str] = []

        for _, word in suggestion:
            if word in result:
                continue

            result.append(word)

            if len(result) == max_suggestions:
                break

        return result
