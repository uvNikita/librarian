import sqlite3
from librarian.models import Book, Author
from librarian import app

class Database(object):
    def __init__(self):
        pass

    def __enter__(self):
        self.db = sqlite3.connect(app.config['DATABASE'])
        return self

    def __exit__(self, type, value, traceback):
        self.db.close()

    def get_book_by_id(self, book_id):
        return Book(book_id, "book title", [Author(1, "first name", "second name")], None, None, None)

    def get_author_by_id(self, author_id):
        return Author(author_id, "first name", "second name")

    def get_books_by_author(self, author_id):
        return [Book(1, "book title", [Author(author_id, "first name", "second name")], None, None, None)]

    def add_book(self, book_id, title, author_ids, genre=None, sequence=None, annotation=None):
        authors = [get_author_by_id(author_id) for author_id in author_ids]
        return Book(book_id, title, authors, genre, sequence, annotation)

    def add_author(self, first_name, last_name):
        return Author(1, first_name, last_name)
