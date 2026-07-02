import json

from engine.index import InvertedIndex

with open("catalog.json", encoding="utf-8") as fichier:
    products = json.load(fichier)

index = InvertedIndex()
result = index.build(products)
print(result)
