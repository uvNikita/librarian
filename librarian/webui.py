from zipfile import ZipFile
from os import listdir, path

from flask import request, render_template, abort, send_from_directory

from librarian import app
from librarian.db import Database


@app.route("/")
def main_page():
    return render_template("main_page.html", name="asdf")


@app.route("/b/<int:book_id>")
def book_info(book_id):
    with Database() as db:
        book = db.get_book_by_id(book_id)
        if not book:
             abort(404)
    return render_template("book_info.html", book=book)


@app.route("/s/<int:sequence_id>")
def sequence_books(sequence_id):
    with Database() as db:
        books = db.get_sequence_books(sequence_id)
        if not books:
            abort(404)
    return render_template("sequence_books.html", books=books)


@app.route("/a/<int:author_id>")
def author_books(author_id):
    with Database() as db:
        author = db.get_author_by_id(author_id)
        if not author:
            abort(404)
        books = db.get_books_by_author(author_id)
    return render_template("books_list.html", books=books, author=author)


@app.route("/search", defaults={'page': 1})
@app.route("/search/<int:page>")
def search_results(page):
    search_type = request.args.get('type', 'all')
    search_term = request.args.get('term', '')
    curr_author_id = request.args.get('curr_author_id')
    if search_type not in ('all', 'authors', 'books'):
        search_type = 'all'
    if search_type == 'authors':
        with Database() as db:
            authors = [db.get_author_by_id(1), db.get_author_by_id(1)]
            return render_template('authors_list.html', authors=authors, search_term=search_term, search_type=search_type)
    if search_type == 'books':
        with Database() as db:
            books = db.search_by_title(search_term, author_id=curr_author_id)
            return render_template('books_search_result.html', books=books, search_term=search_term, search_type=search_type)
    return search_term


@app.route("/authors/")
def authors():
    first_letter = request.args.get('first_letter')
    second_letter = request.args.get('second_letter')
    authors = None
    if first_letter and second_letter:
        with Database() as db:
            authors = db.search_authors_starting_from(first_letter + second_letter)
    return render_template('authors_chooser.html', first_letter=first_letter, second_letter=second_letter, authors=authors)


@app.route("/get_fb2/<int:book_id>")
def get_fb2(book_id):
    lib_path = app.config['PATH_TO_LIBRARY']
    tmp_folder = app.config['TEMPORARY_FOLDER']
    zips = [f for f in listdir(lib_path) if f.endswith('.zip')]
    ranges = [zip.split('-') for zip in zips]
    ranges = [[int(r[1]), int(r[2][:-4])] for r in ranges]
    i = 0
    found = ranges[i][0] <= book_id <= ranges[i][1]
    while not found:
        i += 1
        found = ranges[i][0] <= book_id <= ranges[i][1]
    curr_zip = zips[i]

    filename = '{name}.fb2'.format(name=book_id)
    with ZipFile(path.join(lib_path, curr_zip), 'r') as zip_file:
        zip_file.extract(filename, tmp_folder)
    return send_from_directory(tmp_folder, filename, as_attachment=True)


@app.route("/get_fb2/<int:book_id>")
def get_prc(book_id):
    return "fb2"
