from consoleargs import command
from librarian.models import Author, Book, Sequence
from librarian.db import Database

@command
def main(inp_filename, db_filename):
    for line in open(inp_filename):
        parts = line.split('~')
        unparsed_authors = parts[0].split(':')[:-1]
        authors = []
        for unparsed_author in unparsed_authors:
            unparsed_author = unparsed_author.split(',')
            last_name = unparsed_author[0]
            first_name = unparsed_author[1]
            authors += [Author(
                author_id=None,
                first_name=first_name,
                last_name=last_name
                )]
        
        genres = parts[1].split(':')[:-1]
        title = parts[2]
        sequence = Sequence(sequence_id=None, title=parts[3]) if parts[3] else None
        sequence_number = int(parts[4]) if parts[4] else None
        book_id = int(parts[5])
        book = Book(
                book_id=book_id,
                title=title,
                authors=authors,
                genres=genres,
                sequence=sequence,
                sequence_number=sequence_number,
                annotation=None
        )

        with Database() as db:
            db.add_book(book)


if __name__ == "__main__":
    main()
