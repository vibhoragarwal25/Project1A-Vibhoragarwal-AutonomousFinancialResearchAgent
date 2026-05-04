with open('tools/__init__.py', 'r') as f:
    content = f.read()

# Fix vector_db_search function line
old_search = '''            function=_vector_db_search_fn, top_k=5, ticker=None, **kwargs: {
                "results": _vs.search(query or kwargs.get('company', '') or '', top_k, ticker or kwargs.get('ticker')),
                "count": len(_vs.search(query or kwargs.get('company', '') or '', top_k, ticker or kwargs.get('ticker')))
            },'''

new_search = '''            function=_vector_db_search_fn,'''

# Fix vector_db_store function line
old_store = '''            function=_vector_db_search_fn, ticker, source_type, **kwargs: {
                "doc_id": _vs.store(content, ticker, source_type)
            },'''

new_store = '''            function=_vector_db_store_fn,'''

content = content.replace(old_search, new_search)
content = content.replace(old_store, new_store)

with open('tools/__init__.py', 'w') as f:
    f.write(content)

print("Fixed successfully")
