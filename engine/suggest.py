def levenshteinEditDistance(a: str, b: str) -> int:
    """
    Compute de distance between the given 2 strings using Levenshtein Edit Distance
    """
    lenA, lenB = len(a), len(b)
    distanceMatrix: list[list[int]] = [[0] * (lenB + 1) for _ in range(lenA + 1)]

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
