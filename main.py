import json

from engine.index import InvertedIndex

# csre: CatalogSearchRankingEngine = CatalogSearchRankingEngine()
#
# for p in csre.search("hdmi", 5):
#     print(p)
#
# for p in csre.search_in_category("keyboard", "Electronics", 7):
#     print(p)
#
# suggestEngine = SuggestionEngine(csre._invertedIndex)
# print(suggestEngine.suggest("mase"))
with open("catalog.json", encoding="utf-8") as fichier:
    products = json.load(fichier)

index = InvertedIndex()
result = index.build(products)
print(result)
