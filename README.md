# 📚 Library Management System

A professional desktop application for managing a library's books, members, and
issue/return transactions. Built with Python 3, Tkinter, and SQLite — no third-party
packages required.

---

## Features

| Module | Capabilities |
|---|---|
| **Dashboard** | Live stats (total books, members, issued & available copies); recent-transaction log |
| **Books** | Add · Update · Delete · Search (live filtering); table with sort; low-availability highlight |
| **Members** | Add · Update · Delete · Search; email validation |
| **Issue / Return** | Issue books to members; one-click return; auto-updates available count; view active or all transactions |

---

## Project Structure

```
Library_Management_System/
├── main.py            # Entry point & shell (sidebar, header, router)
├── database.py        # All SQLite CRUD & stat helpers
├── models.py          # Dataclasses: Book, Member, Transaction
├── requirements.txt   # No pip dependencies (stdlib only)
├── README.md
│
├── database/
│   └── library.db     # Created automatically on first run
│
├── ui/
│   ├── dashboard.py   # Dashboard page
│   ├── books.py       # Book management page
│   ├── members.py     # Member management page
│   └── issue_return.py# Issue & Return page
│
└── assets/            # Place custom icons / images here
```

---

## Installation & Running

### Prerequisites
- Python 3.8 or newer
- Tkinter (bundled with standard CPython on Windows and macOS)
  - **Ubuntu / Debian Linux**: `sudo apt install python3-tk`
  - **Fedora**: `sudo dnf install python3-tkinter`

### Steps

```bash
# 1. Clone or download the project
git clone https://github.com/yourname/library-management-system.git
cd Library_Management_System

# 2. (Optional) create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Run – no pip installs needed
python main.py
```

On first run the app will:
- Create `database/library.db` automatically
- Seed 10 sample books and 5 sample members so you can explore right away

---

## Usage Guide

### Dashboard
Opens automatically on launch. Stats refresh each time you navigate back to the page.

### Books
- Fill the left-hand form and click **Add** to create a book.
- Click a row in the table to populate the form, then **Update** or **Delete**.
- Type in the search bar to filter the list instantly (searches title, author, category).
- Rows shown in **red** have zero available copies.

### Members
- Same form-and-table workflow as Books.
- Email must be valid and unique.

### Issue / Return
- Select a **Book** and a **Member** from the dropdowns and click **Issue Book**.
  The dropdown shows current available count.  If it reaches 0 the issue is blocked.
- Switch to **All Transactions** to see returned records too.
- Click an active (orange) row, then **Return Book** to process a return.
  Available count is restored automatically.

---

## Screenshots

*(Replace with actual screenshots after first run)*

| Dashboard | Books |
|---|---|
| ![dashboard](assets/screenshot_dashboard.png) | ![books](assets/screenshot_books.png) |

| Members | Issue / Return |
|---|---|
| ![members](assets/screenshot_members.png) | ![issue](assets/screenshot_issue.png) |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.8+ |
| GUI | Tkinter + ttk |
| Database | SQLite 3 (via stdlib `sqlite3`) |
| Architecture | OOP, MVC-inspired separation of concerns |

---

## License

MIT — free to use, modify, and distribute.
