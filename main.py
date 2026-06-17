"""
main.py - Entry point for the Library Management System.
Run with:  python main.py
"""
import sys
import os
import tkinter as tk
from tkinter import ttk

# Ensure the project root is on the path so sub-packages can be imported.
sys.path.insert(0, os.path.dirname(__file__))

import database as db
from ui.dashboard    import DashboardFrame
from ui.books        import BooksFrame
from ui.members      import MembersFrame
from ui.issue_return import IssueReturnFrame

# ── Colour tokens ─────────────────────────────────────────────────────────────
NAVY   = "#1B2B4B"
SLATE  = "#2C3E6B"
INDIGO = "#4A6FA5"
TEAL   = "#2EC4B6"
AMBER  = "#F4A261"
BG     = "#F0F2F8"
WHITE  = "#FFFFFF"
TEXT   = "#1B2B4B"
MUTED  = "#7B8AB8"
SIDEBAR_W = 200


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("1100x680")
        self.minsize(900, 580)
        self.configure(bg=BG)
        self._apply_theme()
        self._build_ui()

    # ── Theme ─────────────────────────────────────────────────────────────────

    def _apply_theme(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Treeview
        style.configure("Treeview",
                        background=WHITE, foreground=TEXT,
                        rowheight=28, fieldbackground=WHITE,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background=NAVY, foreground=WHITE,
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("Treeview",
                  background=[("selected", INDIGO)],
                  foreground=[("selected", WHITE)])
        style.map("Treeview.Heading",
                  background=[("active", SLATE)])

        # Entry / Combobox
        style.configure("TEntry",
                        fieldbackground=WHITE, foreground=TEXT,
                        insertcolor=TEXT, relief="flat")
        style.configure("TCombobox",
                        fieldbackground=WHITE, foreground=TEXT)

        # Scrollbar
        style.configure("Vertical.TScrollbar",   background=BG, troughcolor=WHITE)
        style.configure("Horizontal.TScrollbar", background=BG, troughcolor=WHITE)

        # Separator
        style.configure("TSeparator", background="#D8DCF0")

    # ── Shell layout ──────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Top header bar ─────────────────────────────────────────────────
        header = tk.Frame(self, bg=NAVY, height=52)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text="📖  Library Management System",
                 font=("Segoe UI", 14, "bold"),
                 bg=NAVY, fg=WHITE).pack(side="left", padx=20, pady=12)

        # ── Body: sidebar + content ────────────────────────────────────────
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)

        self._sidebar = tk.Frame(body, bg=SLATE, width=SIDEBAR_W)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        self._content = tk.Frame(body, bg=BG)
        self._content.pack(side="left", fill="both", expand=True)

        # Logo area at top of sidebar
        logo = tk.Frame(self._sidebar, bg=NAVY, height=60)
        logo.pack(fill="x")
        logo.pack_propagate(False)
        tk.Label(logo, text="📚 LibSys", font=("Segoe UI", 13, "bold"),
                 bg=NAVY, fg=WHITE).pack(expand=True)

        # Navigation buttons
        self._nav_buttons = {}
        nav_items = [
            ("🏠  Dashboard",   "dashboard"),
            ("📖  Books",       "books"),
            ("👥  Members",     "members"),
            ("🔄  Issue/Return","issue_return"),
        ]
        for label, key in nav_items:
            btn = tk.Button(self._sidebar, text=label,
                            font=("Segoe UI", 11), anchor="w",
                            padx=20, pady=12,
                            bg=SLATE, fg=WHITE, relief="flat",
                            cursor="hand2", bd=0,
                            activebackground=INDIGO, activeforeground=WHITE,
                            command=lambda k=key: self._navigate(k))
            btn.pack(fill="x")
            self._nav_buttons[key] = btn

        # Spacer + version
        tk.Frame(self._sidebar, bg=SLATE).pack(fill="both", expand=True)
        tk.Label(self._sidebar, text="v1.0.0", font=("Segoe UI", 8),
                 bg=SLATE, fg=MUTED).pack(pady=8)

        # Build all pages (lazy – only create once)
        self._pages: dict[str, tk.Frame] = {}
        self._navigate("dashboard")

    # ── Navigation ────────────────────────────────────────────────────────────

    def _get_page(self, key: str) -> tk.Frame:
        if key not in self._pages:
            cls_map = {
                "dashboard":   DashboardFrame,
                "books":       BooksFrame,
                "members":     MembersFrame,
                "issue_return": IssueReturnFrame,
            }
            page = cls_map[key](self._content)
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._pages[key] = page
        return self._pages[key]

    def _navigate(self, key: str):
        # Highlight active nav button
        for k, btn in self._nav_buttons.items():
            btn.config(bg=INDIGO if k == key else SLATE)

        # Raise or refresh the target page
        page = self._get_page(key)
        page.lift()
        if hasattr(page, "refresh"):
            page.refresh()


if __name__ == "__main__":
    db.initialize_database()
    app = App()
    app.mainloop()
