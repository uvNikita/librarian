from flask import Flask, request
from db.models import Book, Author
from db import get_book_by_id

app = Flask(__name__)

@app.route("/")
def main_page():
    return "hello from main page."


@app.route("/b/<int:book_id>")
def book_info(book_id):
    book = get_book_by_id(book_id)
    return "id=" + str(book.book_id) + " title=" + str(book.title)


@app.route("/a/<int:author_id>")
def author_books(author_id):
    return str(author_id)


@app.route("/search/<int:page>")
def search_results(page):
    return request.args.get('term', '')


if __name__ == "__main__":
    app.run()
