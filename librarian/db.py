import sqlite3
from librarian.models import Book, Author
from librarian import app

class Database(object):
    def __init__(self):
        pass

    def __enter__(self):
        self.db = sqlite3.connect(app.config['DATABASE'])
        self.db.row_factory = sqlite3.Row
        return self

    def __exit__(self, type, value, traceback):
        self.db.close()

    def get_book_by_id(self, book_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT book_id, book_title, annotation, sequence, sequence_number FROM book WHERE book_id = ?", (book_id,))
        book = cursor.fetchone()
        authors = []
        for book_author in cursor.execute("SELECT author_id FROM author_book WHERE book_id = ?", (book_id,)):
            authors += self.get_author_by_id(book_author['author_id'])
        return Book(
            book_id=book['book_id'],
            title=book['book_title'], 
            authors=authors,
            annotation=book['annotation'],
            sequence=book['sequence'],
            sequence_number=book['sequence_number'],
            genres=[]
        )

    def get_author_by_id(self, author_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT author_id, first_name, last_name FROM author WHERE author_id = ?", (author_id,))
        author = cursor.fetchone()
        return Author(
            author_id=author['author_id'],
            first_name=author['first_name'],
            last_name=author['last_name'],
        )

    def get_books_by_author(self, author_id):
        cursor = self.db.cursor()
        books = []
        for author_book in cursor.execute("SELECT book_id FROM author_book WHERE author_id = ? ", (author_id,)):
            books += [self.get_book_by_id(author_book['book_id'])]
        return books

    def add_book(self, book_id, title, author_ids, genres=[], sequence=None, annotation=None):
        authors = [get_author_by_id(author_id) for author_id in author_ids]
        return Book(book_id, title, authors, genres, sequence, annotation)

    def add_author(self, first_name, last_name):
        return Author(1, first_name, last_name)
