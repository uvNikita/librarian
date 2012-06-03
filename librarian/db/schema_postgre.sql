CREATE TABLE sequence(sequence_id SERIAL PRIMARY KEY, title TEXT);

CREATE TABLE book(
    book_id INTEGER PRIMARY KEY,
    book_title TEXT NOT NULL,
    annotation TEXT,
    sequence_id INTEGER,
    sequence_number INTEGER,
    FOREIGN KEY(sequence_id) REFERENCES sequence(sequence_id));

CREATE TABLE author(author_id SERIAL PRIMARY KEY, first_name TEXT NOT NULL, last_name TEXT NOT NULL);

CREATE TABLE author_book(author_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    FOREIGN KEY(author_id) REFERENCES author(author_id),
    FOREIGN KEY(book_id) REFERENCES book(book_id));

CREATE TABLE book_genre(book_id INTEGER NOT NULL, genre TEXT NOT NULL, FOREIGN KEY(book_id) REFERENCES book(book_id));
