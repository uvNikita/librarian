import models
from models import Book, Author

def get_book_by_id(book_id):
    return Book(book_id, "book title", [Author(1, "first name", "second name")], None, None, None)


def get_author_by_id(author_id):
    return Author(author_id, "first name", "second name")


def get_books_by_author(author_id):
    return [Book(1, "book title", [Author(author_id, "first name", "second name")], None, None, None)]


def add_book(book_id, title, author_ids, genre=None, sequence=None, annotation=None):
    authors = [get_author_by_id(author_id) for author_id in author_ids]
    return Book(book_id, title, authors, genre, sequence, annotation)


def add_author(first_name, last_name):
    return Author(1, first_name, last_name)
