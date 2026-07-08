import heapq
from collections import Counter
from math import log2

from engine.category import CategoryTree
from engine.data_manager import JSONProductCatalog, ProductCatalog
from engine.index import InvertedIndex
from engine.tokenize import tokenize
from engine.types import Product


def get_score(matched_tokens: int, total_query_tokens: int, product: Product) -> float:
    """
    Helper function to calculate score for each candidate
    """
    if total_query_tokens == 0:
        raise ZeroDivisionError(
            f"provided total query tokens cannot be {total_query_tokens}",
        )

    return (
        (matched_tokens / total_query_tokens) * 0.5
        + (product.stock > 0) * 0.2
        + (1 / log2(product.sales_rank + 2)) * 0.3
    )


class CatalogSearchRankingEngine:
    """
    Facade class to handle indexing, category tree and catalog data management
    """

    def __init__(self):
        self._catalog: ProductCatalog = JSONProductCatalog("catalog.json")

        self._inverted_index = InvertedIndex()
        self._inverted_index.build(self._catalog.getValues())

        self._category_tree = CategoryTree()
        self._category_tree.build(self._catalog.getValues())

    def search_in_category(
        self,
        query: str,
        category: str,
        top_k: int = 10,
    ) -> list[Product]:
        """ """
        category_filtered_product_ids = self._category_tree.collect_product_ids(
            category
        )

        return self.search(query, top_k, category_filtered_product_ids)

    def search(
        self, query: str, top_k: int = 10, filtered_ids: set[str] | None = None
    ) -> list[Product]:
        query_tokens = set(tokenize(query))
        query_token_len = len(query_tokens)

        # Dictionary containing product_id and the hits per token
        data_values: Counter = Counter()
        for val in [self._inverted_index.get_index().get(key) for key in query_tokens]:
            asSet = set(val)

            if filtered_ids is not None:
                asSet = asSet.intersection(filtered_ids)

            data_values.update(asSet)

        selected_products = []  # Use of a min_heap to store the top_k items.

        for product_id in data_values:
            score = get_score(
                data_values[product_id],
                query_token_len,
                self._catalog[product_id],
            )

            if len(selected_products) < top_k:
                heapq.heappush(selected_products, [score, product_id])
            elif score > selected_products[0][0]:
                heapq.heapreplace(selected_products, [score, product_id])

        selected_products.sort(reverse=True)

        return [self._catalog[index] for _, index in selected_products]
