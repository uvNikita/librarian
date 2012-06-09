from zipfile import ZipFile
from os import listdir, path

from flask import request, render_template, abort, send_from_directory

from librarian import app
from librarian.models import Book, Author


@app.route("/")
def main_page():
    return render_template("main_page.html")


@app.route("/b/<int:book_id>")
def book_info(book_id):
    book = Book.query.filter_by(id=book_id).first()
    if not book:
         abort(404)
    return render_template("book_info.html", book=book)


@app.route("/s/<int:sequence_id>")
def sequence_books(sequence_id):
    books = Book.query.filter_by(sequence_id=sequence_id)
    if not books:
        abort(404)
    return render_template("sequence_books.html", books=books)


@app.route("/a/<int:author_id>")
def author_books(author_id):
    author = Author.query.filter_by(id=author_id).first()
    if not author:
        abort(404)
    return render_template("books_list.html", author=author)


@app.route("/search", defaults={'page': 1})
@app.route("/search/<int:page>")
def search_results(page):
    search_type = request.args.get('type', 'all')
    search_term = request.args.get('term', '')
    curr_author_id = request.args.get('curr_author_id')
    if search_type not in ('all', 'authors', 'books'):
        search_type = 'all'
    if search_type == 'authors':
        authors = Author.query.limit(10)
        return render_template('authors_list.html', authors=authors, search_term=search_term, search_type=search_type)
    if search_type == 'books':
        books = Book.search_by_title(search_term)
        return render_template('books_search_result.html', books=books, search_term=search_term, search_type=search_type)
    return search_term


@app.route("/authors/")
def authors():
    first_letter = request.args.get('first_letter')
    second_letter = request.args.get('second_letter')
    authors = None
    if first_letter and second_letter:
        authors = Author.search_starting_from(first_letter + second_letter)
    return render_template('authors_chooser.html', first_letter=first_letter, second_letter=second_letter, authors=authors)


@app.route("/get_fb2/<int:book_id>")
def get_fb2(book_id):
    lib_path = app.config['PATH_TO_LIBRARY']
    tmp_folder = app.config['TEMPORARY_FOLDER']
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

    filename = '{name}.fb2'.format(name=book_id)
    with ZipFile(path.join(lib_path, curr_zip), 'r') as zip_file:
        zip_file.extract(filename, tmp_folder)
    return send_from_directory(tmp_folder, filename, as_attachment=True)


@app.route("/get_prc/<int:book_id>")
def get_prc(book_id):
    return "prc"
