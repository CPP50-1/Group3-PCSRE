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
