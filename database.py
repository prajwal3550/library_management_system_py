"""
database.py - Database operations for the Library Management System
Handles all SQLite interactions.
"""
import sqlite3
import os
from datetime import datetime
from models import Book, Member, Transaction


DB_PATH = os.path.join(os.path.dirname(__file__), "database", "library.db")


def get_connection():
    """Return a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Create all tables if they don't exist and seed sample data."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS books (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            title     TEXT    NOT NULL,
            author    TEXT    NOT NULL,
            category  TEXT    NOT NULL,
            quantity  INTEGER NOT NULL DEFAULT 1,
            available INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS members (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id     INTEGER NOT NULL,
            member_id   INTEGER NOT NULL,
            issue_date  TEXT    NOT NULL,
            return_date TEXT,
            status      TEXT    NOT NULL DEFAULT 'issued',
            FOREIGN KEY (book_id)   REFERENCES books(id),
            FOREIGN KEY (member_id) REFERENCES members(id)
        );
    """)

    # Seed sample data only if tables are empty
    if cur.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 0:
        _seed_sample_data(cur)

    conn.commit()
    conn.close()


def _seed_sample_data(cur):
    """Insert sample books and members."""
    books = [
        ("The Great Gatsby",          "F. Scott Fitzgerald", "Fiction",    5, 5),
        ("To Kill a Mockingbird",     "Harper Lee",          "Fiction",    4, 4),
        ("1984",                      "George Orwell",       "Dystopian",  6, 6),
        ("Sapiens",                   "Yuval Noah Harari",   "Non-Fiction",3, 3),
        ("Clean Code",                "Robert C. Martin",    "Technology", 4, 4),
        ("The Pragmatic Programmer",  "David Thomas",        "Technology", 3, 3),
        ("Dune",                      "Frank Herbert",       "Sci-Fi",     5, 5),
        ("The Alchemist",             "Paulo Coelho",        "Fiction",    7, 7),
        ("Atomic Habits",             "James Clear",         "Self-Help",  4, 4),
        ("Deep Work",                 "Cal Newport",         "Self-Help",  3, 3),
    ]
    cur.executemany(
        "INSERT INTO books (title, author, category, quantity, available) VALUES (?,?,?,?,?)",
        books
    )

    members = [
        ("Alice Johnson", "010-1234-5678", "alice@example.com"),
        ("Bob Smith",     "010-2345-6789", "bob@example.com"),
        ("Carol White",   "010-3456-7890", "carol@example.com"),
        ("David Lee",     "010-4567-8901", "david@example.com"),
        ("Emma Davis",    "010-5678-9012", "emma@example.com"),
    ]
    cur.executemany(
        "INSERT INTO members (name, phone, email) VALUES (?,?,?)",
        members
    )


# ─── Book CRUD ────────────────────────────────────────────────────────────────

def add_book(book: Book) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO books (title, author, category, quantity, available) VALUES (?,?,?,?,?)",
        book.to_tuple()
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_book(book: Book):
    conn = get_connection()
    conn.execute(
        "UPDATE books SET title=?, author=?, category=?, quantity=?, available=? WHERE id=?",
        (*book.to_tuple(), book.id)
    )
    conn.commit()
    conn.close()


def delete_book(book_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()


def get_all_books():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM books ORDER BY title").fetchall()
    conn.close()
    return rows


def search_books(query: str):
    q = f"%{query}%"
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR category LIKE ?",
        (q, q, q)
    ).fetchall()
    conn.close()
    return rows


# ─── Member CRUD ──────────────────────────────────────────────────────────────

def add_member(member: Member) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO members (name, phone, email) VALUES (?,?,?)",
        member.to_tuple()
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_member(member: Member):
    conn = get_connection()
    conn.execute(
        "UPDATE members SET name=?, phone=?, email=? WHERE id=?",
        (*member.to_tuple(), member.id)
    )
    conn.commit()
    conn.close()


def delete_member(member_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM members WHERE id=?", (member_id,))
    conn.commit()
    conn.close()


def get_all_members():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM members ORDER BY name").fetchall()
    conn.close()
    return rows


def search_members(query: str):
    q = f"%{query}%"
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM members WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?",
        (q, q, q)
    ).fetchall()
    conn.close()
    return rows


# ─── Transaction operations ───────────────────────────────────────────────────

def issue_book(book_id: int, member_id: int) -> bool:
    """Issue a book. Returns False if no copies are available."""
    conn = get_connection()
    cur = conn.cursor()
    available = cur.execute(
        "SELECT available FROM books WHERE id=?", (book_id,)
    ).fetchone()["available"]

    if available < 1:
        conn.close()
        return False

    cur.execute(
        "INSERT INTO transactions (book_id, member_id, issue_date, status) VALUES (?,?,?,?)",
        (book_id, member_id, datetime.now().strftime("%Y-%m-%d"), "issued")
    )
    cur.execute("UPDATE books SET available = available - 1 WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    return True


def return_book(transaction_id: int):
    """Mark a transaction as returned and restore the book's available count."""
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT book_id FROM transactions WHERE id=?", (transaction_id,)
    ).fetchone()
    if row:
        cur.execute(
            "UPDATE transactions SET status='returned', return_date=? WHERE id=?",
            (datetime.now().strftime("%Y-%m-%d"), transaction_id)
        )
        cur.execute(
            "UPDATE books SET available = available + 1 WHERE id=?", (row["book_id"],)
        )
    conn.commit()
    conn.close()


def get_active_transactions():
    """Return all currently issued (not yet returned) transactions."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.id, b.title, m.name, t.issue_date, t.status
        FROM transactions t
        JOIN books   b ON t.book_id   = b.id
        JOIN members m ON t.member_id = m.id
        WHERE t.status = 'issued'
        ORDER BY t.issue_date DESC
    """).fetchall()
    conn.close()
    return rows


def get_all_transactions():
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.id, b.title, m.name, t.issue_date,
               COALESCE(t.return_date, '-') AS return_date, t.status
        FROM transactions t
        JOIN books   b ON t.book_id   = b.id
        JOIN members m ON t.member_id = m.id
        ORDER BY t.id DESC
    """).fetchall()
    conn.close()
    return rows


# ─── Dashboard statistics ─────────────────────────────────────────────────────

def get_stats() -> dict:
    conn = get_connection()
    cur = conn.cursor()
    total_books   = cur.execute("SELECT COALESCE(SUM(quantity),0)  FROM books").fetchone()[0]
    total_members = cur.execute("SELECT COUNT(*) FROM members").fetchone()[0]
    issued_books  = cur.execute(
        "SELECT COUNT(*) FROM transactions WHERE status='issued'"
    ).fetchone()[0]
    avail_books   = cur.execute("SELECT COALESCE(SUM(available),0) FROM books").fetchone()[0]
    conn.close()
    return {
        "total_books":   total_books,
        "total_members": total_members,
        "issued_books":  issued_books,
        "avail_books":   avail_books,
    }
