"""
ui/dashboard.py - Dashboard page showing library statistics.
"""
import tkinter as tk
from tkinter import ttk
import database as db


# ── Colour tokens (shared with the rest of the app via import) ────────────────
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


class DashboardFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        # Page title
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=32, pady=(28, 4))
        tk.Label(hdr, text="Dashboard", font=("Segoe UI", 22, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")
        tk.Label(hdr, text="Overview of your library at a glance",
                 font=("Segoe UI", 11), bg=BG, fg=MUTED).pack(side="left", padx=12, pady=6)

        # Stat cards row
        self.cards_frame = tk.Frame(self, bg=BG)
        self.cards_frame.pack(fill="x", padx=32, pady=16)

        self.card_widgets = {}
        cards_cfg = [
            ("total_books",   "📚 Total Books",     INDIGO),
            ("total_members", "👥 Total Members",   TEAL),
            ("issued_books",  "📤 Issued Books",    AMBER),
            ("avail_books",   "✅ Available Books", GREEN),
        ]
        for col, (key, label, color) in enumerate(cards_cfg):
            card = self._stat_card(self.cards_frame, label, "—", color)
            card.grid(row=0, column=col, padx=10, pady=4, sticky="nsew")
            self.cards_frame.columnconfigure(col, weight=1)
            self.card_widgets[key] = card

        # Recent transactions table
        sec = tk.Frame(self, bg=BG)
        sec.pack(fill="both", expand=True, padx=32, pady=(8, 24))

        tk.Label(sec, text="Recent Transactions", font=("Segoe UI", 14, "bold"),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(0, 8))

        cols = ("ID", "Book", "Member", "Issue Date", "Status")
        tree_frame = tk.Frame(sec, bg=WHITE, bd=0, relief="flat",
                              highlightthickness=1, highlightbackground="#D8DCF0")
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                 selectmode="browse")
        widths = [50, 240, 160, 110, 90]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="center" if c in ("ID","Status") else "w",
                             minwidth=w)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",   command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.refresh()

    def _stat_card(self, parent, label, value, color):
        """Build one stat card and return a reference so the value can be updated."""
        card = tk.Frame(parent, bg=WHITE, bd=0, relief="flat",
                        highlightthickness=2, highlightbackground=color)
        accent = tk.Frame(card, bg=color, width=6)
        accent.pack(side="left", fill="y")
        inner = tk.Frame(card, bg=WHITE, padx=18, pady=18)
        inner.pack(fill="both", expand=True)
        lbl = tk.Label(inner, text=label, font=("Segoe UI", 10), bg=WHITE, fg=MUTED)
        lbl.pack(anchor="w")
        val = tk.Label(inner, text=value, font=("Segoe UI", 26, "bold"), bg=WHITE, fg=color)
        val.pack(anchor="w", pady=(4, 0))
        card._value_label = val          # stash reference for updates
        return card

    def refresh(self):
        """Reload stats and recent transaction list from the database."""
        stats = db.get_stats()
        keys = ["total_books", "total_members", "issued_books", "avail_books"]
        for key in keys:
            self.card_widgets[key]._value_label.config(text=str(stats[key]))

        # Recent transactions (latest 50)
        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, row in enumerate(db.get_all_transactions()[:50]):
            tag = "even" if i % 2 == 0 else "odd"
            status_tag = "issued" if row["status"] == "issued" else "returned"
            self.tree.insert("", "end",
                             values=(row["id"], row["title"], row["name"],
                                     row["issue_date"], row["status"].capitalize()),
                             tags=(tag, status_tag))

        self.tree.tag_configure("even",     background="#F8F9FD")
        self.tree.tag_configure("odd",      background=WHITE)
        self.tree.tag_configure("issued",   foreground=AMBER)
        self.tree.tag_configure("returned", foreground=GREEN)
