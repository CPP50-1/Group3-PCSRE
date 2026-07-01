# Exercise : Product Catalog Search & Ranking Engine

**Module:** Algorithms & Data Structures   
**Team size:** 3 developers  
**Language:** Python 3.12, standard library only (no `pandas`, no `elasticsearch`, no external search libs)

| Group | Members                     |
|-------|-----------------------------|
| 3     | Nathan - Sergio - Mithirsan |

---

## Context

Odoo and its partners manage product catalogs that can reach tens of thousands of SKUs (Stock keeping Unit). A common real-world need is to let a salesperson or customer type a few words and instantly get the most relevant products back (filtered, ranked, and tolerant of typos).

You are going to build a search and ranking engine for a product catalog from scratch. Every structural choice you make has a direct performance consequence. You will be expected to justify each one.

---

## Dataset

A Python script is provided to generate your dataset: `generate_catalog.py`.  
Run it once before starting:

```bash
python generate_catalog.py          # produces catalog.json (~5 000 products)
```

Each product has the following shape:

```json
{
  "id": "P00042",
  "name": "Wireless Ergonomic Keyboard",
  "category": "Electronics/Computers/Peripherals",
  "tags": ["wireless", "ergonomic", "keyboard", "bluetooth"],
  "price": 89.99,
  "stock": 142,
  "sales_rank": 318
}
```

`category` is a slash-separated path representing a hierarchy (e.g. `Electronics` → `Computers` → `Peripherals`).  
`sales_rank` is a positive integer, the lower the number, the better-selling the product.

---

## What You Must Build

### Part 1 - Inverted index

Build an index at load time that maps every word that appears in a product's `name` or `tags` to the list of product IDs that contain it.

Requirements:
- Tokenise by splitting on spaces and punctuation, lowercasing, stripping short words (≤ 2 chars)
- The index must be built **once** when the engine starts, not rebuilt on every query
- A search for a single term must run in **O(k)** where k is the number of matching product IDs, not O(n) over the full catalog

You must be able to explain: why is a dict of sets (or lists) the right structure here? What would the complexity be with a plain list scan instead?

### Part 2 - Ranked search

Implement a `search(query: str, top_k: int = 10)` function that:

1. Tokenises the query the same way as the index
2. Finds the union of all product IDs matching any query token
3. Scores each candidate product with this formula:

```
score = (matched_tokens / total_query_tokens) * 0.5
      + (stock > 0) * 0.2
      + (1 / log2(sales_rank + 2)) * 0.3
```

4. Returns the `top_k` highest-scoring products

The constraint: **do not sort the full result set**. Use a min-heap of size `top_k` to retrieve the top results in O(m log k) where m is the number of candidates. You must be able to explain why this beats a full sort when k << m.

### Part 3 - Category tree filter

Implement a `search_in_category(query: str, category: str, top_k: int = 10)` function that restricts results to products whose category **starts with** the given path.

Example: filtering on `"Electronics"` must also return products in `"Electronics/Computers"` and `"Electronics/Computers/Peripherals"`.

Requirements:
- Build a tree structure from the category paths at load time
- Use either BFS or DFS to collect all matching category paths, you must justify which one you chose and why
- The category filter must be applied **before** scoring, not after, to avoid scoring products that will be discarded

### Part 4 - "Did you mean?" suggestions

Implement a `suggest(query: str, max_suggestions: int = 3)` function that returns the closest words from the index vocabulary when a query term produces zero results.

Requirements:
- Use edit distance (Levenshtein) to measure similarity between the unknown term and index vocabulary
- Only suggest words with an edit distance ≤ 2
- Return at most `max_suggestions` suggestions, sorted by edit distance ascending
- You must compute and document the time complexity of your suggest function as a function of V (vocabulary size) and L (average word length)

### Part 5 - CLI

Wrap everything in a small command-line interface:

```
$ python search.py "wireless keyboard"
$ python search.py "wireless keyboard" --category "Electronics"
$ python search.py "wireles keyborad"   # should trigger suggestions
$ python search.py "wireless keyboard" --top 5
```

Output format is your choice, keep it readable.

---

## Deliverables

At the end, your repository looks like that :

