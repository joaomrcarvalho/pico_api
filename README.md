# 📚 Library API: a first web API in Python

A small, complete example for learning **what an API is**:

- a **web API** written in Python with [Flask](https://flask.palletsprojects.com/),
- that keeps its books in a **SQLite database** (`library.db`),
- and **two different clients** that use it: a Python script and a web page.

```
browser / client.py / web page  --HTTP + JSON-->  app.py  --Python-->  database.py  --SQL-->  library.db
```

> **Teachers:** [TEACHING_GUIDE.md](TEACHING_GUIDE.md) explains APIs step by step and
> has a 60-minute lesson plan, questions for the class and exercises.

## What's inside

| File | What it is |
|---|---|
| `app.py` | **The API.** A small web server with one function per endpoint. |
| `database.py` | Everything that talks to the database. All the SQL is here. |
| `library.db` | The SQLite database, with 14 sample books. |
| `client.py` | A Python program that *uses* the API, step by step. |
| `static/index.html` | A web page that uses the *same* API. |
| `test_app.py` | Automated tests for the API (optional). |
| `requirements.txt` | The Python packages you need. |

## Getting started

You need **Python 3.10 or newer**.

**1. Install the packages.** It's best to use a virtual environment.

On macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows:

```bat
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**2. Start the API.** Leave this terminal open: this program is the *server*.

```bash
python app.py
```

**3. Use it.** Every request the server receives is printed in that terminal.

| Client | How |
|---|---|
| Your browser | Open <http://localhost:8000/api> and <http://localhost:8000/api/books> |
| The Python client | In a **second** terminal (with the virtual environment active): `python client.py` |
| The web page | Open <http://localhost:8000> |

## The API

| Method | URL | What it does | Status codes |
|---|---|---|---|
| `GET` | `/api` | Lists the endpoints (the "menu") | `200` |
| `GET` | `/api/books` | Lists all the books | `200` |
| `GET` | `/api/books?author=orwell&genre=dystopia` | Filters by author (contains the text) and/or genre (exact) | `200` |
| `GET` | `/api/books/1` | Gets one book | `200`, `404` |
| `POST` | `/api/books` | Adds the book sent as JSON | `201`, `400` |
| `PUT` | `/api/books/1` | Replaces the data of a book with the JSON sent | `200`, `400`, `404` |
| `DELETE` | `/api/books/1` | Deletes a book | `200`, `404` |

A book, in JSON:

```json
{
  "id": 1,
  "title": "1984",
  "author": "George Orwell",
  "year": 1949,
  "genre": "Dystopia",
  "available": true
}
```

When you send a book (`POST` or `PUT`), `title`, `author` and `year` are required, and `genre`
and `available` are optional. The `id` is always chosen by the database. Errors are JSON too,
for example `{"error": "Missing required field: 'author'"}`.

### Trying it with curl (optional)

```bash
curl -i http://localhost:8000/api/books/1
curl "http://localhost:8000/api/books?genre=fantasy"
curl -i -X POST http://localhost:8000/api/books -H "Content-Type: application/json" \
     -d '{"title": "The Martian", "author": "Andy Weir", "year": 2011}'
curl -i -X DELETE http://localhost:8000/api/books/15
```

`-i` also shows the status code and the headers of the response. In the last command, use the
`id` you got back from the `POST`. These commands work on macOS, Linux and Git Bash. In Windows
PowerShell, type `curl.exe` instead of `curl`; the JSON quotes are tricky there, so `client.py`
is easier.

## Resetting the data

Demos change the data. To go back to the 14 original books, run this (the server can keep
running):

```bash
python database.py
```

## Looking inside the database

`library.db` is a normal SQLite file. Open it with a free tool like
[DB Browser for SQLite](https://sqlitebrowser.org/), or a SQLite extension for VS Code, to watch
the `books` table change while you use the API.

## Running the tests

```bash
pytest
```

## Troubleshooting

| Problem | What to do |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` (or `'requests'`) | Activate the virtual environment in that terminal, then `pip install -r requirements.txt`. |
| `client.py` says *Could not connect* | Start the server first (`python app.py`) in another terminal. |
| *Address already in use* | Another program is using port 8000. Change `PORT` in `app.py` and `API_URL` in `client.py`. (We don't use Flask's usual port 5000 because recent Macs use it for AirPlay.) |
| Windows PowerShell won't run `activate` | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once, or use Command Prompt. |
| `python` is not found on macOS | Use `python3`. |
| The data looks wrong after a demo | `python database.py` resets it. |
