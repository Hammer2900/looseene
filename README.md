# looseene 🕵️‍♂️
A tiny, persistent full-text search engine in one file, built with Python.

It's like Lucene, but... *looser*.

## Features
- Persistent on-disk storage
- Full-text indexing with BM25 ranking
- Compaction to merge segments and clean up data
- Highlighting search results in text snippets
- Simple, clean API

## Quick Start
```python
from looseene import create_index, add_to_index, search_text, highlight_result

# 1. Create an index
create_index('my_index', schema={'id': int, 'content': str}, path='./my_index_data')

# 2. Add data
add_to_index('my_index', {'id': 1, 'content': 'The quick brown fox jumps over the lazy dog.'})
add_to_index('my_index', {'id': 2, 'content': 'A lazy developer never creates a good search engine.'})

# 3. Search
query = "lazy fox"
for doc in search_text('my_index', query):
    snippet = highlight_result(doc, 'content', query)
    print(f"ID: {doc['id']}, Snippet: {snippet}")
```
