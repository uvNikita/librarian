# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()


book_genre = db.Table(
    'book_genre',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id', ondelete='CASCADE')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id', ondelete='CASCADE'))
)


author_book = db.Table(
    'author_book',
    db.Column('author_id', db.Integer, db.ForeignKey('author.id', ondelete='CASCADE')),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'))
)


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False, unique=True)

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Genre %r>" % self.id


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String(), nullable=False)

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return "<Author %r>" % self.id

    @classmethod
    def search_by_last_name(cls, term):
        term = term.lower()
        term = term.replace(' ', '%')
        term = '%' + term + '%'
        return cls.query.filter(cls.last_name.ilike(term))

    @property
    def full_name(self):
        if not self.first_name:
            return self.last_name
        return "%s %s" % (self.first_name, self.last_name)

    @classmethod
    def search_starting_from(cls, prefix):
        prefix = prefix.lower()
        prefix += '%'
        return cls.query.filter(cls.last_name.ilike(prefix))


class Sequence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False, unique=True)
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

    def __init__(self, id, title, annotation, sequence,
                 sequence_number, authors, genres):
        self.id = id
        self.title = title
        self.annotation = annotation
        self.sequence = sequence
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
