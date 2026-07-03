from engine.tokenize import tokenize


class InvertedIndex:
    def __init__(self):
        self.data = {}

    def build(self, products):
        """Build inverted index from a list of products."""
        for product in products:
            product_id = product["id"]
            texts = [product["name"]] + product.get("tags", [])
            for text in texts:
                words = tokenize(text)
                for word in words:
                    ids = self.data.setdefault(word, [])
                    if product_id not in ids:
                        ids.append(product_id)
        return self.data

    def get_index(self):
        """Return the inverted index."""
        return self.data

    def getVocabulary(self) -> set[str]:
        return set(self.data.keys())
