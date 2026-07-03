from __future__ import annotations

from abc import ABC


class Product:
    """
    Class repesenting a Product
    """

    def __init__(
        self,
        id,
        name,
        category,
        tags: list[str],
        price: float,
        stock: int,
        sales_rank: int,
    ):
        self._id = id
        self._name = name
        self._category = category
        self._tags = tags
        self._price = price
        self._stock = stock
        self._sales_rank = sales_rank

    def __eq__(self, other: Product) -> bool:
        if not isinstance(other, Product):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __str__(self) -> str:
        return f"{self._id}: {self._name} {self._price} [{self._stock}] ({self._category}) [{self._tags}] ({self._sales_rank})"


class ProductRepository(ABC):
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
