"""
ui/books.py - Book management page (Add / Update / Delete / Search).
"""
import tkinter as tk
from tkinter import ttk, messagebox
import database as db
from models import Book

NAVY   = "#1B2B4B"
SLATE  = "#2C3E6B"
INDIGO = "#4A6FA5"
TEAL   = "#2EC4B6"
AMBER  = "#F4A261"
ROSE   = "#E76F51"
GREEN  = "#52B788"
BG     = "#F0F2F8"
WHITE  = "#FFFFFF"
TEXT   = "#1B2B4B"
MUTED  = "#7B8AB8"

CATEGORIES = ["Fiction", "Non-Fiction", "Science", "Technology", "History",
               "Biography", "Self-Help", "Dystopian", "Sci-Fi", "Fantasy", "Other"]


class BooksFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._selected_id = None
        self._build()
        self.load_books()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=32, pady=(28, 4))
        tk.Label(hdr, text="Book Management", font=("Segoe UI", 22, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")

        # Main split: left form | right table
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=32, pady=12)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_form(body)
        self._build_table(body)

    def _build_form(self, parent):
        panel = tk.Frame(parent, bg=WHITE, bd=0, relief="flat",
                         highlightthickness=1, highlightbackground="#D8DCF0",
                         width=300)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        panel.pack_propagate(False)

        tk.Label(panel, text="Book Details", font=("Segoe UI", 13, "bold"),
                 bg=WHITE, fg=TEXT).pack(anchor="w", padx=20, pady=(18, 10))
        ttk.Separator(panel, orient="horizontal").pack(fill="x", padx=20, pady=(0, 14))

        self.vars = {}
        fields = [("Title", "title"), ("Author", "author"),
                  ("Category", "category"), ("Quantity", "quantity")]

        for label, key in fields:
            tk.Label(panel, text=label, font=("Segoe UI", 10, "bold"),
                     bg=WHITE, fg=TEXT).pack(anchor="w", padx=20, pady=(0, 2))
            if key == "category":
                var = tk.StringVar(value=CATEGORIES[0])
                widget = ttk.Combobox(panel, textvariable=var, values=CATEGORIES,
                                      state="readonly", font=("Segoe UI", 10))
            else:
                var = tk.StringVar()
                widget = ttk.Entry(panel, textvariable=var, font=("Segoe UI", 10))
            widget.pack(fill="x", padx=20, pady=(0, 12), ipady=4)
            self.vars[key] = var

        # Buttons
        btn_frame = tk.Frame(panel, bg=WHITE)
        btn_frame.pack(fill="x", padx=20, pady=(8, 20))

        btn_cfg = [
            ("Add",    self.add_book,    INDIGO),
            ("Update", self.update_book, TEAL),
            ("Delete", self.delete_book, ROSE),
            ("Clear",  self.clear_form,  MUTED),
        ]
        for row, (lbl, cmd, color) in enumerate(btn_cfg):
            tk.Button(btn_frame, text=lbl, command=cmd,
                      bg=color, fg=WHITE, font=("Segoe UI", 10, "bold"),
                      relief="flat", cursor="hand2", padx=10, pady=6,
                      activebackground=SLATE, activeforeground=WHITE
                      ).pack(fill="x", pady=3)

    def _build_table(self, parent):
        right = tk.Frame(parent, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        # Search bar
        sf = tk.Frame(right, bg=BG)
        sf.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        tk.Label(sf, text="🔍", font=("Segoe UI", 12), bg=BG).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.load_books())
        ttk.Entry(sf, textvariable=self.search_var,
                  font=("Segoe UI", 11)).pack(side="left", fill="x",
                                              expand=True, padx=6, ipady=5)
        tk.Button(sf, text="Clear Search", command=lambda: self.search_var.set(""),
                  bg=MUTED, fg=WHITE, font=("Segoe UI", 9), relief="flat",
                  cursor="hand2", padx=8).pack(side="left")

        # Treeview
        cols = ("ID", "Title", "Author", "Category", "Quantity", "Available")
        tree_wrap = tk.Frame(right, bg=WHITE, highlightthickness=1,
                             highlightbackground="#D8DCF0")
        tree_wrap.grid(row=1, column=0, sticky="nsew")

        self.tree = ttk.Treeview(tree_wrap, columns=cols, show="headings",
                                 selectmode="browse")
        widths = [45, 210, 150, 110, 80, 80]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c, command=lambda _c=c: self._sort(_c))
            self.tree.column(c, width=w, minwidth=w,
                             anchor="center" if c not in ("Title","Author","Category") else "w")

        vsb = ttk.Scrollbar(tree_wrap, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    # ── Data helpers ──────────────────────────────────────────────────────────

    def load_books(self):
        query = self.search_var.get().strip()
        rows = db.search_books(query) if query else db.get_all_books()
        self._populate(rows)

    def _populate(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            low_tag = "low" if row["available"] == 0 else ""
            self.tree.insert("", "end",
                             values=(row["id"], row["title"], row["author"],
                                     row["category"], row["quantity"], row["available"]),
                             tags=(tag, low_tag))
        self.tree.tag_configure("even", background="#F8F9FD")
        self.tree.tag_configure("odd",  background=WHITE)
        self.tree.tag_configure("low",  foreground=ROSE)

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        self._selected_id = int(vals[0])
        self.vars["title"].set(vals[1])
        self.vars["author"].set(vals[2])
        self.vars["category"].set(vals[3])
        self.vars["quantity"].set(vals[4])

    def _sort(self, col):
        data = [(self.tree.set(child, col), child)
                for child in self.tree.get_children("")]
        try:
            data.sort(key=lambda t: int(t[0]))
        except ValueError:
            data.sort()
        for i, (_, child) in enumerate(data):
            self.tree.move(child, "", i)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _get_form(self):
        title    = self.vars["title"].get().strip()
        author   = self.vars["author"].get().strip()
        category = self.vars["category"].get().strip()
        qty_str  = self.vars["quantity"].get().strip()

        if not all([title, author, category, qty_str]):
            messagebox.showwarning("Validation", "All fields are required.")
            return None
        try:
            qty = int(qty_str)
            if qty < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Quantity must be a positive integer.")
            return None
        return title, author, category, qty

    def add_book(self):
        data = self._get_form()
        if not data:
            return
        title, author, category, qty = data
        book = Book(id=None, title=title, author=author,
                    category=category, quantity=qty, available=qty)
        db.add_book(book)
        self.clear_form()
        self.load_books()
        messagebox.showinfo("Success", "Book added successfully.")

    def update_book(self):
        if not self._selected_id:
            messagebox.showwarning("Select", "Please select a book to update.")
            return
        data = self._get_form()
        if not data:
            return
        title, author, category, qty = data
        # Keep the same available count (don't reset it on update)
        book = Book(id=self._selected_id, title=title, author=author,
                    category=category, quantity=qty, available=qty)
        db.update_book(book)
        self.load_books()
        messagebox.showinfo("Success", "Book updated.")

    def delete_book(self):
        if not self._selected_id:
            messagebox.showwarning("Select", "Please select a book to delete.")
            return
        if messagebox.askyesno("Confirm", "Delete this book? This cannot be undone."):
            db.delete_book(self._selected_id)
            self.clear_form()
            self.load_books()

    def clear_form(self):
        for var in self.vars.values():
            var.set("")
        self.vars["category"].set(CATEGORIES[0])
        self._selected_id = None
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def refresh(self):
        self.load_books()
