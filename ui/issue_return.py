"""
ui/issue_return.py - Issue and Return books page.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import database as db

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


class IssueReturnFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._selected_txn_id = None
        self._build()
        self.load_data()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=32, pady=(28, 4))
        tk.Label(hdr, text="Issue & Return", font=("Segoe UI", 22, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")

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

        # ── Issue section ──────────────────────────────────────────────────
        tk.Label(panel, text="Issue a Book", font=("Segoe UI", 13, "bold"),
                 bg=WHITE, fg=TEXT).pack(anchor="w", padx=20, pady=(18, 10))
        ttk.Separator(panel, orient="horizontal").pack(fill="x", padx=20, pady=(0, 14))

        # Book dropdown
        tk.Label(panel, text="Book", font=("Segoe UI", 10, "bold"),
                 bg=WHITE, fg=TEXT).pack(anchor="w", padx=20, pady=(0, 2))
        self.book_var = tk.StringVar()
        self.book_cb  = ttk.Combobox(panel, textvariable=self.book_var,
                                     state="readonly", font=("Segoe UI", 10))
        self.book_cb.pack(fill="x", padx=20, pady=(0, 12), ipady=4)

        # Member dropdown
        tk.Label(panel, text="Member", font=("Segoe UI", 10, "bold"),
                 bg=WHITE, fg=TEXT).pack(anchor="w", padx=20, pady=(0, 2))
        self.member_var = tk.StringVar()
        self.member_cb  = ttk.Combobox(panel, textvariable=self.member_var,
                                       state="readonly", font=("Segoe UI", 10))
        self.member_cb.pack(fill="x", padx=20, pady=(0, 12), ipady=4)

        tk.Button(panel, text="Issue Book", command=self.issue_book,
                  bg=INDIGO, fg=WHITE, font=("Segoe UI", 10, "bold"),
                  relief="flat", cursor="hand2", padx=10, pady=7,
                  activebackground=SLATE, activeforeground=WHITE
                  ).pack(fill="x", padx=20, pady=(4, 4))

        ttk.Separator(panel, orient="horizontal").pack(fill="x", padx=20, pady=18)

        # ── Return section ─────────────────────────────────────────────────
        tk.Label(panel, text="Return a Book", font=("Segoe UI", 13, "bold"),
                 bg=WHITE, fg=TEXT).pack(anchor="w", padx=20, pady=(0, 8))
        tk.Label(panel, text="Select a row in the table\nthen click Return.",
                 font=("Segoe UI", 9), bg=WHITE, fg=MUTED,
                 justify="left").pack(anchor="w", padx=20)

        self.selected_lbl = tk.Label(panel, text="No transaction selected",
                                     font=("Segoe UI", 9, "italic"),
                                     bg=WHITE, fg=AMBER)
        self.selected_lbl.pack(anchor="w", padx=20, pady=6)

        tk.Button(panel, text="Return Book", command=self.return_book,
                  bg=GREEN, fg=WHITE, font=("Segoe UI", 10, "bold"),
                  relief="flat", cursor="hand2", padx=10, pady=7,
                  activebackground=SLATE, activeforeground=WHITE
                  ).pack(fill="x", padx=20, pady=(0, 20))

    def _build_table(self, parent):
        right = tk.Frame(parent, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        # Tab-style toggle for active vs all
        tab_row = tk.Frame(right, bg=BG)
        tab_row.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.view_var = tk.StringVar(value="active")
        for val, lbl in [("active", "Active Issues"), ("all", "All Transactions")]:
            tk.Radiobutton(tab_row, text=lbl, variable=self.view_var, value=val,
                           command=self.load_data, bg=BG, fg=TEXT,
                           selectcolor=INDIGO, font=("Segoe UI", 10),
                           activebackground=BG).pack(side="left", padx=8)

        cols_active = ("Txn ID", "Book Title", "Member", "Issue Date", "Status")
        cols_all    = ("Txn ID", "Book Title", "Member", "Issue Date", "Return Date", "Status")

        tree_wrap = tk.Frame(right, bg=WHITE, highlightthickness=1,
                             highlightbackground="#D8DCF0")
        tree_wrap.grid(row=1, column=0, sticky="nsew")

        self.tree = ttk.Treeview(tree_wrap, columns=cols_active, show="headings",
                                 selectmode="browse")
        self._set_columns(cols_active)

        vsb = ttk.Scrollbar(tree_wrap, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _set_columns(self, cols):
        self.tree.configure(columns=cols)
        widths = {
            "Txn ID": 60, "Book Title": 220, "Member": 150,
            "Issue Date": 100, "Return Date": 100, "Status": 90
        }
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=widths.get(c, 100), minwidth=widths.get(c, 80),
                             anchor="center" if c in ("Txn ID","Status") else "w")

    # ── Data helpers ──────────────────────────────────────────────────────────

    def load_data(self):
        # Refresh dropdowns
        books   = db.get_all_books()
        members = db.get_all_members()
        self._book_map   = {f"{r['title']} (avail: {r['available']})": r["id"] for r in books}
        self._member_map = {f"{r['name']} — {r['email']}": r["id"] for r in members}
        self.book_cb["values"]   = list(self._book_map.keys())
        self.member_cb["values"] = list(self._member_map.keys())

        # Refresh table
        is_active = self.view_var.get() == "active"
        rows = db.get_active_transactions() if is_active else db.get_all_transactions()

        if is_active:
            cols = ("Txn ID", "Book Title", "Member", "Issue Date", "Status")
        else:
            cols = ("Txn ID", "Book Title", "Member", "Issue Date", "Return Date", "Status")

        self._set_columns(cols)
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            values = tuple(row)
            status = row["status"]
            self.tree.insert("", "end", values=values,
                             tags=(tag, status))

        self.tree.tag_configure("even",     background="#F8F9FD")
        self.tree.tag_configure("odd",      background=WHITE)
        self.tree.tag_configure("issued",   foreground=AMBER)
        self.tree.tag_configure("returned", foreground=GREEN)

        # Reset selection
        self._selected_txn_id = None
        self.selected_lbl.config(text="No transaction selected")

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        # Only allow selecting active (issued) transactions for return
        if vals[-1].lower() == "issued":
            self._selected_txn_id = int(vals[0])
            self.selected_lbl.config(text=f"Transaction #{vals[0]}: {vals[1][:30]}")
        else:
            self._selected_txn_id = None
            self.selected_lbl.config(text="Already returned — pick an active row")

    # ── Actions ───────────────────────────────────────────────────────────────

    def issue_book(self):
        book_sel   = self.book_var.get()
        member_sel = self.member_var.get()
        if not book_sel or not member_sel:
            messagebox.showwarning("Validation", "Please select both a book and a member.")
            return
        book_id   = self._book_map[book_sel]
        member_id = self._member_map[member_sel]
        success = db.issue_book(book_id, member_id)
        if success:
            messagebox.showinfo("Success", "Book issued successfully.")
            self.book_var.set("")
            self.member_var.set("")
            self.load_data()
        else:
            messagebox.showerror("Unavailable", "No copies of this book are currently available.")

    def return_book(self):
        if not self._selected_txn_id:
            messagebox.showwarning("Select", "Please select an active transaction to return.")
            return
        if messagebox.askyesno("Confirm", f"Mark transaction #{self._selected_txn_id} as returned?"):
            db.return_book(self._selected_txn_id)
            messagebox.showinfo("Success", "Book returned successfully.")
            self.load_data()

    def refresh(self):
        self.load_data()
