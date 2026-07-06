import argparse

from engine.ranking import CatalogSearchRankingEngine
from engine.suggest import SuggestionEngine
from engine.tokenize import tokenize


def main():
    parser = argparse.ArgumentParser(description="Product search")
    parser.add_argument("query", type=str, help="Search terms")
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Filter by category",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of results to return",
    )
    args = parser.parse_args()

    # Load and build all what we need
    print("Loading catalog...", end=" ")
    engine = CatalogSearchRankingEngine()
    index = engine._invertedIndex
    products = engine._catalog

    suggestion_engine = SuggestionEngine(vocabularyProvider=index)
    print(f"{len(products)} products indexed. \n")

    print(f'Results for: "{args.query}"')
    print("-" * 40)

    # Tokenise the query the same way as the index
    query_tokens = tokenize(args.query)

    # For each query token, check whether it produces any matches.
    # If a token matches nothing, collect suggestions for that word.
    found_issues = False
    suggestions_found = []  # list of (token, suggestions)
    no_suggestions_tokens = []  # tokens with zero matches AND zero suggestions

    for token in query_tokens:
        matches = index.get_index().get(token, [])
        if not matches:
            found_issues = True
            suggestions = suggestion_engine.suggest(token, max_suggestions=3)
            if suggestions:
                suggestions_found.append((token, suggestions))
            else:
                no_suggestions_tokens.append(token)

    if found_issues:
        for token in no_suggestions_tokens:
            print(f"No results for '{token}'")
        if len(suggestions_found) > 0:
            print("\nDid you mean?")
            for token, suggestions in suggestions_found:
                for word in suggestions:
                    print(f"    {token} -> {word}")
        return

    formatted_query = " ".join(query_tokens)
    if args.category:
        results = engine.search_in_category(formatted_query, args.category, args.top)
    else:
        results = engine.search(formatted_query, args.top)
    for product in results:
        print(product)


if __name__ == "__main__":
    main()
