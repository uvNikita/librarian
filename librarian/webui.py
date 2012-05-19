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
    return request.args.get('term', '')
