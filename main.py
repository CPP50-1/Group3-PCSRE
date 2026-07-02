import json

from engine.index import InvertedIndex

with open('catalog.json', 'r', encoding='utf-8') as fichier:
    products = json.load(fichier)

index = InvertedIndex()
index.build(products)

print(index.lookup("inkjet"))

