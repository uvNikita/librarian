# -*- coding: utf-8 -*-

from os import listdir, path
from zipfile import ZipFile
import mimetypes

from flask import redirect, url_for, send_file
from flask import Blueprint, current_app, request, render_template, abort
from unidecode import unidecode
from sqlalchemy import distinct
from conversion import fb2_2_epub

from librarian.util import authors_sorted, books_sorted, seqs_sorted
from librarian.util import get_image_filepath
from librarian.models import author_book, Book, Author, Sequence, db


ITEMS_PER_PAGE = 50
mimetypes.init()


main = Blueprint('main', __name__, template_folder='templates',
                 static_folder='static')


@main.route('/')
def main_page():
    return redirect(url_for('.authors_chooser'))


@main.route('/b-<int:book_id>')
def book_info(book_id):
    book = Book.query.get(book_id)
    if not book:
        abort(404)
    return render_template('book_info.html', book=book)


@main.route('/s-<int:seq_id>', defaults={'page': 1})
@main.route('/s-<int:seq_id>/p<int:page>')
def seq_books(seq_id, page):
    books = books_sorted(Book.query.filter_by(sequence_id=seq_id))
    if not books:
        abort(404)
    books_pager = books.paginate(page, ITEMS_PER_PAGE)
    return render_template('seq_books.html', books_pager=books_pager)


@main.route('/a-<int:author_id>')
def author(author_id):
    return redirect(url_for('.author_seqs', author_id=author_id))


@main.route('/a-<int:author_id>/all', defaults={'page': 1})
@main.route('/a-<int:author_id>/all/p<int:page>')
def author_books(author_id, page):
    author = Author.query.get(author_id)
    if not author:
        abort(404)
    books_pager = books_sorted(author.books).paginate(page, ITEMS_PER_PAGE)
    return render_template('books_list.html', author=author,
                           books_pager=books_pager)


@main.route('/a-<int:author_id>/other', defaults={'page': 1})
@main.route('/a-<int:author_id>/other/p<int:page>')
def author_books_other(author_id, page):
    author = Author.query.get(author_id)
    if not author:
        abort(404)
    books = author.books.filter_by(sequence_id=None)
    books_pager = books_sorted(books).paginate(page, ITEMS_PER_PAGE)
    return render_template('books_list.html', author=author,
                           books_pager=books_pager)


@main.route('/a-<int:author_id>/seqs/', defaults={'page': 1})
@main.route('/a-<int:author_id>/seqs/p<int:page>')
def author_seqs(author_id, page):
    author = Author.query.get(author_id)
    if not author:
        abort(404)
    seq_ids = (
        db.session.query(distinct(Book.sequence_id))
        .join(author_book)
        .filter_by(author_id=author_id)
        .all())
    if seq_ids:
        seqs = Sequence.query.filter(Sequence.id.in_(seq_ids))
    else:
        seqs = []
    seqs_pager = seqs_sorted(seqs).paginate(page, ITEMS_PER_PAGE)
    if not seqs_pager.total:
        return redirect(url_for('.author_books', author_id=author_id))
    return render_template('seqs_list.html', author=author,
                           seqs_pager=seqs_pager)


@main.route('/search', defaults={'page': 1})
@main.route('/search/p<int:page>')
def search(page):
    search_type = request.args.get('type', 'books')
    search_term = request.args.get('term', '')
    curr_author_id = request.args.get('curr_author_id')
    if search_type not in ('authors', 'books'):
        search_type = 'books'
    if search_type == 'authors':
        authors = authors_sorted(Author.search_by_last_name(search_term))
        authors_pager = authors.paginate(page, ITEMS_PER_PAGE)
        return render_template(
            'authors_search_results.html',
            authors_pager=authors_pager,
            search_term=search_term,
            search_type=search_type
        )
    elif search_type == 'books':
        books = books_sorted(Book.search_by_title(search_term))
        books_pager = books.paginate(page, ITEMS_PER_PAGE)
        return render_template(
            'books_search_result.html',
            books_pager=books_pager,
            search_term=search_term,
            search_type=search_type,
            curr_author_id=curr_author_id
        )
    assert False, "Uknown search type"


@main.route('/authors', defaults={'page': 1})
@main.route('/authors/p<int:page>')
def authors_chooser(page):
    prefix = request.args.get('prefix', '')
    authors_pager = None
    if prefix:
        authors = authors_sorted(Author.search_starting_from(prefix))
        authors_pager = authors.paginate(page, ITEMS_PER_PAGE)
    return render_template(
        'authors_chooser.html',
        prefix=prefix,
        authors_pager=authors_pager
    )


def _get_fb2_file_by_id(book_id):
    lib_path = current_app.config['PATH_TO_LIBRARY']
    zips = [f for f in listdir(lib_path) if f.endswith('.zip')]
    ranges = []
    for zip_file in zips:
        parts = zip_file.split('-')
        try:
            ranges.append([int(parts[1]), int(parts[2][:-4])])
        except ValueError:
            pass
    curr_zip = None
    for range_, zip_file in zip(ranges, zips):
        if range_[0] <= book_id <= range_[1]:
            curr_zip = zip_file
            break
    if curr_zip is None:
        return None

    filename = '%s.fb2' % book_id
    fb2_file = None
    with ZipFile(path.join(lib_path, curr_zip), 'r') as zip_file:
        fb2_file = zip_file.open(filename)
    return fb2_file


@main.route('/get_fb2/b-<int:book_id>')
def get_fb2(book_id):
    fb2_file = _get_fb2_file_by_id(book_id)
    if not fb2_file:
        abort(404)
    book = Book.query.get(book_id)
    if not book:
        abort(404)
    filename = '%s.fb2' % unidecode(book.title)
    return send_file(fb2_file, as_attachment=True,
                     attachment_filename=filename,
                     mimetype='text/xml',
                     add_etags=False)


@main.route('/get_prc/b-<int:book_id>')
def get_prc(book_id):
    return "prc"


@main.route('/get_epub/b-<int:book_id>')
def get_epub(book_id):
    fb2_file = _get_fb2_file_by_id(book_id)
    if not fb2_file:
        abort(404)
    epub_file = fb2_2_epub(fb2_file, str(book_id))
    book = Book.query.get(book_id)
    if not book:
        abort(404)
    filename = '%s.epub' % unidecode(book.title)
    return send_file(epub_file, as_attachment=True,
                     attachment_filename=filename,
                     add_etags=False)


@main.route('/images/b-<int:book_id>.<string:ext>')
def images(book_id, ext):
    ext = '.' + ext
    filepath = get_image_filepath(current_app.config['IMAGE_ROOT_DIR'], book_id, ext=ext)
    mimetype = mimetypes.types_map[ext]
    if not path.exists(filepath):
        abort(404)
    return send_file(filepath, mimetype=mimetype)
