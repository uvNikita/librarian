CREATE TABLE book(book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, annotation TEXT, sequence TEXT);

CREATE TABLE author(author_id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT NOT NULL, last_name TEXT NOT NULL);

CREATE TABLE author_book(author_id INTEGER NOT NULL, book_id INTEGER NOT NULL, FOREIGN KEY(author_id) REFERENCES author(author_id), FOREIGN KEY(book_id) REFERENCES book(book_id));

CREATE TABLE book_genre(book_id INTEGER NOT NULL, genre TEXT NOT NULL, FOREIGN KEY(book_id) REFERENCES book(book_id));
