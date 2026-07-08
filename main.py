from engine.ranking import CatalogSearchRankingEngine

engine = CatalogSearchRankingEngine()
index = engine._invertedIndex  # noqa: E113
products = engine._catalog

print(index.get_index())
