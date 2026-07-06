from engine.ranking import CatalogSearchRankingEngine
from engine.suggest import SuggestionEngine

csre: CatalogSearchRankingEngine = CatalogSearchRankingEngine()

for p in csre.search_in_category("keyboard", "Electronics", 10):
    print(p)

suggestEngine = SuggestionEngine(csre._invertedIndex)
print(suggestEngine.suggest("mase"))
