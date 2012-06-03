import psycopg2
import psycopg2.extras
from librarian.models import Book, Sequence, Author
from librarian import app

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)


class Database(object):
    def __init__(self, db_connect=None):
        if db_connect:
            self.db_connect = db_connect
        else:
            self.db_connect = app.config['DATABASE']

    def __enter__(self):
        self.db = psycopg2.connect(self.db_connect)
        self.cursor = self.db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return self

    def __exit__(self, type, value, traceback):
        self.db.close()

    def get_book_by_id(self, book_id):
        self.cursor.execute("SELECT book_id, book_title, annotation, sequence_id, sequence_number FROM book WHERE book_id = %s", (book_id,))
        book = self.cursor.fetchone()
        if not book:
            return None
        authors = []
        self.cursor.execute("SELECT author_id FROM author_book WHERE book_id = %s", (book_id,))
        for book_author in self.cursor.fetchall():
            authors += [self.get_author_by_id(book_author['author_id'])]
        genres = []
        self.cursor.execute("SELECT genre FROM book_genre WHERE book_id = %s", (book_id,))
        for book_genre in self.cursor.fetchall():
            genres += [book_genre['genre']]
        sequence = None
        if book['sequence_id']:
            self.cursor.execute("SELECT title FROM sequence WHERE sequence_id = %s", (book['sequence_id'],))
            sequence = Sequence(book['sequence_id'], self.cursor.fetchone()['title'])
        return Book(
            book_id=book['book_id'],
            title=book['book_title'], 
            authors=authors,
            annotation=book['annotation'],
            sequence=sequence,
            sequence_number=book['sequence_number'],
            genres=genres
        )

    def get_author_by_id(self, author_id):
        self.cursor.execute("SELECT author_id, first_name, last_name FROM author WHERE author_id = %s", (author_id,))
        author = self.cursor.fetchone()
        if not author:
            return None
        return Author(
            author_id=author['author_id'],
            first_name=author['first_name'],
            last_name=author['last_name'],
        )

    def get_books_by_author(self, author_id):
        # order by book_id ( or sequence_id, sequence_number, book_id)
        books = []
        self.cursor.execute("SELECT book_id FROM author_book WHERE author_id = %s ", (author_id,))
        for author_book in self.cursor.fetchall():
            books += [self.get_book_by_id(author_book['book_id'])]
        return books

    def get_sequence_books(self, sequence_id):
        # order by sequence_number
        books = []
        self.cursor.execute("SELECT book_id FROM book WHERE sequence_id = %s", (sequence_id,))
        for sequence_book in self.cursor.fetchall():
            books += [self.get_book_by_id(sequence_book['book_id'])]
        return books

    def search_by_title(self, title, author_id=None):
        # order by book_id
        books = []
        title = title.lower()
        title = title.replace(' ', '%')
        title = '%' + title + '%'
        if author_id:
            self.cursor.execute(
                "SELECT book.book_id FROM book, author_book WHERE author_book.book_id=book.book_id and author_book.author_id = %s and book_title ILIKE %s",
                (author_id, title,))
            for book in self.cursor.fetchall():
                books += [self.get_book_by_id(book['book_id'])]
        else:
            self.cursor.execute("SELECT book_id FROM book WHERE book_title ILIKE %s", (title,))
            for book in self.cursor.fetchall():
                books += [self.get_book_by_id(book['book_id'])]
        return books

    def search_authors_starting_from(self, prefix):
        # order by author_id
        prefix = prefix.lower()
        prefix += '%'
        authors = []
        self.cursor.execute("SELECT author_id FROM author WHERE last_name ILIKE %s", (prefix,))
        for author in self.cursor.fetchall():
            authors += [self.get_author_by_id(author['author_id'])]
        return authors

    # def add_book(self, book):
    #     self.cursor.execute('select sequence_id from sequence where title=%s', (book.sequence.title,))
    #     sequence_row = self.cursor.fetchone()
    #     if sequence_row:
    #         sequence_id = sequence_row['sequence_id']
    #     else:
    #         self.cursor.execute('insert into sequence (title) values(%s)', (book.sequence.title,))
    #         sequence_id = self.cursor.lastrowid

    #     self.cursor.execute('insert into book values (:book_id, :title, :annotation, :sequence_id, :sequence_number)', {
    #         'book_id': book.book_id, 'title': book.title,
    #         'annotation': book.annotation, 'sequence_id': sequence_id,
    #         'sequence_number': book.sequence_number
    #     })

    #     #authors
    #     for author in book.authors:
    #         self.cursor.execute('select author_id from author where first_name=%s and last_name=%s', (author.first_name, author.last_name))
    #         author_row = self.cursor.fetchone()
    #         if author_row:
    #             author_id = author_row['author_id']
    #         else:
    #             self.cursor.execute('insert into author (first_name, last_name) values (%s, %s)', (author.first_name, author.last_name))
    #             author_id = self.cursor.lastrowid
    #         self.cursor.execute('insert into author_book values(%s, %s)', (author_id, book.book_id))

    #     for genre in book.genres:
    #         self.cursor.execute('insert into book_genre values(%s, %s)', (book.book_id, genre))
    #     self.db.commit()

    def add_book(self, book):
        pass

    def add_author(self, first_name, last_name):
        return Author(1, first_name, last_name)
