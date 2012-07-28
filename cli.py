# -*- coding: utf-8 -*-

from consoleargs import command

from librarian import db
from librarian.models import Author, Book, Sequence, Genre


@command
def main(inp_filename):
    for line in open(inp_filename):
        parts = line.split('\x04')
        unparsed_authors = parts[0].split(':')[:-1]
        authors = []
        for unparsed_author in unparsed_authors:
            unparsed_author = unparsed_author.split(',')
            last_name = unparsed_author[0]
            first_name = unparsed_author[1] or None
            db_author = Author.query.filter_by(
                first_name=first_name,
                last_name=last_name
            ).first()
            if db_author:
                authors.append(db_author)
            else:
                authors.append(Author(
                    first_name=first_name,
                    last_name=last_name
                ))
        
        gen_titles = parts[1].split(':')[:-1]
        genres = []
        for gen_title in gen_titles:
            db_genre = Genre.query.filter_by(title=gen_title).first()
            if db_genre:
                genres.append(db_genre)
            else:
                genres.append(Genre(title=gen_title))

        title = parts[2]

        seq_title = parts[3] or None
        sequence = None
        if seq_title:
            db_sequence = Sequence.query.filter_by(title=seq_title).first()
            if db_sequence:
                sequence = db_sequence
            else:
                sequence = Sequence(title=seq_title)

        sequence_number = int(parts[4]) if parts[4] else None
        id = int(parts[5])
        book = Book(
                id=id,
                title=title,
                authors=authors,
                genres=genres,
                sequence=sequence,
                sequence_number=sequence_number,
                annotation=None
        )

        db.session.add(book)
        db.session.flush()
    db.session.commit()


if __name__ == "__main__":
    main()
