# Library Management System Documentation

## Introduction

The Library Management System is a command-line application developed using Python and SQLite. It helps users manage book records efficiently through a simple menu-based interface.

---

## System Requirements

* Python 3.8 or later
* SQLite3 (included with Python)

---

## Database Design

### Books Table

| Column   | Type    | Description      |
| -------- | ------- | ---------------- |
| id       | INTEGER | Primary Key      |
| title    | TEXT    | Book Title       |
| author   | TEXT    | Author Name      |
| quantity | INTEGER | Available Copies |

---

## Functional Modules

### Add Book

Allows users to add a new book record.

Input:

* Book Title
* Author Name
* Quantity

Output:

* Book added successfully.

---

### View Books

Displays all books stored in the database.

Output:

* Book ID
* Title
* Author
* Quantity

---

### Search Book

Allows users to search for books by title.

Input:

* Book title or keyword

Output:

* Matching book records

---

### Update Book

Updates existing book information.

Input:

* Book ID
* New Title
* New Author
* New Quantity

Output:

* Book updated successfully

---

### Delete Book

Deletes a book from the database.

Input:

* Book ID

Output:

* Book removed successfully

---

### Issue Book

Issues a book to a user.

Process:

* Checks book availability
* Decreases quantity by one

Output:

* Book issued successfully

---

### Return Book

Returns a previously issued book.

Process:

* Increases quantity by one

Output:

* Book returned successfully

---

## Program Flow

1. Application starts
2. Database connection established
3. Main menu displayed
4. User selects an operation
5. Database updated accordingly
6. User exits application
7. Database connection closes

---

## Error Handling

Current implementation handles:

* Invalid menu selection
* Book not found
* Out-of-stock books

Future versions can include:

* Input validation
* Exception handling
* Logging system

---

## Future Scope

* GUI using Tkinter
* Multi-user support
* Authentication system
* Fine calculation
* Book categories
* Report generation
* Cloud database integration

---

## Conclusion

This project demonstrates the practical use of Python programming, SQLite databases, CRUD operations, and software project organization. It serves as a beginner-friendly example of a real-world management system.
