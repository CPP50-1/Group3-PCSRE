from __future__ import annotations

import json
from abc import ABC

from engine.types import Product


class ProductCatalog(ABC):
    """
    Data handler repository to manage product datas
    """

    def __init__(self) -> None:
        self.__products: dict[str, Product] = {}

    def __len__(self) -> int:
        return len(self.__products)

    def __getitem__(self, key: str) -> Product:
        if not isinstance(key, str):
            raise TypeError(f"Given key {key} is not a string")

        p = self.__products.get(key)

        if p is None:
            raise ValueError(f"Not product found matching key {key}")

        return p

    def __setitem__(self, key: str, value: Product) -> None:
        if not isinstance(key, str):
            raise TypeError(f"Given key {key} is not a string")
        if not isinstance(value, Product):
            raise TypeError(f"Given product {value} is not an instance of Product")
        if key in self.__products:
            raise KeyError(f"Product {key} already exist")

        self.__products[key] = value

    def clear(self) -> None:
        """Helper method to allow subclasses or users to clear the repo"""
        self.__products.clear()

    def get_values(self) -> list[Product]:
        return self.__products.values()


class JSONProductCatalog(ProductCatalog):
    """
    Concrete repo managing product data loaded from a json file
    """

    def __init__(self, path_to_file: str) -> None:
        super().__init__()

        with open(path_to_file, encoding="utf-8") as fichier:
            products = json.load(fichier)

        for product in products:
            product_id = product.get("id")

            self[product_id] = Product(
                product_id,
                product["name"],
                product["category"],
                product["tags"],
                product["price"],
                product["stock"],
                product["sales_rank"],
            )
