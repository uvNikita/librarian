from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def main_page():
    return "hello from main page."


@app.route("/b/<int:book_id>")
def book_info(book_id):
    return str(book_id)


@app.route("/a/<int:author_id>")
def author_books(author_id):
    return str(author_id)


@app.route("/search/<int:page>")
def search_results(page):
    return request.args.get('term', '')


if __name__ == "__main__":
    app.run()
