import sqlite3
from flask import Flask, request, render_template, g
from db.models import Book, Author
from db import get_book_by_id, get_books_by_author

app = Flask(__name__)
app.config.from_object('config')

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route("/")
def main_page():
    return render_template("main_page.html", name="asdf")


@app.route("/b/<int:book_id>")
def book_info(book_id):
    book = get_book_by_id(book_id)
    return "id=" + str(book.book_id) + " title=" + str(book.title)


@app.route("/a/<int:author_id>")
def author_books(author_id):
    books = get_books_by_author(author_id)
    res = ""
    return render_template("books_list.html", books=books)


@app.route("/search/<int:page>")
def search_results(page):
    return request.args.get('term', '')


if __name__ == "__main__":
    app.run()
