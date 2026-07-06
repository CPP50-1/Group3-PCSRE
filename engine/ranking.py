import heapq
import json
from collections import Counter
from math import log

from engine.index import InvertedIndex
from engine.tokenize import tokenize


class Product:
    def __init__(self, product_id, name, category, tags: list[str], price: float, stock: int, sales_rank: int):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.tags = tags
        self.price = price
        self.stock = stock
        self.sales_rank = sales_rank

    def __str__(self):
        return f"name:{self.name}; category:{self.category}; tag: {self.tags}"

    def __lt__(self, other):
        return self.product_id < other.product_id


def get_all_products():
    with open("../catalog.json", encoding="utf-8") as f:
        return json.load(f)


all_products = get_all_products()


def get_product_by_id(prd_id: str):
    res = next((x for x in all_products if x["id"] == prd_id), None)
    if res:
        return Product(res["id"], res["name"], res["category"], res["tags"], res["price"], res["stock"], res["sales_rank"])

    return None


def search(query: str, top_k: int = 10):
    query_tokens = set(tokenize(query))             # Ensure there is only one token of every sort
    inverted_index = InvertedIndex()                # Ensure there is only one token of every sorta list of product_id
    inverted_index.build(all_products)
    data_values = [inverted_index.data.get(k) for k in query_tokens]

    freq = Counter()                                # Dictionary containing product_id and the hits per token
    for val in data_values:
        freq.update(val)
    selected_products = []                          # Use of a min_heap to store the top_k items. This is a list of paired values (score, Product) of length top_k  # noqa: E116
    heapq.heapify(selected_products)

    for counted_item in freq:
        prod = get_product_by_id(counted_item)
        if prod:
            score = get_score(freq[counted_item], len(query_tokens), prod)
            if len(selected_products) < top_k:
                heapq.heappush(selected_products, [score, prod])  # noqa: E701
            elif score > selected_products[0][0]:
                heapq.heapreplace(selected_products, [score, prod])  # noqa: E701
    return selected_products


def get_score(matched_tokens, total_query_tokens, product: Product) -> float:
    return ((matched_tokens / total_query_tokens) * 0.5 + (product.stock > 0) * 0.2
             + (1 / log(product.sales_rank + 2, 2)) * 0.3)


