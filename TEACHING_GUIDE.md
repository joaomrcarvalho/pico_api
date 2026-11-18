# Teaching guide: what is an API?

This guide goes with the Library API project. It has the explanation, a lesson plan of about
60 minutes, questions for the class and exercises. Setup instructions are in the
[README](README.md).

---

## 1. The big idea

> An **API** (Application Programming Interface) is an agreed way for one program to ask
> another program for data, or to do something, **without knowing how the other program works
> inside**.

The key word is *interface*. An API says **what** you can ask for and **what** you will get
back. The **how** stays hidden.

Students already use APIs without calling them that:

| Something they know | Why it's an API |
|---|---|
| `len("hello")` | They know what to give it and what comes back, but not how Python counts. |
| `random.randint(1, 6)` | Same idea: a promise about inputs and outputs. |
| A weather app | The app asks a weather service on the internet for the forecast, through a **web API**. |
| "Sign in with Google" | The website asks Google's API who you are. |

This lesson is about **web APIs**: APIs that programs use over a network, with HTTP, the same
protocol a browser uses to load web pages.

## 2. An analogy: the restaurant

| In a restaurant | In our project |
|---|---|
| You, the customer | The **client**: a browser, `client.py`, the web page |
| The menu | The list of **endpoints** (`GET /api`) |
| Your order: "the soup, please" | A **request**: `GET /api/books/1` |
| The waiter | **The API**: `app.py` |
| The kitchen and the pantry | `database.py` and `library.db` |
| Your dish | The **response**: JSON data and a status code |
| "Sorry, we don't have that" | `404 Not Found` |
| "I don't understand your order" | `400 Bad Request` |

Two things to stress:

- Customers never walk into the kitchen. **Clients never touch the database.**
- The kitchen can change its recipes, its cooks or its ovens. As long as the menu stays the
  same, customers don't notice. **That's why APIs make programs easier to change.**

## 3. Vocabulary

| Word | Meaning | Example |
|---|---|---|
| **Client** | The program that asks | `client.py`, a browser |
| **Server** | The program that waits for requests and answers them | `app.py` |
| **Request** | A question: a method, a URL and sometimes some data | `GET /api/books/1` |
| **Endpoint** | One URL that the API offers | `/api/books` |
| **Method** | The kind of action we want | `GET`, `POST`, `PUT`, `DELETE` |
| **Query parameter** | Options added to the URL after a `?` | `?author=orwell` |
| **Response** | The answer: a status code and some data | `200 OK` and a book |
| **Status code** | A number that says how it went | `200`, `201`, `400`, `404` |
| **JSON** | The text format used for the data | `{"title": "1984"}` |

**Status codes:** the first digit is what matters.

- `2xx`: it worked (`200 OK`, `201 Created`)
- `4xx`: the client made a mistake (`400 Bad Request`, `404 Not Found`, `405 Method Not Allowed`)
- `5xx`: the server broke (`500 Internal Server Error`)

