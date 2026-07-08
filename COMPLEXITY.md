### Part 1 : Inverted Index

We use a **dict of sets**: `self.data: dict[str, set[str]]`, mapping each
token to the set of product IDs whose `name` or `tags` contain that token.
This matches the assignment's own description of the index: a mapping from
word to the list (here: set) of product IDs that contain it.

This structure is exposed through two methods with distinct roles:

- **`build(products)` returns `None`.** Its purpose is not to compute a
  result but to populate `self.data` as a side effect. This is intentional:
  the caller runs it once, at startup, and never needs a return value
  from it.
- **`lookup(word)` returns the matching `set[str]` of product IDs** for
  that token — O(1) average to find the bucket via the hash table, then
  the cost of returning it is proportional to k, the number of matches.
  We return a `set` (not a `list`) because it mirrors the internal storage
  exactly, avoiding any conversion step, and lets a caller doing a
  multi-token search (Part 2) combine several lookups with a native set
  union (`|`) instead of manually deduplicating IDs across tokens. If no
  product matches, `lookup` returns an empty set, never raises an error.
  
## Part 2: Ranked search
### 1. Data structures

We use a set of query tokens to ensure we only use unique query tokens.
  queryTokens = set(tokenize(query))

USE
  * This will provide very fast membership testing (O(1) average case), and prevent repeated words in a query from unfairly increasing a product's score.

A Counter structure is used to count how many query terms match each product.
USE
  * Efficiently counts occurrences without manually checking whether keys already exist.
  * The count is later used to compute each product's relevance score.
The 'Inverted index' and the 'Catalog' both use a dictionary to store and retrieve indexed data efficiently.
USE
  * Provides average O(1) lookup time.
  * Makes retrieving products and token matches very efficient during a search. 

To keep only the top k highest-scoring products we use a min_heap structure managed by the heapify library in heap module
Each element is stored as: [score, product]

As products are scored:

  * If fewer than top_k products have been found, they are added.
  * Once the heap reaches top_k, only products with a higher score than the current minimum replace an existing entry.

USE

  * Avoids sorting every matching product.
  * Maintains only the best k products during the search.
  * More efficient than sorting all results when the number of matching products is large.

The structures above-mentioned allow us to both quickly and efficiently find and score products and return only the highest scored results.

### 2. Complexity
#### Time: overall

All in all (combining all the stages) we can observe a complexity of  O(q + m + (n log k)) where:
  * q = number of unique query tokens
  * m = total number of product matches returned by the inverted index (across all query tokens)
  * n = number of unique candidate products (len(data_values))
  * k = top_k

This is because usually k is usually much smaller than k

#### Time: Worst-case complexity
In the worst case, every query token matches every product.

If N is the total number of products, then:
  * m=qN
  * n=N

The complexity becomes: O(qN +N log k). Since qN dominates it becomes O(qN).

#### Space: overall

The search method allocates:

Query token set: O(q)
Counter for candidate products: O(n)
Heap of top results: O(k)

Overall: O(q+n+k) or simply O(n) since k and q are generally much smaller than the number of candidate products.

## Part 3: Category Tree Filter

### 1. Data Structure

Category hierarchy is modeled as a **tree of `CategoryNode` objects**.
When a product has the category `"Electronics/Computers/Peripherals"`, that string constitutes a path with three levels: "Electronics" is a parent of "Computers", which is a parent of "Peripherals". A tree mirrors this structure; each node may have an arbitrary number of child nodes.

**Why a tree instead of a flat scan?**

The flat scan loop over all products and check `product.category.startswith(target_path)` on every query. This approach is O(P), where P is the catalog size, and requires string splitting and comparison for each product.

The tree shifts that cost to build time and makes each query O(P_sub), where P_sub is the number of products in the queried subtree. For a small hierarchy, this is substantially faster.

**Why `dict` for children instead of a list?**

If children were stored as a list, walking from one path segment to the next would require iterating through the list until a matching name is found. This operation would be O(N), where N is the number of children.
With a dict, the operation is O(1). For a small tree, the list approach is acceptable, but it does not scale well for larger trees. Dicts also make the intent explicit: each entry maps a child name to the corresponding child node.

**Why `set` for `productIds` instead of a list?**

First, when product IDs from multiple nodes (parent and all descendants) are combined via `set.update()`, the operation merges them without creating duplicates. If lists were used, every merge would require explicit duplicate checking.

Second, downstream in the ranking engine, product IDs are used as set keys for set operations (union, intersection). Storing them as sets from the outset avoids conversion costs.

