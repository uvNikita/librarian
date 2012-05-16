from collections import namedtuple

Book = namedtuple('Book', ['book_id', 'title', 'authors', 'genres', 'sequence', 'annotation'])
    
Author = namedtuple('Author', ['author_id', 'first_name', 'last_name'])
