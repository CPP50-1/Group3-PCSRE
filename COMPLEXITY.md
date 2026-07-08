## Part 1: Inverted Index

### 1. Data Structure

The index maps every word in a product's `name` or `tags` to the set of
product IDs that contain it: a **`dict[str, set[str]]`**, stored as the
private `self.__data`, exposed only via `get_index()` and `getVocabulary()`.

**Why `dict` instead of a flat list scan?**

Resolving a query token to its candidates needs a direct jump, not a scan.
`self.__data.get(word)` is a single hash-table lookup, independent of
catalog size.

**Why `set` for product IDs instead of a list?**

A word can appear in both `name` and a tag of the same product (e.g.
`name = "Wireless Keyboard"`, tag `"keyboard"`). This is guarded explicitly:

```python
ids = self.__data.setdefault(word, set())
if product.id not in ids:
    ids.add(product.id)
```

With a `set`, this check-and-insert is O(1) average. With a `list`, the
same guard would cost O(m) per check (m = current list length), making
cumulative insertion for a popular word O(m²) instead of O(m). Sets also
match what downstream parts need without conversion: Part 2's multi-token
search unions several lookups (`|`), and Part 3's category filter
intersects query matches with a category subtree (`&`) — both native,
optimized set operations.

**Two exposed operations, two roles:**

- **`build(products)`** populates `self.__data` as its main effect —
  iterating once over every product, tokenizing `[product.name] + list(product.tags)`,
  inserting each token — and also returns the finished dict for
  convenience. Runs exactly once, at startup.
- **`get_index()`** returns the whole dict, O(1), no copying; a caller
  resolves one word via `get_index().get(word, set())`. **`getVocabulary()`**
  returns `set(self.__data.keys())` for Part 4's suggestion engine, which
  needs every known word but not their ID sets.

**Alternative considered: dict of lists.** Same duplicate-check logic, but
O(m) per check instead of O(1), giving O(m²) worst-case cumulative
insertion cost. It would also force Parts 2 and 3 to reimplement
union/intersection by hand instead of using native set operations. Dict of
sets wins on both fronts at negligible memory cost.
### 2. Complexity

#### Build-time Complexity

**O(n · t · L)**, where:

- **n** = number of products in the catalog
- **t** = average number of text fields per product (1 for `name`, plus
  one per tag)
- **L** = average length (in characters) of each text field

For each product, `build()` iterates over `[product.name] + list(product.tags)`
**t** fields and calls `tokenize()` on each. `tokenize()` itself runs a
single regex scan over the text (`_TOKEN_PATTERN.findall`), which is O(L).
The resulting tokens are then lowercased and length-filtered in two linear
passes, also O(L) combined. For each surviving token, `self.__data.setdefault(word, set())`
plus the `if product.id not in ids` check and `.add()` are O(1) amortized
(set operations). Multiplying across all products and all their text
fields gives O(n · t · L) total.

#### Query-time Complexity

**O(1) average**, via `get_index().get(word)` (or `word in getVocabulary()`).

Retrieving the set of product IDs for a single word is a single hash-table
lookup into `self.__data` — independent of n, the catalog size — followed
by O(k) to read the k matching IDs out of the returned set. No method here
loops over `self.__data`'s full contents to answer a single-word query.

#### Space complexity

**O(V + n)**, where **V** = number of unique tokens in the vocabulary
(dict keys) and each token maps to a set holding up to n product IDs in
the worst case (a token appearing in every product). In practice, V is
small (tens of words) and each token's set holds a small fraction of n, so
actual memory use stays well below n × V.

### 3. Concrete Scenario Analysis

A catalog of n = 3 products is indexed, then queried for `"keyboard"`.

```python
products = [
    Product(id="P1", name="Wireless Keyboard", tags={"bluetooth", "keyboard"}, ...),
    Product(id="P2", name="USB Mouse",          tags={"wired"},git ...),
    Product(id="P3", name="Keyboard Cover",     tags={"silicone"},             ...),
]
```

**Step 1: `build(products)` iterates over each product.**

For **P1**, `texts = ["Wireless Keyboard", "bluetooth", "keyboard"]`
(order of `tags` set iteration may vary, this is illustrative).

| Text | `tokenize()` output |
|---|---|
| `"Wireless Keyboard"` | `["wireless", "keyboard"]` |
| `"bluetooth"` | `["bluetooth"]` |
| `"keyboard"` | `["keyboard"]` |

**Step 2: Trace `tokenize("Wireless Keyboard")` internally.**

- `_TOKEN_PATTERN.findall("Wireless Keyboard")` → `["Wireless", "Keyboard"]`
  (regex splits on the space, keeping only alphanumeric runs).
- `lowercase_tokens` → `["wireless", "keyboard"]`.
- Length filter (`len(tok) >= 3`): both pass (8 and 8 characters) → final
  result `["wireless", "keyboard"]`.

**Step 3: Each token is inserted into `self.__data`.**

For P1's three texts, the following insertions happen (duplicates
collapsed by the `if product.id not in ids` guard before each `.add()`):

- `"wireless"` → `{"P1"}`
- `"keyboard"` → `{"P1"}` (inserted once from `name`; the second
  occurrence from the tag `"keyboard"` is skipped, since `"P1"` is
  already in the set)
- `"bluetooth"` → `{"P1"}`

**Step 4: P2 and P3 are processed the same way**, extending the index:

```python
{
    "wireless":  {"P1"},
    "keyboard":  {"P1", "P3"},   # P1 (name) and P3 (name)
    "bluetooth": {"P1"},
    "usb":       {"P2"},
    "mouse":     {"P2"},
    "wired":     {"P2"},
    "cover":     {"P3"},
    "silicone":  {"P3"},
}
```

Total cost: 3 products × ~3 text fields each × O(L) tokenization + O(1)
amortized insertions per token — a single linear pass over the catalog,
performed once at startup.



