from librarian import db


book_genre = db.Table('book_genre',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'))
)


author_book = db.Table('author_book',
    db.Column('author_id', db.Integer, db.ForeignKey('author.id')),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'))
)


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)

    def __init__(self, title):
        self.title = title
    
    def __repr__(self):
        return "<Genre %r>" % self.id


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
    
    def __repr__(self):
        return "<Author %r>" % self.id

    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    @classmethod
    def search_starting_from(cls, prefix):
        prefix = prefix.lower()
        prefix += '%'
        return cls.query.filter(cls.last_name.ilike(prefix))



class Sequence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    books = db.relationship('Book', backref='sequence', lazy='dynamic')

    def __init__(self, title):
        self.title = title
    
    def __repr__(self):
        return "<Seuence %r>" % self.id


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    annotation = db.Column(db.String())
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequence.id'))
    sequence_number = db.Column(db.Integer())
    authors = db.relationship('Author', secondary=author_book,
        backref=db.backref('books', lazy='dynamic'))
    genres = db.relationship('Genre', secondary=book_genre,
        backref=db.backref('books', lazy='dynamic'))

    def __init__(self, id, title, annotation, sequence_id, sequence_number, authors, genres):
        self.id = id
        self.title = title
        self.annotation = annotation
        self.sequence_id = sequence_id
        self.sequence_number = sequence_number
        self.authors = authors
        self.genres = genres

    def __repr__(self):
        return '<Book %r>' % self.id
    
    @classmethod
    def search_by_title(cls, title):
        title = title.lower()
        title = title.replace(' ', '%')
        title = '%' + title + '%'
        return cls.query.filter(cls.title.ilike(title))