---

To collect all product IDs under a category (including subcategories), the implementation uses **Depth-First Search**.

**Why DFS over BFS?**

In practice, both strategies perform equally for the dataset sizes used here. However, DFS offers a practical advantage: Python's `list` works as a stack natively (`list.pop()` removes from the end in O(1) time). For BFS, one would typically use `collections.deque` to achieve O(1) pops from the front. In terms of memory, DFS requires O(depth) space while BFS requires O(width) space. The category tree has lower depth than width, making DFS more memory-efficient.

#### Filtering before scoring

In `ranking.py`, `search_in_category` operates as follows:

```python
def search_in_category(self, query, category, top_k=10):
    filtered_product_ids = self._categoryTree.collect_product_ids(category)
    return self.search(query, top_k, filtered_product_ids)
```

The method first collects the filtered ID set, then passes that set to `search()`, which scores only products whose IDs are present in the set.

Scoring every product first and subsequently discarding those outside the category would waste computation on irrelevant products. By filtering first, the candidate pool is reduced. The filter itself (the tree traversal) is inexpensive: a handful of dict lookups and set unions.

The tree makes this approach efficient because it has already grouped products by category path at build time. Without the tree, each query would need to scan every product's category string at query time. This would still be O(catalog), but it would interleave string comparisons with scoring, preventing the scoring step from being skipped for non-matching products.

### 2. Complexity

#### Build-time Complexity

**O(P × D)** where:

- **P** = number of products in the catalog
- **D** = average depth of a category path in segments

Total memory is roughly proportional to the number of unique path segments plus the number of products. Product IDs are stored only once, in their most specific category node (the leaf), no duplication occurs across nodes.

#### Query-time Complexity

**O(P_sub)**, where **P_sub** is the number of products in the queried subtree.

The traversal overhead (stack operations) scales with the number of nodes visited, O(N_nodes), but the dominant cost is collecting product IDs from each visited node into a result set via `set.update()`, which is O(P_sub). In practice, the node count is small (30–35 nodes in the full tree), so the traversal component is negligible.

In the worst case (querying the root), the entire catalog is collected. This remains efficient enough that further optimization would introduce code complexity without observable speedup.

### 3. Concrete Scenario Analysis

A user runs: `python search.py "laptop" --category "Electronics"`

The following describes the exact sequence of operations:

**Step 1: `search_in_category("laptop", "Electronics")` is called.**

**Step 2: `_find_node("Electronics")` locates the starting point.**

- The string `"Electronics"` is split into `["Electronics"]`.
- The search begins at `_root` (a dummy root node).
- The key `"Electronics"` is looked up in `_root.children` via a single dict lookup.
- The `"Electronics"` node is found and returned.

Cost: one string split, one dict lookup.

**Step 3: `collect_product_ids` traverses the subtree.**

The subtree rooted at `"Electronics"` includes approximately seven nodes:

- `Electronics` (products categorized directly at `"Electronics"`)
- `Electronics/Computers/Laptops`
- `Electronics/Computers/Peripherals`
- ...

For each node, the algorithm pops it from the stack, adds its product IDs to the result set, and pushes its children. The result is a set of approximately 2,300 product IDs — roughly half the catalog, as approximately half of the 15 category paths begin with `"Electronics"`.

**Step 4: The filtered set is passed to `search("laptop", top_k=10, filtered_ids=set_of_2300_ids)`.**

Inside `search()`:

- The query `"laptop"` is tokenized → `{"laptop"}`.
- The token is looked up in the inverted index, yielding a set of product IDs whose name or tags contain "laptop" (approximately 200 IDs).
- Only IDs present in `filtered_ids` are considered.
- Each of the ~100–200 candidates is scored using the formula: `(matched_tokens / total_query_tokens) * 0.5 + (stock > 0) * 0.2 + (1 / log2(sales_rank + 2)) * 0.3`.
- The top 10 results are retained using a min-heap.

**Comparison with the non-tree alternative:**

Without the tree, `search_in_category` would need to:

1. Load all 5,000 products.
2. For each product, check whether its category starts with `"Electronics"` — that is, call `startswith()`, which performs character-by-character comparison.
3. Score only the matching products.

While this approach works, the category check (steps 1–2) costs O(catalog). With the tree, collecting the filtered products costs O(subtree products) rather than O(catalog), yielding a noticeable improvement in the filtering step. The tree also makes the code cleaner: `collect_product_ids` returns a set that can be composed naturally with other filters. A flat scan would require the filtering logic to be interleaved with the scoring loop, making the system harder to extend or test independently.

