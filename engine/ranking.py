import heapq
from collections import Counter
from math import log2

from engine.category import CategoryTree
from engine.data_manager import JSONProductCatalog, ProductCatalog
from engine.index import InvertedIndex
from engine.tokenize import tokenize
from engine.types import Product


def getScore(matched_tokens, total_query_tokens, product: Product) -> float:
    """
    Helper function to calculate score for each candidate
    """
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

        self._invertedIndex = InvertedIndex()
        self._invertedIndex.build(self._catalog.getValues())

        self._categoryTree = CategoryTree()
        self._categoryTree.build(self._catalog.getValues())

    def search_in_category(
        self,
        query: str,
        category: str,
        top_k: int = 10,
    ) -> list[Product]:
        """ """
        categoryFilteredProductIds = self._categoryTree.collect_product_ids(category)

        return self.search(query, top_k, categoryFilteredProductIds)

    def search(self, query: str, top_k: int = 10, filtered_ids: set[str] | None = None):
        queryTokens = set(tokenize(query))
        queryTokenLen = len(queryTokens)

        # Dictionary containing product_id and the hits per token
        data_values: Counter = Counter()
        for val in [self._invertedIndex.get_index().get(key) for key in queryTokens]:
            asSet = set(val)

            if filtered_ids is not None:
                asSet = asSet.intersection(filtered_ids)

            data_values.update(asSet)

        selected_products = []  # Use of a min_heap to store the top_k items.

        heapq.heapify(selected_products)

        for productId in data_values:
            score = getScore(
                data_values[productId],
                queryTokenLen,
                self._catalog[productId],
            )

            if len(selected_products) < top_k:
                heapq.heappush(selected_products, [score, productId])
            elif score > selected_products[0][0]:
                heapq.heapreplace(selected_products, [score, productId])

        selected_products.sort(reverse=True)

        return [self._catalog[index] for _, index in selected_products]