```
generate_catalog.py       # provided, do not modify
search.py                 # CLI entry point
engine/
    __init__.py
    tokenize.py           # shared tokenizer (Part 0)
    index.py              # inverted index (Part 1)
    ranking.py            # scored search + heap (Part 2)
    categories.py         # category tree (Part 3)
    suggest.py            # edit distance suggestions (Part 4)
tests/
    __init__.py
    test_engine.py        # 24 unit tests, 6 per module
COMPLEXITY.md             # written analysis (see below)
```

### COMPLEXITY.md - required written analysis

This document is as important as the code. For each of the four parts, write:

- The data structure(s) you chose and **why** (what alternatives did you consider?)
- The **build-time complexity** (index construction, tree construction)
- The **query-time complexity** for a typical search
- One concrete example: given a catalog of n products with an average of t tags each, what is the cost of a full search query?

Length: roughly half a page per part. Be precise, "it's fast" is not an acceptable justification.

---

## Constraints

- Standard library only: `heapq`, `collections`, `math`, `re`, `json`, `argparse` are all fair game
- No external search engines, no databases, no pandas
- Python 3.12, use type hints throughout
- All four engine modules must have at least one unit test each (`unittest` or `pytest`)

---

## Evaluation criteria

| Criterion                                                          | Weight |
|--------------------------------------------------------------------|--------|
| Correctness - does it return sensible results?                     | 25%    |
| Structure choices - are they justified and appropriate?            | 25%    |
| Complexity analysis in `COMPLEXITY.md` - is it precise and honest? | 25%    |
| Code quality - readability, type hints, tests                      | 25%    |

During the review session, each team member will be asked to explain one part of the implementation and defend the structure choices made. You should all understand the full codebase, not just the part you wrote.

---

## Suggested team split

| Member      | Ownership                                     |
|-------------|-----------------------------------------------|
| Developer A | Part 1 (inverted index) + Part 5 (CLI)        |
| Developer B | Part 2 (ranked search + heap) + unit tests    |
| Developer C | Part 3 (category tree) + Part 4 (suggestions) |

`COMPLEXITY.md` is written collaboratively, every section must be reviewed by all three.

---

## Dataset generator

Save the following as `generate_catalog.py` and run it once to produce `catalog.json`:

```python
import json
import random
import string

random.seed(42)

CATEGORIES = [
    "Electronics/Computers/Laptops",
    "Electronics/Computers/Peripherals",
    "Electronics/Phones/Smartphones",
    "Electronics/Phones/Accessories",
    "Electronics/Audio/Headphones",
    "Electronics/Audio/Speakers",
    "Office/Furniture/Chairs",
    "Office/Furniture/Desks",
    "Office/Supplies/Paper",
    "Office/Supplies/Pens",
    "Software/Productivity",
    "Software/Security",
    "Networking/Routers",
    "Networking/Switches",
    "Networking/Cables",
]

WORDS = [
    "wireless", "ergonomic", "compact", "portable", "mechanical",
    "bluetooth", "usb", "hdmi", "rechargeable", "adjustable",
    "gaming", "professional", "silent", "backlit", "foldable",
    "keyboard", "mouse", "monitor", "headset", "webcam",
    "chair", "desk", "lamp", "cable", "adapter",
    "router", "switch", "hub", "drive", "printer",
    "laser", "inkjet", "optical", "digital", "smart",
    "pro", "lite", "plus", "max", "ultra",
]

def make_product(i: int) -> dict:
    n_words = random.randint(2, 4)
    name_words = random.sample(WORDS, n_words)
    name = " ".join(w.capitalize() for w in name_words)
    tags = random.sample(WORDS, random.randint(2, 6))
    return {
        "id": f"P{i:05d}",
        "name": name,
        "category": random.choice(CATEGORIES),
        "tags": tags,
        "price": round(random.uniform(5.0, 999.0), 2),
        "stock": random.randint(0, 500),
        "sales_rank": random.randint(1, 5000),
    }

catalog = [make_product(i) for i in range(5000)]
with open("catalog.json", "w") as f:
    json.dump(catalog, f, indent=2)

print(f"Generated {len(catalog)} products -> catalog.json")
```