---

## Part 4: "Did you mean?" Suggestions

### 1. Data Structure

The suggestion engine is invoked when a user types a word that matches nothing in the index and must find the closest real words from the vocabulary and suggest them.

The central structure is a **vocabulary**: the set of every unique word appearing in the catalog's product names and tags. Since the index is built at startup (Part 1), the vocabulary is available at no additional cost, no extra pass over the catalog is required.

The vocabulary is stored as a **`set[str]`**. Because the vocabulary is small (approximately 40 words), the suggestion algorithm can scan the entire set and compare each word against the input without requiring ordering or indexing. The set provides O(1) membership testing (`if word in vocabulary`), used to skip exact matches (for which no suggestion is needed).

For measuring string dissimilarity, two algorithms are employed:

**Levenshtein distance**: counts the minimum number of single-character insertions, deletions, and substitutions needed to transform one string into another. For example:

- `"cat"` → `"cats"` (insert 's' at the end): distance 1.
- `"cat"` → `"kitten"`: insert 'k' at position 0, substitute 'c' with 'i', substitute 'a' with 't', insert 'e' after position 4, insert 'n' after position 5 — the minimum is 5 operations.
- A key property is that Levenshtein handles strings of differing lengths correctly, because insertions and deletions allow alignment.

**Hamming distance**: counts only the number of character substitutions between two strings of **equal length**. For example:

- `"cat"` → `"cut"` (replace 'a' with 'u'): distance 1.

Hamming does not handle insertions or deletions, so it is applicable only to strings of identical length. However, because it does not require building a 2D matrix, it is substantially faster: a single loop over the characters, O(L) instead of O(L²).

Both functions accept a `maxEdit` parameter. If the computed distance exceeds this threshold, the function terminates early and returns the current value. This avoids computing the full distance for words that are clearly too dissimilar to be useful suggestions.

#### How the vocabulary is connected?

The `SuggestionEngine` does not know the origin of the vocabulary. It accepts any object implementing the `VocabularyProvider` protocol, which requires a single method: `getVocabulary() -> set[str]`. The `InvertedIndex` happens to provide this method, but the vocabulary source could be swapped (a dictionary file, a database, etc.) without modifying the suggestion logic. This design choice decouples the suggestion engine from the rest of the system.

#### Three optimizations in `suggest()`

The `suggest()` method employs three performance optimizations:

**1. Length-based discard filter.**

A fundamental property of edit distance is that the Levenshtein distance between two strings is always at least `abs(len(a) - len(b))`. To make two strings equal, at least as many insertions or deletions as their length difference are required. If the strings differ by five characters, at least five operations are needed simply to balance the lengths, regardless of the character content.

This filter is especially effective because vocabulary words span a range of lengths: "pro" (3), "max" (3), "usb" (3), "hdmi" (4), "smart" (5), "laser" (5), "gaming" (6), "silent" (6), "wireless" (8), "bluetooth" (9), etc. For an 8-character input, all 3–5 character words are skipped by this filter, eliminating approximately half the vocabulary before any distance computation begins.

**2. Hamming shortcut for equal-length words.**

When `len(word) == len(input)`, Hamming distance is used instead of Levenshtein. Hamming counts only character substitutions and does not consider insertions or deletions, because the strings are already the same length. The implementation is a single loop:

```python
for index in range(len(a)):
    if a[index] != b[index]:
        distance += 1
        if useMaxEdit and distance > maxEdit:
            return distance
```

In contrast, Levenshtein allocates a 2D matrix of size `(lenA+1) × (lenB+1)` and fills every cell. For 8-character strings, this is a 9 × 9 = 81-cell table, with each cell computing a minimum of three values. Hamming performs just 8 character comparisons.

**3. Early exits in Levenshtein.**

The implementation adds an additional optimization: after computing each row of the Levenshtein matrix, if `maxEdit > min(values_in_row)`, the smallest value in that row is checked. If even the smallest value exceeds `maxEdit`, the final distance cannot be within the threshold (the minimum value in each row is non-decreasing), so the algorithm returns immediately. This avoids computing the remainder of the matrix for words that are clearly too distant.

