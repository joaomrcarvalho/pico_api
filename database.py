"""
database.py - everything that talks to the SQLite database lives here.

The web API (app.py) never writes SQL itself. It calls the functions in
this file instead, so each file has one job:

    app.py       talks to the clients  (HTTP requests and JSON)
    database.py  talks to the data     (SQL and the library.db file)

Notice that these functions are an API too! app.py knows WHAT each
function does (its name, what to give it and what it returns), but not
HOW it does it. We could switch to a different database tomorrow, and
app.py would not need to change at all.

Run this file directly to create the database, or to reset it to the
sample books after a demo:

    python database.py
"""

import sqlite3
from contextlib import closing
from pathlib import Path

# A SQLite database is just one file. We keep it next to this script.
DATABASE_FILE = Path(__file__).parent / "library.db"

# The books we start with: (title, author, year, genre, available)
SAMPLE_BOOKS = [
    ("1984", "George Orwell", 1949, "Dystopia", True),
    ("Animal Farm", "George Orwell", 1945, "Dystopia", False),
    ("Pride and Prejudice", "Jane Austen", 1813, "Romance", True),
    ("The Hobbit", "J.R.R. Tolkien", 1937, "Fantasy", True),
    ("The Lion, the Witch and the Wardrobe", "C.S. Lewis", 1950, "Fantasy", False),
    ("Dune", "Frank Herbert", 1965, "Science Fiction", True),
    ("The Hitchhiker's Guide to the Galaxy", "Douglas Adams", 1979, "Science Fiction", True),
    ("Frankenstein", "Mary Shelley", 1818, "Science Fiction", True),
    ("Murder on the Orient Express", "Agatha Christie", 1934, "Mystery", True),
    ("Blindness", "José Saramago", 1995, "Fiction", True),
    ("One Hundred Years of Solitude", "Gabriel García Márquez", 1967, "Fiction", False),
    ("The Little Prince", "Antoine de Saint-Exupéry", 1943, "Fiction", True),
    ("The Pragmatic Programmer", "Andrew Hunt and David Thomas", 1999, "Programming", True),
    ("Automate the Boring Stuff with Python", "Al Sweigart", 2015, "Programming", True),
]


def connect():
    """Open the database file.

    Use it in a `with` block, the same way you use `with open(...)` for
    files. The connection is closed for you when the block ends:

        with connect() as db:
            db.execute("SELECT ...")
    """
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row  # lets us write row["title"] instead of row[1]
    return closing(connection)


def create_database():
    """Create the books table (deleting the old one, if any) and add the sample books."""
    with connect() as db:
        db.execute("DROP TABLE IF EXISTS books")
        db.execute("""
            CREATE TABLE books (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,  -- the database chooses the id
                title     TEXT    NOT NULL,
                author    TEXT    NOT NULL,
                year      INTEGER NOT NULL,
                genre     TEXT,                               -- optional: can be NULL
                available INTEGER NOT NULL DEFAULT 1          -- 1 = on the shelf, 0 = borrowed
            )
        """)
        db.executemany(
            "INSERT INTO books (title, author, year, genre, available) VALUES (?, ?, ?, ?, ?)",
            SAMPLE_BOOKS,
        )
        db.commit()  # "commit" = save the changes in the file


def to_dict(row):
    """Turn one row from the database into a normal Python dictionary.

    The database stores `available` as 1 or 0. For the people who use our
    API, true/false is much clearer, so we translate it here.
    """
    return {
        "id": row["id"],
        "title": row["title"],
        "author": row["author"],
        "year": row["year"],
        "genre": row["genre"],
        "available": bool(row["available"]),  # 1 -> True, 0 -> False
    }


def select_books(author=None, genre=None):
    """Return a list with all the books, optionally filtered.

    author: keep the books whose author CONTAINS this text ("orwell" finds "George Orwell")
    genre:  keep the books with exactly this genre          ("fantasy" finds "Fantasy")
    Upper and lower case don't matter in either of them.
    """
    sql = "SELECT * FROM books"
    conditions = []
    values = []

    # The ? marks are placeholders: sqlite3 puts the values in their place, safely.
    # Never paste text that came from a user straight into an SQL string!
    # (Look up "SQL injection" to see why.)
    if author:
        conditions.append("author LIKE ?")
        values.append(f"%{author}%")  # in LIKE, % means "anything": %orwell% = "contains orwell"
    if genre:
        conditions.append("LOWER(genre) = LOWER(?)")
        values.append(genre)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY id"

    with connect() as db:
        rows = db.execute(sql, values).fetchall()
    return [to_dict(row) for row in rows]


def select_book(book_id):
    """Return the book with this id as a dictionary, or None if it doesn't exist."""
    with connect() as db:
        # (book_id,) is a tuple with a single value - the comma is needed!
        row = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if row is None:
        return None
    return to_dict(row)


def insert_book(title, author, year, genre=None, available=True):
    """Add a new book and return the id that the database gave it."""
    with connect() as db:
        cursor = db.execute(
            "INSERT INTO books (title, author, year, genre, available) VALUES (?, ?, ?, ?, ?)",
            (title, author, year, genre, int(available)),  # int(True) = 1, int(False) = 0
        )
        db.commit()
        return cursor.lastrowid  # the id of the row we just added


def update_book(book_id, title, author, year, genre=None, available=True):
    """Replace all the data of the book with this id."""
    with connect() as db:
        db.execute(
            "UPDATE books SET title = ?, author = ?, year = ?, genre = ?, available = ? WHERE id = ?",
            (title, author, year, genre, int(available), book_id),
        )
        db.commit()


def delete_book(book_id):
    """Delete the book with this id."""
    with connect() as db:
        db.execute("DELETE FROM books WHERE id = ?", (book_id,))
        db.commit()


# This part only runs when you start this file directly (python database.py),
# not when app.py imports it.
if __name__ == "__main__":
    create_database()
    print(f"Done! {DATABASE_FILE.name} now has {len(SAMPLE_BOOKS)} books.")
