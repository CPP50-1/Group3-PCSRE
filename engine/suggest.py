from __future__ import annotations

import heapq
from typing import Protocol


class VocabularyProvider(Protocol):
    """
    Protocol that provides available words for suggestion matching
    """

    def get_vocabulary(self) -> set[str]:
        raise NotImplementedError


def _levenshtein_distance(a: str, b: str, max_edit: int = 0) -> int:
    """
    Compute de distance between the given 2 strings using Levenshtein Edit Distance. Case insensitive
    """
    trimmed_a, trimmed_b = a, b
    len_a, len_b = len(trimmed_a), len(trimmed_b)
    use_max_edit: bool = max_edit > 0

    # Trim common prefix
    start: int = 0
    while start < len_a and start < len_b and trimmed_a[start] == trimmed_b[start]:
        start += 1

    # Trim common suffix
    endA, endB = len_a - 1, len_b - 1
    while endA >= 0 and endB >= 0 and trimmed_a[endA] == trimmed_b[endB]:
        endA -= 1
        endB -= 1

    trimmed_a = trimmed_a[start : endA + 1]
    trimmed_b = trimmed_b[start : endB + 1]

    len_a, len_b = len(trimmed_a), len(trimmed_b)

    # making row size as short as possible
    if len_b > len_a:
        trimmed_a, trimmed_b = trimmed_b, trimmed_a
        len_a, len_b = len_b, len_a

    # If length difference alone exceeds maxEdit
    if max_edit > 0 and len_a - len_b > max_edit:
        return len_a - len_b

    # Only two rows needed instead of a full (lenA+1) x (lenB+1) matrix
    prev: list[int] = list(range(len_b + 1))
    curr: list[int] = [0] * (len_b + 1)

    # Compute matrix
    for i in range(1, len_a + 1):
        curr[0] = i

        # only keep colums where |i - j| <= maxEdit can stay <= maxEdit
        low = max(1, i - max_edit) if use_max_edit else 1
        high = min(len_b, i + max_edit) if use_max_edit else len_b

        # columns before the band inherit the diagonal cost
        for j in range(1, low):
            curr[j] = prev[j] + 1

        min_edit_in_row = len_b

        for j in range(low, high + 1):
            cost: int = 0 if trimmed_a[i - 1] == trimmed_b[j - 1] else 1

            curr[j] = min(
                prev[j] + 1,  # deletion
                curr[j - 1] + 1,  # insertion
                prev[j - 1] + cost,  # substitution
            )

            if min_edit_in_row > curr[j]:
                min_edit_in_row = curr[j]

        # if the min of the row is already higher, we can stop here. the number will not go down anywhere
        # later
        if use_max_edit and min_edit_in_row > max_edit:
            return min_edit_in_row

        prev, curr = curr, prev

    return prev[len_b]


def _hamming_distance(a: str, b: str, maxEdit: int = 0) -> int:
    """
    Compute de distance between the given 2 strings using Hamming Distance. Case insensitive
    string to compare should be the same length. it uses only substitution to compute distances
    """
    len_a, len_b = len(a), len(b)
    use_max_edit: bool = maxEdit > 0

    if len_a != len_b:
        raise ValueError(f"{a} and {b} does not have the same length")

    distance: int = 0

    for index in range(len_a):
        if a[index] != b[index]:
            distance += 1
            if use_max_edit and distance > maxEdit:
                return distance

    return distance


class SuggestionEngine:
    """
    Suggestion engine providing method to find a matching word
    """

    def __init__(
        self,
        vocabulary_provider: VocabularyProvider,
        max_edit_distance=2,
    ) -> None:
        self._vocabulary_provider = vocabulary_provider
        self._max_edit_distance = max_edit_distance

    def suggest(
        self,
        query: str,
        max_suggestions: int = 3,
    ) -> list[str]:
        """
        Return the closest matching words in vocabulary
        """
        query_len = len(query)

        if max_suggestions <= 0 or query_len <= 0:
            return []

        query_lower = query.lower()

        vocabulary = self._vocabulary_provider.get_vocabulary()

        heap: list[tuple[int, str]] = []

        for word in vocabulary:
            # Because we discard every suggestion if the distance is higher than what we set, we can skip words that
            # would lead to an higher difference in length compared to the input. Levenshtein Edit Distance is costly
            # in process so we have an opportunity to save computation time here.
            word_len = len(word)
            if abs(word_len - query_len) > self._max_edit_distance:
                continue

            word_lower = word.lower()

            # If word and input are the same length, we can use Hamming Distance which is lighter than levenshtein.
            # We don't need deletion and insertion if the strings are the same size
            dist: int = (
                _hamming_distance(
                    query_lower,
                    word_lower,
                    self._max_edit_distance,
                )
                if word_len == query_len
                else _levenshtein_distance(
                    query_lower,
                    word_lower,
                    self._max_edit_distance,
                )
            )

            if dist > self._max_edit_distance:
                continue

            # heapq is a min-heap, so we store (-dist, word) to simulate a max-heap.
            # This way heap[0] is the worst candidate (largest dist), letting us
            # efficiently evict it via heapreplace when a better word is found.
            if len(heap) == max_suggestions:
                if -heap[0][0] > dist:
                    heapq.heapreplace(heap, (-dist, word))
            else:
                heapq.heappush(heap, (-dist, word))

        return [word for _, word in sorted(heap, key=lambda x: (-x[0], x[1]))]
