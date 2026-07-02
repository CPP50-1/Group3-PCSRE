from collections import Counter
from math import log
from unittest import result

from engine.index import InvertedIndex
from engine.tokenize import tokenize
import heapq
import json

from generate_catalog import catalog


class Product:
    def __init__(self, product_id, name, category, tags:list[str], price:float, stock:int, sales_rank:int):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.tags = tags
        self.price = price
        self.stock = stock
        self.sales_rank = sales_rank


def get_all_products() -> list[Product]:
    with open("./catalog.json", "r") as f:
        products = json.load(f)
    return products

all_products = get_all_products()

def search(query: str, top_k: int = 10):
    query_tokens = set(tokenize(query))             #Ensure there is only one token of every sort
    inverted_index = InvertedIndex().data           #this is a dict containing a key (token) and a list of product_id

    freq = Counter(inverted_index.values())         #List of tuples
    selected_products = []                          #Will store the top_k items
    heapq.heapify(selected_products)

    for counted_item in freq:
        prod = get_product_by_id(counted_item[0])
        score = get_score(counted_item[1], query_tokens, prod)
        if len(selected_products) < top_k: heapq.heappush(selected_products, [score, prod])     #!!!! find how to compare on push
        elif score > selected_products[0][0]: heapq.heapreplace(selected_products, [score, prod])


    return selected_products


def get_score(matched_tokens, total_query_tokens, product:Product) -> float:
    score = (matched_tokens / total_query_tokens) * 0.5 + (product.stock > 0) * 0.2 + (1 / log(product.sales_rank + 2,2)) * 0.3
    return score


def get_product_by_id(product_id:str) -> Product:
    res =  next((x for x in all_products if x.product_id == product_id), None)
    p = Product(product_id, "","",[],0.0,0,0)
    if res:
        p = Product(product_id, res.name, res.category, res.tags, res.price, res.stock, res.sales_rank)

    return p



