from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.types import Product


class CategoryNode:
    """
    Represent an unique category in the tree
    """

    def __init__(
        self,
        name: str,
        children: dict[str, CategoryNode] | None = None,
        product_ids: set[str] | None = None,
    ) -> None:
        self.__name = name

        if children is not None:
            self.children = children
        else:
            self.children = dict()

        if product_ids is not None:
            self.product_ids = product_ids
        else:
            self.product_ids = set()

    def __eq__(self, other: CategoryNode) -> bool:
        if not isinstance(other, CategoryNode):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def children(self) -> dict[str, CategoryNode]:
        return self.__children

    @children.setter
    def children(self, children: dict[str, CategoryNode]) -> None:
        self.__children = children

    def add_child(self, node: CategoryNode) -> None:
        """
        Add given child node as to the children node

        Property:
            node: CategoryNode child category node to be added
        """
        self.children[node.name] = node

    @property
    def product_ids(self) -> set[str]:
        return self.__product_ids

    @product_ids.setter
    def product_ids(self, product_ids: set[str]) -> None:
        self.__product_ids = product_ids

    def add_product_id(self, id: str) -> None:
        """
        Add specified product id into product id set
        """
        self.product_ids.add(id)


class CategoryTree:
    """
    Manage the construction and navigation in the category tree
    """

    def __init__(self) -> None:
        self._root = CategoryNode("root")

    def build(self, products: list[Product]) -> None:
        """
        Build the tree from the catalog
        """
        for product in products:
            categories: list[str] = product.category.split("/")

            current_node: CategoryNode = self._root

            for category in categories:
                # skip empty category if any
                if not category.strip():
                    continue

                node: CategoryNode = current_node.children.get(category)
                if node is None:
                    node = CategoryNode(category)
                    current_node.add_child(node)
                current_node = node

            current_node.add_product_id(product.id)

    def _find_node(self, category_path: str) -> CategoryNode | None:
        """
        Find a node in the tree from the path
        """
        current_node = self._root

        for category in category_path.split("/"):
            node: CategoryNode = current_node.children.get(category)
            if node is None:
                return None
            current_node = node

        return current_node

    def collect_product_ids(self, category_path: str) -> set[str]:
        """
        Collect all product from the given category path (ex: "Electronics/Computers/Peripherals") and its sub-categories
        """
        node = self._find_node(category_path)

        if node is None:
            return set()

        products_ids: set[str] = set()

        node_stack: list[CategoryNode] = [node]

        while node_stack:
            current_node = node_stack.pop()

            products_ids.update(current_node.product_ids)

            for child_node in current_node.children.values():
                node_stack.append(child_node)

        return products_ids
