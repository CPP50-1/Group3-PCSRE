from engine.tokenize import tokenize
from engine.types import Product


class InvertedIndex:
    def __init__(self):
        self.__data = {}

    def build(self, products: list[Product]):
        """Build inverted index from a list of products."""
        for product in products:
            texts = [product.name] + list(product.tags)
            for text in texts:
                words = tokenize(text)
                for word in words:
                    ids = self.__data.setdefault(word, set())
                    if product.id not in ids:
                        ids.add(product.id)
        return self.__data

    def get_index(self):
        """Return the inverted index."""
        return self.__data

    def getVocabulary(self) -> set[str]:
        return set(self.__data.keys())
