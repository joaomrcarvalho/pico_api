"""
test_app.py - automated tests for the Library API.

Run them with:

    pytest

Each test sends a request to the API and checks the answer. Flask's
"test client" sends the requests straight to app.py, so you don't need
to start the server first. The tests use a temporary database, so your
real library.db is never changed.
"""

import pytest

import database
from app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Give every test a fresh database and a client to send requests with."""
    monkeypatch.setattr(database, "DATABASE_FILE", tmp_path / "test.db")
    database.create_database()
    return app.test_client()


# --- Reading (GET) -------------------------------------------------------------

def test_list_all_books(client):
    response = client.get("/api/books")
    assert response.status_code == 200
    assert len(response.get_json()) == len(database.SAMPLE_BOOKS)


def test_filter_by_author(client):
    response = client.get("/api/books?author=ORWELL")  # upper/lower case doesn't matter
    titles = [book["title"] for book in response.get_json()]
    assert titles == ["1984", "Animal Farm"]


def test_filter_by_genre(client):
    response = client.get("/api/books?genre=fantasy")
    titles = [book["title"] for book in response.get_json()]
    assert titles == ["The Hobbit", "The Lion, the Witch and the Wardrobe"]


def test_get_one_book(client):
    response = client.get("/api/books/1")
    assert response.status_code == 200
    assert response.get_json() == {
        "id": 1,
        "title": "1984",
        "author": "George Orwell",
        "year": 1949,
        "genre": "Dystopia",
        "available": True,
    }


def test_get_a_book_that_does_not_exist(client):
    response = client.get("/api/books/999")
    assert response.status_code == 404
    assert "error" in response.get_json()


# --- Creating (POST) -----------------------------------------------------------

def test_add_book(client):
    response = client.post("/api/books", json={"title": "The Martian", "author": "Andy Weir", "year": 2011})
    assert response.status_code == 201
    book = response.get_json()
    assert book["title"] == "The Martian"
    assert book["available"] is True  # the default value
    # The new book is really saved: we can ask for it.
    assert client.get(f"/api/books/{book['id']}").status_code == 200


def test_add_book_with_a_missing_field(client):
    response = client.post("/api/books", json={"title": "No Author Here", "year": 2000})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing required field: 'author'"


def test_add_book_with_year_as_text(client):
    response = client.post("/api/books", json={"title": "Dune", "author": "Frank Herbert", "year": "1965"})
    assert response.status_code == 400


def test_add_book_from_the_future(client):
    response = client.post("/api/books", json={"title": "My Autobiography", "author": "Future Me", "year": 2999})
    assert response.status_code == 400


def test_add_book_without_json(client):
    response = client.post("/api/books", data="this is not JSON")
    assert response.status_code == 400


# --- Updating (PUT) ------------------------------------------------------------

def test_update_book(client):
    changed = {"title": "1984", "author": "George Orwell", "year": 1949, "genre": "Dystopia", "available": False}
    response = client.put("/api/books/1", json=changed)
    assert response.status_code == 200
    assert client.get("/api/books/1").get_json()["available"] is False


def test_update_a_book_that_does_not_exist(client):
    response = client.put("/api/books/999", json={"title": "X", "author": "Y", "year": 2000})
    assert response.status_code == 404


# --- Deleting (DELETE) ---------------------------------------------------------

def test_delete_book(client):
    response = client.delete("/api/books/1")
    assert response.status_code == 200
    assert client.get("/api/books/1").status_code == 404


def test_delete_a_book_that_does_not_exist(client):
    assert client.delete("/api/books/999").status_code == 404


# --- Wrong URLs and wrong methods ---------------------------------------------

def test_unknown_url(client):
    response = client.get("/api/unicorns")
    assert response.status_code == 404
    assert response.is_json


def test_wrong_method(client):
    response = client.delete("/api/books")  # you can't delete the whole list
    assert response.status_code == 405
    assert response.is_json


def test_web_page_is_served(client):
    with client.get("/") as response:  # "with" closes the page file when we're done
        assert response.status_code == 200
        assert b"Library API" in response.data
