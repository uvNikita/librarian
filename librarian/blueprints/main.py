# -*- coding: utf-8 -*-

from os import listdir, path, rename
from zipfile import ZipFile

from flask import Blueprint, current_app, request, render_template, abort
from flask import send_from_directory

from librarian.models import Book, Author


ITEMS_PER_PAGE = 100


main = Blueprint('main', __name__, template_folder='templates',
                 static_folder='static')


def books_sorted(query):
    return (
        query
        .order_by(Book.sequence_id)
        .order_by(Book.sequence_number)
    )


def authors_sorted(query):
    return (
        query
        .order_by(Author.last_name)
    )


@main.route("/")
def main_page():
    return render_template("main_page.html")


@main.route("/b/<int:book_id>")
def book_info(book_id):
    book = Book.query.filter_by(id=book_id).first()
    if not book:
         abort(404)
    return render_template("book_info.html", book=book)


@main.route("/s/<int:sequence_id>", defaults={'page': 1})
@main.route("/s/<int:sequence_id>/p<int:page>")
def sequence_books(sequence_id, page):
    books = books_sorted(Book.query.filter_by(sequence_id=sequence_id))
    if not books:
        abort(404)
    books_pager = books.paginate(page, ITEMS_PER_PAGE)
    return render_template("sequence_books.html", books_pager=books_pager)


@main.route("/a/<int:author_id>", defaults={'page': 1})
@main.route("/a/<int:author_id>/p<int:page>")
def author_books(author_id, page):
    author = Author.query.filter_by(id=author_id).first()
    if not author:
        abort(404)
    books_pager = books_sorted(author.books).paginate(page, ITEMS_PER_PAGE)
    return render_template("books_list.html", author=author, books_pager=books_pager)


@main.route("/search", defaults={'page': 1})
@main.route("/search/p<int:page>")
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


@main.route("/authors", defaults={'page': 1})
@main.route("/authors/p<int:page>")
def authors_chooser(page):
    first_letter = request.args.get('first_letter')
    second_letter = request.args.get('second_letter')
    authors_pager = None
    if first_letter and second_letter:
        prefix = first_letter + second_letter
        authors = authors_sorted(Author.search_starting_from(prefix))
        authors_pager = authors.paginate(page, ITEMS_PER_PAGE)
    return render_template(
        'authors_chooser.html',
        first_letter=first_letter,
        second_letter=second_letter,
        authors_pager=authors_pager
    )


@main.route("/get_fb2/<int:book_id>")
def get_fb2(book_id):
    lib_path = current_app.config['PATH_TO_LIBRARY']
    tmp_folder = current_app.config['TEMPORARY_FOLDER']
    zips = [f for f in listdir(lib_path) if f.endswith('.zip')]
    ranges = [zip_file.split('-') for zip_file in zips]
    ranges = [[int(r[1]), int(r[2][:-4])] for r in ranges]
    curr_zip = None
    for range, zip_file in zip(ranges, zips):
        if range[0] <= book_id <= range[1]:
            curr_zip = zip_file
            break
    if not curr_zip:
        abort(404)

    filename = '%s.fb2' % book_id
    with ZipFile(path.join(lib_path, curr_zip), 'r') as zip_file:
        zip_file.extract(filename, tmp_folder)
    title = Book.query.filter_by(id=book_id).first().title
    new_filename = (u'%s.fb2' % title).encode('utf-8')
    new_filename = new_filename
    rename(path.join(tmp_folder, filename), path.join(tmp_folder, new_filename))
    return send_from_directory(tmp_folder, new_filename, as_attachment=True)


@main.route("/get_prc/<int:book_id>")
def get_prc(book_id):
    return "prc"
