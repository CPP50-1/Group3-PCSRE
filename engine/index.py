from engine.tokenize import tokenize


class InvertedIndex:
    def __init__(self):
        self.data = {}
        self.products_by_id = {}

    def build(self, products):
        for product in products:
            product_id = product["id"]
            self.products_by_id[product_id] = product

            texts = [product["name"]] + product.get("tags", [])
            for text in texts:
                words = tokenize(text)
                for word in words:
                    if word not in self.data:
                        self.data[word] = set()
                    self.data[word].add(product_id)

    def lookup(self, word):
        ids = self.data.get(word, set())
        return [self.products_by_id[pid] for pid in ids]

    def get_product(self, product_id):
        return self.products_by_id.get(product_id)