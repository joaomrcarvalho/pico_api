"""
client.py - a Python program that USES the Library API.

    app.py    is the SERVER: it waits for requests and answers them.
    client.py is a CLIENT:   it sends requests and uses the answers.

The two programs share no code and no variables. They only exchange
HTTP requests and JSON data - and that is exactly what an API is for.

How to run it:
    1. In one terminal, start the server:     python app.py
    2. In a second terminal, run this client: python client.py

The demo stops after each step so you can talk about it.
To run all the steps without stopping:  python client.py --no-pause
"""

import json
import sys

import requests  # the most popular Python library for sending HTTP requests

# Where the API lives. 127.0.0.1 means "this computer" (it's the same as "localhost").
API_URL = "http://127.0.0.1:8000/api"

PAUSE = "--no-pause" not in sys.argv


def step(title):
    """Wait for Enter, then print the title of the next step."""
    if PAUSE:
        input("\nPress Enter to continue...")
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def show(response, show_data=True):
    """Print the request we sent and the response the server sent back."""
    sent = response.request
    print(f"-> Request:  {sent.method} {sent.url}")
    if sent.body:
        print(f"             with the data {sent.body.decode()}")
    print(f"<- Response: {response.status_code} {response.reason}")
    if show_data:
        # response.json() turns the JSON text into Python lists and dictionaries.
        # json.dumps(..., indent=2) turns them back into text, nicely indented.
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))


# Before we start, check that the server is running.
try:
    requests.get(API_URL)
except requests.exceptions.ConnectionError:
    print(f"Could not connect to {API_URL}")
    print("Is the server running? Start it in another terminal with:  python app.py")
    sys.exit(1)

print("This demo talks to the Library API, one request at a time.")


# -----------------------------------------------------------------------------
step("Step 1: GET /api/books  ->  ask for all the books")

response = requests.get(f"{API_URL}/books")
show(response, show_data=False)

books = response.json()  # JSON text -> a normal Python list of dictionaries!
print(f"\nWe got a list of {len(books)} books. It's a normal Python list, so we can loop over it:\n")
for book in books:
    status = "available" if book["available"] else "borrowed"
    print(f"  {book['id']:>2}. {book['title']} - {book['author']} ({book['year']}) [{status}]")


# -----------------------------------------------------------------------------
step("Step 2: GET /api/books?author=orwell  ->  only some books (a 'query parameter')")

response = requests.get(f"{API_URL}/books", params={"author": "orwell"})
show(response)


# -----------------------------------------------------------------------------
step("Step 3: GET /api/books/1  ->  one book, chosen by its id")

response = requests.get(f"{API_URL}/books/1")
show(response)


# -----------------------------------------------------------------------------
step("Step 4: POST /api/books  ->  add a NEW book")

new_book = {
    "title": "The Martian",
    "author": "Andy Weir",
    "year": 2011,
    "genre": "Science Fiction",
}
response = requests.post(f"{API_URL}/books", json=new_book)
show(response)

book_id = response.json()["id"]  # the server tells us which id it gave the new book
print(f"\nThe server saved our book and gave it the id {book_id}.")


# -----------------------------------------------------------------------------
step(f"Step 5: PUT /api/books/{book_id}  ->  change the book (someone borrowed it)")

new_book["available"] = False
response = requests.put(f"{API_URL}/books/{book_id}", json=new_book)
show(response)


# -----------------------------------------------------------------------------
step(f"Step 6: DELETE /api/books/{book_id}  ->  remove the book")

response = requests.delete(f"{API_URL}/books/{book_id}")
show(response)


# -----------------------------------------------------------------------------
step(f"Step 7: GET /api/books/{book_id} again  ->  the book is gone")

response = requests.get(f"{API_URL}/books/{book_id}")
show(response)

# The status code tells our program what happened, so it can react to it:
if response.status_code == 404:
    print("\nOur program checked the status code: 404 means that book doesn't exist anymore.")


# -----------------------------------------------------------------------------
step("Step 8: POST /api/books with BAD data  ->  the API protects the database")

response = requests.post(f"{API_URL}/books", json={"title": "A Book With No Author", "year": 2020})
show(response)
print()
response = requests.post(f"{API_URL}/books", json={"title": "My Autobiography", "author": "Future Me", "year": 2999})
show(response)


print("\n" + "=" * 72)
print("Done! This program never opened the database. It only sent HTTP requests")
print("and read the JSON answers. Any other program that speaks HTTP - a website,")
print("a phone app, a game - can use the Library API in exactly the same way.")