(Fun fact for the class: `418 I'm a teapot` exists. It started as an April Fools' joke.)

**JSON** looks almost exactly like Python lists and dictionaries. The differences: JSON writes
`true`, `false` and `null` instead of `True`, `False` and `None`, and it only uses double quotes.

## 4. How the project is built

```
     CLIENTS                   WEB API                  DATA LAYER               DATABASE
+---------------+          +--------------+          +---------------+        +-------------+
| your browser  | request  |              |   call   |               | query  |             |
| client.py     | -------> |    app.py    | -------> |  database.py  | -----> | library.db  |
| the web page  | <------- |   (Flask)    | <------- |               | <----- |  (SQLite)   |
+---------------+ response +--------------+  result  +---------------+  rows  +-------------+
                HTTP + JSON                  Python                      SQL
```

**There are two APIs in this project.** The web API is the obvious one: `app.py` offers
endpoints to clients over HTTP. But `database.py` is an API too. Its functions
(`select_books()`, `insert_book()` and so on) are the interface that `app.py` uses to reach the
data, and `app.py` doesn't contain a single line of SQL. It's the same idea at a smaller scale.

**One action, three languages:**

| Action (CRUD) | HTTP method in `app.py` | SQL in `database.py` |
|---|---|---|
| **C**reate | `POST` | `INSERT` |
| **R**ead | `GET` | `SELECT` |
| **U**pdate | `PUT` | `UPDATE` |
| **D**elete | `DELETE` | `DELETE` |

**The life of one request**, `GET /api/books/1`:

1. The browser sends `GET /api/books/1` to the server.
2. Flask finds the function marked `@app.get("/api/books/<int:book_id>")` and calls
   `get_book(1)`.
3. `get_book` calls `database.select_book(1)`, which runs
   `SELECT * FROM books WHERE id = ?`.
4. SQLite returns the row. `to_dict()` turns it into a Python dictionary, and turns the `1`
   in the `available` column into `True`.
5. `jsonify()` turns the dictionary into JSON text, and Flask sends it back with the status
   code `200`.

## 5. Lesson plan (about 60 minutes)

**Before class:** install the packages, run `python database.py` to start from clean data, and
check that `python app.py` starts. On the projector, put the terminal and the browser side by
side.

### Step 1: the idea (10 min)

- Ask: "How does a weather app know tomorrow's weather?" Lead them to: it asks another program.
- Give the definition and the restaurant analogy.
- Show that `len()` is an API too: you use it every day without knowing how it works inside.

### Step 2: meet the API (5 min)

- Run `python app.py`. Point out that the program doesn't end: it waits for requests. That's
  what a server does.
- Open <http://localhost:8000/api>: "This is the menu."
- `localhost` (or `127.0.0.1`) means "this computer". `8000` is the *port*, like a door number
  that the server listens on.

### Step 3: ask for data with the browser (10 min)

Open these one at a time:

- `/api/books`: JSON. Ask: "What would this be in Python?" (A list of dictionaries.)
- `/api/books/1`: one book.
- `/api/books?author=orwell` and `/api/books?genre=fantasy`: query parameters.
- `/api/books/999`: a `404`. Errors are answers too.

Each time, point at the server terminal: a new line appears with the method, the URL and the
status code. Then ask: "How could we *add* a book? The address bar can only send `GET`
requests…" That's why we need a program.

### Step 4: a Python client (10 min)

Run `python client.py` in a second terminal and press Enter to go through it step by step.

- Step 1: `response.json()` gives back a normal Python list, so we can loop over it.
- Step 4: `POST` answers `201 Created`, and the server tells us the new `id`.
- Steps 5 and 6: `PUT` changes the book, `DELETE` removes it.
- Step 7: the program checks `response.status_code == 404`. Status codes are for programs,
  messages are for humans.
- Step 8: the API refuses bad data with `400`. The API protects the database.

Stress that `client.py` and `app.py` share no code. They only exchange HTTP and JSON, so the
client could be written in any language.

### Step 5: a different client, the same API (5 min)

- Open <http://localhost:8000>. Add a book, borrow one, delete one.
- Point at the **API log** on the page (or open F12, then the Network tab): the page sends the
  same requests that `client.py` sent.
- Try to add a book with an empty title: the page shows the API's error message. The page
  doesn't check anything itself.
- "A phone app would do exactly this. Most apps you use are a screen that talks to an API."

### Step 6: look inside (15 min)

- Open `app.py` and read one endpoint together: the decorator (method + URL), the function,
  the call to `database.py`, and the `return jsonify(...)` with a status code.
- Follow `GET /api/books/1` from start to finish (see section 4).
- Open `database.py` and look at the SQL. Point out the `?` placeholders.
- Optional: open `library.db` in DB Browser for SQLite. `available` is stored as `1` or `0`,
  but the API shows `true` or `false`. Clients see the API, not the database.
- Live coding: add a tiny endpoint together, then save the file. The server restarts by itself.

  ```python
  @app.get("/api/hello")
  def hello():
      return jsonify({"message": "Hello, class!"}), 200
  ```

  Then open <http://localhost:8000/api/hello>.

### Step 7: wrap-up (5 min)

- An API is a contract between programs: what you can ask for, how to ask, and what you get
  back.
- A web API is that contract over HTTP: a method and a URL go in, a status code and JSON come
  out.
- Hand out the exercises.

## 6. Questions to ask the class

**Why doesn't the web page just open `library.db` itself?**
In real life the database is on another computer, and you don't want every app (or every user)
to reach it directly. The API is the only door: it checks the data, decides what is allowed and
hides the details.

**If we renamed the `author` column in the database, which files would have to change?**
Only `database.py`. `app.py`, `client.py` and the web page keep working, because the API, the
contract, didn't change. That's the whole point of an interface.

**Why does the API answer `404` and not just a message like "not found"?**
A program can check a number easily (`if response.status_code == 404:`), and every HTTP client,
in every language, understands the same codes. Messages are for humans.

**Why JSON?**
It's plain text, people can read it, and every programming language can read and write it.

**Is `len()` an API? Is `database.py`?**
Yes, and yes. An API doesn't have to be on the web.

**Why does `database.py` put `?` in the SQL instead of building it with an f-string?**
If text typed by a user goes straight into the SQL, someone can type SQL code instead of a name
and run it on your database. That's called *SQL injection* (xkcd #327, "Exploits of a Mom", is
the classic joke about it). With `?`, sqlite3 always treats the values as data, never as code.

