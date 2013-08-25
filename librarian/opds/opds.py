# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, abort
from sqlalchemy import distinct

from librarian.util import books_sorted, authors_sorted, xml_response
from librarian.models import Author, Sequence, Book, author_book, db


AUTHORS_PER_PAGE = 20


opds = Blueprint('opds', __name__, template_folder='templates',
                 static_folder='static')


eng_chars = 'abcdefghijklmnopqrstuvwxyz'
rus_chars = u'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'


@opds.route('/')
@xml_response
def authors_chooser():
    curr_prefix = request.args.get('curr_prefix', '')
    show_authors = request.args.get('show_authors', False)
    lang = request.args.get('lang', 'rus')
    if lang == 'rus':
        chars = rus_chars
    elif lang == 'eng':
        chars = eng_chars
    else:
        abort(404)

    if show_authors:
        authors = Author.query.filter(Author.last_name.ilike(curr_prefix))
        return render_template('opds_authors.xml', authors=authors)

    authors = Author.search_starting_from(curr_prefix)
    if authors.count() < AUTHORS_PER_PAGE:
        authors = authors_sorted(authors)
        return render_template('opds_authors.xml', authors=authors)
    prefixes = []
    for char in chars:
        new_prefix = curr_prefix + char
        count = Author.search_starting_from(new_prefix).count()
        if count:
            prefixes.append((new_prefix, count))
    return render_template('opds_authors_chooser.xml', curr_prefix=curr_prefix,
                           prefixes=prefixes, lang=lang)


@opds.route('/a-<int:author_id>/all')
@xml_response
def author_books(author_id):
    author = Author.query.filter_by(id=author_id).first()
    if not author:
        abort(404)
    books = books_sorted(author.books).all()
    return render_template('opds_books_list.xml', author=author, books=books)


@opds.route('/a-<int:author_id>/other')
@xml_response
def author_books_other(author_id):
    author = Author.query.get(author_id)
    if not author:
        abort(404)
    books = author.books.filter_by(sequence_id=None).all()
    return render_template('opds_books_list.xml', author=author, books=books)


@opds.route('/a-<int:author_id>')
@xml_response
def author_seqs(author_id):
    author = Author.query.get(author_id)
    if not author:
        abort(404)
    seq_ids = (
        db.session.query(distinct(Book.sequence_id))
        .join(author_book)
        .filter_by(author_id=author_id)
        .all())
    if seq_ids:
        seqs = Sequence.query.filter(Sequence.id.in_(seq_ids)).all()
    else:
        seqs = []
    # CoolReader doesn't support redirects in opds: http://sourceforge.net/p/crengine/bugs/276/
    # if not seqs:
    #     return redirect(url_for('.author_books', author_id=author_id))
    return render_template('opds_seqs_list.xml', author=author, seqs=seqs)


@opds.route('/s-<int:seq_id>')
@xml_response
def seq_books(seq_id):
    books = books_sorted(Book.query.filter_by(sequence_id=seq_id)).all()
    if not books:
        abort(404)
    return render_template('opds_books_list.xml', books=books)
