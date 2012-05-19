from flask import request, render_template, g, abort

from librarian import app

from librarian.models import Book, Author
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
    if search_type not in ('all', 'authors', 'books'):
        search_type = 'all'
    if search_type == 'authors':
        with Database() as db:
            authors = [db.get_author_by_id(1), db.get_author_by_id(1)]
            return render_template('authors_list.html', authors=authors, search_term=search_term)
    return search_term


@app.route("/get_fb2/<int:book_id>")
def get_fb2(book_id):
    return "fb2"


@app.route("/get_fb2/<int:book_id>")
def get_prc(book_id):
    return "fb2"
