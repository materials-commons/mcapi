.. manual/search.rst

Search
======

The Materials Commons API exposes a simple search API for searching published datasets and public communities. It will
find matching datasets and communities, searching in their description, name and author fields. ::

    # Find published communities and datasets that contain the keyword magnesium
    matching = c.search_published_data("magnesium")

The returned matches are of type mcapi.Searchable.