## 7. Exercises

### Warm-up: use the API (don't change `app.py`)

1. Using only the browser, find all the Science Fiction books. Then find all the books whose
   author's name contains "an".
2. Write `my_client.py` that prints the titles of the books that are available.
   *Hint: `requests.get(...)`, `.json()`, a `for` loop and an `if`.*
3. Ask the user for an author with `input()` and print that author's books, or
   "No books found".
4. Add three of your favourite books with a Python script (`requests.post`). Check that they
   appear on the web page.
5. Count how many books there are of each genre, using only data from the API.
   *Hint: a dictionary.*

### Main: change the API

6. Add the filter `?available=true` / `?available=false` to `GET /api/books`.
   *Careful: query parameters are always text: `"true"`, not `True`.*
7. Add `GET /api/stats`, which answers something like
   `{"total": 14, "available": 11, "borrowed": 3}`.
8. Add `GET /api/genres`, which answers the list of genres, without repeats, in alphabetical
   order. *Hint: `SELECT DISTINCT`.*
9. Add an optional `pages` field to the books (the database table, `to_dict()`,
   `check_book()`, `insert_book()` and `update_book()`). Run `client.py` afterwards: does it
   still work? Why? *(Adding an optional field doesn't break the clients that don't use it.)*

### Challenge

10. Add `PATCH /api/books/<id>`, which changes only the fields that are sent, for example
    `{"available": false}`.
11. Add `POST /api/books/<id>/borrow` and `POST /api/books/<id>/return`. Borrowing a book that
    is already borrowed should answer `409 Conflict`.
12. Add sorting and pages: `?sort=year` and `?limit=5&offset=10`.
    *Careful: `?` placeholders can't be used for column names, so only accept column names
    from a fixed list.*
13. Move the authors to their own table and add `GET /api/authors` and
    `GET /api/authors/<id>/books`.

## 8. Bonus: one API for the whole class

If everyone is on the same network, the students can use **your** API from their own laptops:

1. In `app.py`, change the last line to `app.run(host="0.0.0.0", port=PORT)`. Leave out
   `debug=True`: the debugger must never be reachable from other computers.
2. Find your computer's IP address, for example `192.168.1.23`: run `ipconfig` on Windows,
   look in System Settings → Wi-Fi → Details on macOS, or run `hostname -I` on Linux. If the
   firewall asks, allow Python to accept connections.
3. The students set `API_URL = "http://192.168.1.23:8000/api"` in their own client and each
   send a `POST` with their favourite book.
4. Keep the web page open on the projector and click **Search** to refresh: the books appear
   as the requests arrive, and every request shows up in your terminal.

Some school networks block connections between devices. If nobody can connect, that's
probably why.
