from __future__ import annotations

from typing import Protocol


class VocabularyProvider(Protocol):
    """
    Protocol that provides available words for suggestion matching
    """

    def getVocabulary(self) -> set[str]:
        raise NotImplementedError


def _levenshteinEditDistance(a: str, b: str, maxEdit: int = 0) -> int:
    """
    Compute de distance between the given 2 strings using Levenshtein Edit Distance. Case insensitive
    """
    lenA, lenB = len(a), len(b)
    useMaxEdit: bool = maxEdit > 0

    # making row size as short as possible
    if lenB > lenA:
        a, b = b, a
        lenA, lenB = lenB, lenA

    # Only two rows needed instead of a full (lenA+1) x (lenB+1) matrix
    prev: list[int] = list(range(lenB + 1))
    curr: list[int] = [0] * (lenB + 1)

    # Compute matrix
    for i in range(1, lenA + 1):
        curr[0] = i
        minEditInRow = lenB

        for j in range(1, lenB + 1):
            cost: int = 0 if a[i - 1] == b[j - 1] else 1

            curr[j] = min(
                prev[j] + 1,  # deletion
                curr[j - 1] + 1,  # insertion
                prev[j - 1] + cost,  # substitution
            )

            if minEditInRow > curr[j]:
                minEditInRow = curr[j]

        # if the min of the row is already higher, we can stop here. the number will not go down anywhere
        # later
        if useMaxEdit and minEditInRow > maxEdit:
            return minEditInRow

        prev, curr = curr, prev

    return prev[lenB]


def _hammingDistance(a: str, b: str, maxEdit: int = 0) -> int:
    """
    Compute de distance between the given 2 strings using Hamming Distance. Case insensitive
    string to compare should be the same length. it uses only substitution to compute distances
    """
    lenA, lenB = len(a), len(b)
    useMaxEdit: bool = maxEdit > 0

    if lenA != lenB:
        raise ValueError(f"{a} and {b} does not have the same lenght")

    distance: int = 0

    for index in range(lenA):
        if a[index] != b[index]:
            distance += 1
            if useMaxEdit and distance > maxEdit:
                return distance

    return distance


class SuggestionEngine:
    """
    Suggestion engine providing method to find a matching word
    """

    def __init__(
        self,
        vocabularyProvider: VocabularyProvider,
        discardDistance=2,
    ) -> None:
        self._vocabularyProvider = vocabularyProvider
        self._discardDistance = discardDistance

    def suggest(
        self,
        input: str,
        maxSuggestions: int = 3,
    ) -> list[str]:
        """
        Return the closest matching words in vocabulary
        """
        input_len = len(input)

        if maxSuggestions <= 0 or input_len <= 0:
            return []

        vocabulary = self._vocabularyProvider.getVocabulary()
        suggestion: list[tuple[int, str]] = []

        for word in vocabulary:
            # Because we discard every suggestion if the distance is higher than what we set, we can skip words that
            # would lead to an higher difference in length compared to the input. Levenshtein Edit Distance is costly
            # in process so we have an opportunity to save computation time here.
            word_len = len(word)
            if abs(word_len - input_len) > self._discardDistance:
                continue

            # If word and input are the same length, we can use Hamming Distance which is lighter than levenshtein.
            # We don't need deletion and insertion if the strings are the same size
            dist: int = (
                _hammingDistance(input.lower(), word.lower(), self._discardDistance)
                if word_len == input_len
                else _levenshteinEditDistance(
                    input.lower(), word.lower(), self._discardDistance
                )
            )

            if dist <= self._discardDistance:
                suggestion.append((dist, word))

        suggestion.sort(key=lambda x: (x[0], x[1]))

        result: list[str] = []

        for _, word in suggestion:
            result.append(word)

            if len(result) == maxSuggestions:
                break

        return result
