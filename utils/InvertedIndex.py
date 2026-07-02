from collections import defaultdict

from utils.tokenizer import tokenize

class InvertedIndex:
    def __init__(self):
        self.data = defaultdict(set)

    def build(self, products):
        for product in products:
            product_id = product["id"]
            texts = [product["name"]] + product.get("tags", [])
            for text in texts:
                words = tokenize(text)
                for word in words:
                    if word not in self.data:
                        self.data[word] = set()
                    self.data[word].add(product_id)

    def lookup(self, word):
        if word in self.data:
            return self.data[word]
        return set()