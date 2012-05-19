from flask import request, render_template, g

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
    return render_template("book_info.html", book=book)


@app.route("/a/<int:author_id>")
def author_books(author_id):
    with Database() as db:
        books = db.get_books_by_author(author_id)
    res = ""
    return render_template("books_list.html", books=books)


@app.route("/search", defaults={'page': 1})
@app.route("/search/<int:page>")
def search_results(page):
    search_type = request.args.get('type', 'all')
    if search_type not in ('all', 'authors', 'books'):
        search_type = 'all'
    if search_type == 'authors':
        with Database() as db:
            authors = [db.get_author_by_id(1), db.get_author_by_id(1)]
            return render_template('authors_list.html', authors=authors)
    return request.args.get('term', '')

@app.route("/get_fb2/<int:book_id>")
def get_fb2(book_id):
    return "fb2"

@app.route("/get_fb2/<int:book_id>")
def get_prc(book_id):
    return "fb2"