For example, comparing `"keyborad"` with `"zzzzzzzz"` (eight z's) with `maxEdit = 2`: by row 3 or 4, the minimum value in each row exceeds 2, and the algorithm terminates early instead of computing all 81 cells.

### 2. Complexity

#### Build-time Complexity

**O(1)**, the suggestion engine adds no build time of its own.

The vocabulary is obtained from `InvertedIndex.getVocabulary()`, which returns `self.data.keys()`. The inverted index is built in `CatalogSearchRankingEngine.__init__()` regardless of whether suggestions are used. The `SuggestionEngine` merely stores a reference to the vocabulary provider; it does not call `getVocabulary()` until a query arrives.

Thus, the total build cost for the suggestion feature is zero: it reuses work already performed for Part 1.

#### Query-time Complexity

Worst case: **O(V × L² + V log V)** where:

- **V** = vocabulary size
- **L** = length of the input word

The V × L² term arises from the Levenshtein matrix: for each of V words, a matrix of size (L+1) × (L+1) may need to be computed, costing O(L²). The V log V term accounts for sorting the results at the end.

In practice, the actual runtime is substantially lower due to the three optimizations explained earlier.

#### Space complexity at query time

The Levenshtein matrix constitutes the only significant allocation: O(L²) integers. For L = 8, this amounts to 81 integers — negligible. The result list and suggestion tuples are also small (at most V entries). No persistent memory is retained between queries.

### 3. Concrete Scenario Analysis

A user types `"keyborad"` (8 characters) and receives zero search results. The system's `suggest()` function is invoked to find the closest vocabulary words.

The following describes the exact sequence of operations:

**Step 1: Fetch the vocabulary.**

`suggest()` calls `self._vocabularyProvider.getVocabulary()`, which returns the inverted index's keys: a set of approximately 40 words. For this analysis, the vocabulary is assumed to include words such as `keyboard`, `wireless`, `ergonomic`, `compact`, `headset`, `webcam`, `chair`, `desk`, `lamp`, `cable`, `adapter`, `pro`, `lite`, `plus`, `max`, `ultra`, `hdmi`, and `usb`.

**Step 2: Iterate over each vocabulary word and apply the length filter.**

Input length = 8 ("keyborad"). Discard distance = 2. Only words with length between 6 and 10 (inclusive) are considered.

| Word | Length | abs(8 - len) ≤ 2? | Action |
|---|---|---|---|
| keyboard | 8 | 0 ≤ 2 | Process |
| wireless | 8 | 0 ≤ 2 | Process |
| rechargeable | 12 | 4 > 2 | **Skip** |
| adjustable | 10 | 2 ≤ 2 | Process |
| gaming | 6 | 2 ≤ 2 | Process |
| ... | ... | ... | ... |
| usb | 3 | 5 > 2 | **Skip** |
| pro | 3 | 5 > 2 | **Skip** |

**Step 3: Compute edit distance for each passing word.**

For each word passing the filter, the algorithm checks whether its length matches the input (8 characters). If so, Hamming distance is used; otherwise, Levenshtein distance is used.

A few representative comparisons are traced below:

- **"wireless" (len 8) vs "keyborad" (len 8)**: Same length → Hamming.
  Character-by-character comparison: w/k, i/e, r/y, e/b, l/o, e/r, s/a, s/d.
  First mismatch sets distance to 1. Second mismatch sets distance to 2. Third mismatch sets distance to 3, which exceeds `maxEdit=2`. Early exit with distance 3. Rejected.

- **"ergonomic" (len 9) vs "keyborad" (len 8)**: Different length → Levenshtein.
  A 10×9 matrix is computed. The first row and column contain base cases (0, 1, 2, ...). As each row is filled, the minimum value in the row is tracked. After a few rows, the minimum reaches 1 (at least one insertion or deletion is required due to the length difference). Because the strings share almost no common prefix, distances grow quickly. By row 3 or 4, the row minimum exceeds 2, and the algorithm exits early. Rejected.

- **"foldable" (len 8) vs "keyborad" (len 8)**: Same length → Hamming.
  f/k (mismatch), o/e (mismatch), l/y (mismatch). Distance reaches 3 after only 3 character comparisons. Early exit. Rejected.

- **"compact" (len 7) vs "keyborad" (len 8)**: Different length → Levenshtein with 8×9 matrix.
  The length difference is 1, so the minimum possible distance is 1. However, the actual distance is substantially higher because the strings share no obvious similarity. The Levenshtein matrix quickly shows row minima exceeding 2. Early exit. Rejected.

After all comparisons, the only word with distance ≤ 2 is **"keyboard"** (distance 2).

**Step 4: Sort and return.**

A list of `(distance, word)` tuples is constructed: `[(2, "keyboard")]`.
The list is sorted by distance, then alphabetically: `[(2, "keyboard")]`.
The top `max_suggestions` (3) words are returned → `["keyboard"]`.