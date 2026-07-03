import json

from engine.index import InvertedIndex
from engine.suggest import SuggestionEngine

with open("catalog.json", encoding="utf-8") as fichier:
    products = json.load(fichier)

index = InvertedIndex()
result = index.build(products)
print(result)

suggestEngine = SuggestionEngine(index)
print(suggestEngine.suggest("mase"))
