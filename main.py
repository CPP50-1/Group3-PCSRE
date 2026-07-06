from engine.ranking import CatalogSearchRankingEngine
from engine.suggest import SuggestionEngine

csre: CatalogSearchRankingEngine = CatalogSearchRankingEngine()

for p in csre.search("hdmi", 5):
    print(p)

for p in csre.search_in_category("keyboard", "Electronics", 7):
    print(p)

suggestEngine = SuggestionEngine(csre._invertedIndex)
print(suggestEngine.suggest("mase"))
