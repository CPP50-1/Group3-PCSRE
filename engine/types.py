from __future__ import annotations


class Product:
    """
    Class repesenting a Product
    """

    def __init__(
        self,
        id,
        name,
        category,
        tags: set[str],
        price: float,
        stock: int,
        sales_rank: int,
    ):
        self.id = id
        self.name = name
        self.category = category
        self.tags = tags
        self.price = price
        self.stock = stock
        self.sales_rank = sales_rank

    def __eq__(self, other: Product) -> bool:
        if not isinstance(other, Product):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __str__(self):
        return (
            f"[{self.id}] {self.name}\n"
            f"{self.category}\n"
            f"\u20ac{self.price:.2f}  |  {self.stock} in stock  |  Rank #{self.sales_rank}"
            f" \n"
        )

    def __lt__(self, other):
        return self.product_id < other.product_id

    @property
    def id(self) -> str:
        return self.__id

    @id.setter
    def id(self, id: str) -> None:
        self.__id = id

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        self.__name = name

    @property
    def category(self) -> str:
        return self.__category

    @category.setter
    def category(self, category: str) -> None:
        self.__category = category

    @property
    def tags(self) -> set[str]:
        return self.__tags

    @tags.setter
    def tags(self, tags: set[str]) -> None:
        self.__tags = tags

    @property
    def price(self) -> float:
        return self.__price

    @price.setter
    def price(self, price: float) -> None:
        self.__price = price

    @property
    def stock(self) -> int:
        return self.__stock

    @stock.setter
    def stock(self, stock: int) -> None:
        self.__stock = stock

    @property
    def sales_rank(self) -> int:
        return self.__sales_rank

    @sales_rank.setter
    def sales_rank(self, sales_rank: int) -> None:
        self.__sales_rank = sales_rank
