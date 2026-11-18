"""
app.py - the Library API.

A small web API that lets other programs read and change a list of books.
It is written with Flask, a popular Python library for building web servers.

Start it with:

    python app.py

and then open http://localhost:8000/api in your browser.

What happens when a request arrives, for example  GET /api/books/3 :

    1. Flask looks at the METHOD (GET) and the URL (/api/books/3)
       and calls the function that matches them: get_book(3).
    2. That function asks database.py for the data.
    3. It sends back a RESPONSE: the data as JSON, plus a status code
       that says how it went (200 = OK, 404 = Not Found, ...).
"""

from datetime import date

from flask import Flask, jsonify, request

import database

PORT = 8000

app = Flask(__name__)
app.json.sort_keys = False     # keep the fields in the order we wrote them
app.json.ensure_ascii = False  # show letters like é and ç as they are
app.json.compact = False       # indent the JSON, so humans can read it too


# -----------------------------------------------------------------------------
# The "menu": a list of everything this API can do
# -----------------------------------------------------------------------------

@app.get("/api")
def menu():
    return jsonify({
        "name": "Library API",
        "endpoints": {
            "GET /api/books": "List all the books. Optional filters: ?author=...&genre=...",
            "GET /api/books/<id>": "Get one book",
            "POST /api/books": "Add a book (send it as JSON)",
            "PUT /api/books/<id>": "Replace the data of a book (send it as JSON)",
            "DELETE /api/books/<id>": "Delete a book",
        },
    }), 200


# -----------------------------------------------------------------------------
# READ - GET requests only ask for data. They never change anything.
# -----------------------------------------------------------------------------

@app.get("/api/books")
def list_books():
    # Query parameters are the optional part of the URL after the "?":
    #     /api/books?author=orwell&genre=dystopia
    # request.args.get() gives None when a parameter isn't there.
    author = request.args.get("author")
    genre = request.args.get("genre")

    books = database.select_books(author=author, genre=genre)
    return jsonify(books), 200  # 200 = OK


@app.get("/api/books/<int:book_id>")
def get_book(book_id):
    # <int:book_id> takes the number from the URL:  /api/books/3  ->  book_id = 3
    book = database.select_book(book_id)
    if book is None:
        return jsonify({"error": f"There is no book with id {book_id}"}), 404  # 404 = Not Found
    return jsonify(book), 200


# -----------------------------------------------------------------------------
# Checking the data that clients send us
# -----------------------------------------------------------------------------

def check_book(data):
    """Check a book sent by a client.

    Returns a message describing the first problem it finds,
    or None if the book is fine.

    Golden rule: an API must never trust the data it receives!
    """
    if not isinstance(data, dict):
        return 'Send the book as JSON, for example: {"title": "Dune", "author": "Frank Herbert", "year": 1965}'

    for field in ["title", "author", "year"]:
        if field not in data:
            return f"Missing required field: '{field}'"

    for field in ["title", "author"]:
        if not isinstance(data[field], str):
            return f"'{field}' must be text"
        if data[field].strip() == "":
            return f"'{field}' cannot be empty"

    if not isinstance(data["year"], int):
        return "'year' must be a whole number, like 1949"
    if data["year"] > date.today().year:
        return "'year' cannot be in the future"

    if data.get("genre") is not None and not isinstance(data["genre"], str):
        return "'genre' must be text"
    if "available" in data and not isinstance(data["available"], bool):
        return "'available' must be true or false"

    return None  # no problems found


# -----------------------------------------------------------------------------
# CREATE - POST sends a new book to the server
# -----------------------------------------------------------------------------

@app.post("/api/books")
def add_book():
    # The JSON the client sent, as a Python dictionary.
    # silent=True: if it isn't valid JSON, give us None instead of crashing.
    data = request.get_json(silent=True)

    problem = check_book(data)
    if problem:
        return jsonify({"error": problem}), 400  # 400 = Bad Request: the client sent bad data

    new_id = database.insert_book(
        title=data["title"].strip(),
        author=data["author"].strip(),
        year=data["year"],
        genre=data.get("genre"),
        available=data.get("available", True),  # if it's not sent, the book is available
    )
    return jsonify(database.select_book(new_id)), 201  # 201 = Created


# -----------------------------------------------------------------------------
# UPDATE - PUT replaces the data of a book that already exists
# -----------------------------------------------------------------------------

@app.put("/api/books/<int:book_id>")
def replace_book(book_id):
    if database.select_book(book_id) is None:
        return jsonify({"error": f"There is no book with id {book_id}"}), 404

    data = request.get_json(silent=True)
    problem = check_book(data)
    if problem:
        return jsonify({"error": problem}), 400

    # PUT means "here is the new version of the WHOLE book", so an optional
    # field that isn't sent goes back to its default value.
    database.update_book(
        book_id,
        title=data["title"].strip(),
        author=data["author"].strip(),
        year=data["year"],
        genre=data.get("genre"),
        available=data.get("available", True),
    )
    return jsonify(database.select_book(book_id)), 200


# -----------------------------------------------------------------------------
# DELETE - removes a book
# -----------------------------------------------------------------------------

@app.delete("/api/books/<int:book_id>")
def remove_book(book_id):
    book = database.select_book(book_id)
    if book is None:
        return jsonify({"error": f"There is no book with id {book_id}"}), 404

    database.delete_book(book_id)
    return jsonify({"message": f"Deleted book {book_id}: {book['title']}"}), 200


# -----------------------------------------------------------------------------
# Wrong URLs and wrong methods get a JSON answer too (instead of a web page)
# -----------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "This URL does not exist. See GET /api for the list of endpoints."}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "This URL does not accept that method. See GET /api for the list of endpoints."}), 405


# -----------------------------------------------------------------------------
# A web page that USES this API. It's just another client, like client.py.
# The page itself is in static/index.html.
# -----------------------------------------------------------------------------

@app.get("/")
def web_page():
    return app.send_static_file("index.html")


# -----------------------------------------------------------------------------
# Start the server
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    if not database.DATABASE_FILE.exists():
        database.create_database()

    # debug=True restarts the server by itself every time you save this file.
    app.run(port=PORT, debug=True)
