# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, abort

from librarian.util import books_sorted, authors_sorted
from librarian.models import Author


AUTHORS_PER_PAGE = 20


opds = Blueprint('opds', __name__, template_folder='templates',
                 static_folder='static')


eng_chars = 'abcdefghijklmnopqrstuvwxyz'
rus_chars = u'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'


@opds.route('/')
def authors_chooser():
    curr_prefix = request.args.get('curr_prefix', '')
    show_authors = request.args.get('show_authors', False)
    lang = request.args.get('lang', 'rus')
    if lang == 'rus':
        chars = rus_chars
    elif lang == 'eng':
        chars = eng_chars
    else:
        assert False, "No such language"

    if show_authors:
        authors = Author.query.filter(Author.last_name.ilike(curr_prefix))
        return render_template('opds_authors.jinja', authors=authors)

    authors = Author.search_starting_from(curr_prefix)
    if authors.count() < AUTHORS_PER_PAGE:
        authors = authors_sorted(authors)
        return render_template('opds_authors.jinja', authors=authors)
    prefixes = []
    for char in chars:
        new_prefix = curr_prefix + char
        count = Author.search_starting_from(new_prefix).count()
        if count:
            prefixes.append((new_prefix, count))
    return render_template('opds_authors_chooser.jinja', curr_prefix=curr_prefix,
                           prefixes=prefixes, lang=lang)


@opds.route('/a-<int:author_id>')
def author_books(author_id):
    author = Author.query.filter_by(id=author_id).first()
    if not author:
        abort(404)
    books = books_sorted(author.books)
    return render_template('opds_books_list.jinja', author=author, books=books)
