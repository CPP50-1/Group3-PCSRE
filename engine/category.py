from __future__ import annotations


class CategoryNode:
    """
    Represent an unique category in the tree
    """

    def __init__(
        self,
        name: str,
        children: dict[str, CategoryNode] | None = None,
        product_ids: set[str] | None = None,
    ):
        self.name = name

        if children is not None:
            self.children = children
        else:
            self.children = dict()

        if product_ids is not None:
            self.product_ids = product_ids
        else:
            self.product_ids = set()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def children(self) -> dict[str, CategoryNode]:
        return self._children

    @children.setter
    def children(self, children: dict[str, CategoryNode]) -> None:
        self._children = children

    def addChild(self, node: CategoryNode) -> None:
        """
        Add given child node as to the children node

        Propterty:
            node: CategoryNode child category node to be added
        """
        self.children[node.name] = node

    @property
    def product_ids(self) -> set[str]:
        return self._product_ids

    @product_ids.setter
    def product_ids(self, product_ids: set[str]) -> None:
        self._product_ids = product_ids

    def addProductId(self, id: str) -> None:
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

    def build(self, products: list[dict]) -> None:
        """
        Build the tree from the catalog
        """
        for product in products:
            product_id: str = product.get("id")
            if product_id is None:
                raise ValueError(f"product: {product} doesn't have an id")

            path: str = product.get("category")
            if path is None:
                raise ValueError(f"product: {product} doesn't have a category")

            categories: list[str] = path.split("/")

            current_node: CategoryNode = self._root

            for category in categories:
                if category not in current_node.children:
                    current_node.addChild(CategoryNode(category))

                current_node = current_node.children[category]

            current_node.addProductId(product_id)

    def _find_node(self, category_path: str) -> CategoryNode | None:
        """
        Find a node in the tree from the path
        """
        current_node = self._root

        for category in category_path.split("/"):
            if category not in current_node.children:
                return None

            current_node = current_node.children[category]

        return current_node

    def collect_product_ids(self, category_path: str) -> set[str]:
        """
        Collect all product from the given category path (ex: "Electronics/Computers/Peripherals") and its sub-caregories
        """
        node = self._find_node(category_path)

        if node is None:
            return set()

        prodcuts_id: set[str] = set()

        visited: set[CategoryNode] = set()

        node_stack: list[CategoryNode] = [node]

        while node_stack:
            current_node = node_stack.pop()

            if current_node in visited:
                continue

            prodcuts_id.update(current_node.product_ids)

            visited.add(current_node)

            for child_node in current_node.children.values():
                node_stack.append(child_node)

        return prodcuts_id


class CategorySearch:
    """ """

    def __init__(self, category_tree: CategoryTree):
        self._category_tree = category_tree

    def search_in_category(
        self,
        query: str,
        category_path: str,
        top_k: int = 10,
    ) -> list[str]:
        """
        Restrict result to product whose category starts with the given path.
        """
        raise NotImplementedError

        # TODO: implementaton of he querry
        productIds = self._category_tree.collect_product_ids(category_path)
