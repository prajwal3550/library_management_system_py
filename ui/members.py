"""
ui/members.py - Member management page (Add / Update / Delete / Search).
"""
import tkinter as tk
from tkinter import ttk, messagebox
import re
import database as db
from models import Member

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


def _valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


class MembersFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._selected_id = None
        self._build()
        self.load_members()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=32, pady=(28, 4))
        tk.Label(hdr, text="Member Management", font=("Segoe UI", 22, "bold"),
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

        tk.Label(panel, text="Member Details", font=("Segoe UI", 13, "bold"),
                 bg=WHITE, fg=TEXT).pack(anchor="w", padx=20, pady=(18, 10))
        ttk.Separator(panel, orient="horizontal").pack(fill="x", padx=20, pady=(0, 14))

        self.vars = {}
        for label, key in [("Full Name", "name"), ("Phone", "phone"), ("Email", "email")]:
            tk.Label(panel, text=label, font=("Segoe UI", 10, "bold"),
                     bg=WHITE, fg=TEXT).pack(anchor="w", padx=20, pady=(0, 2))
            var = tk.StringVar()
            ttk.Entry(panel, textvariable=var,
                      font=("Segoe UI", 10)).pack(fill="x", padx=20, pady=(0, 12), ipady=4)
            self.vars[key] = var

        btn_frame = tk.Frame(panel, bg=WHITE)
        btn_frame.pack(fill="x", padx=20, pady=(8, 20))

        for lbl, cmd, color in [
            ("Add",    self.add_member,    INDIGO),
            ("Update", self.update_member, TEAL),
            ("Delete", self.delete_member, ROSE),
            ("Clear",  self.clear_form,    MUTED),
        ]:
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

        sf = tk.Frame(right, bg=BG)
        sf.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        tk.Label(sf, text="🔍", font=("Segoe UI", 12), bg=BG).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.load_members())
        ttk.Entry(sf, textvariable=self.search_var,
                  font=("Segoe UI", 11)).pack(side="left", fill="x", expand=True,
                                              padx=6, ipady=5)
        tk.Button(sf, text="Clear Search", command=lambda: self.search_var.set(""),
                  bg=MUTED, fg=WHITE, font=("Segoe UI", 9), relief="flat",
                  cursor="hand2", padx=8).pack(side="left")

        cols = ("ID", "Name", "Phone", "Email")
        tree_wrap = tk.Frame(right, bg=WHITE, highlightthickness=1,
                             highlightbackground="#D8DCF0")
        tree_wrap.grid(row=1, column=0, sticky="nsew")

        self.tree = ttk.Treeview(tree_wrap, columns=cols, show="headings",
                                 selectmode="browse")
        widths = [50, 200, 140, 250]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, minwidth=w,
                             anchor="center" if c == "ID" else "w")

        vsb = ttk.Scrollbar(tree_wrap, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    # ── Data helpers ──────────────────────────────────────────────────────────

    def load_members(self):
        query = self.search_var.get().strip()
        rows = db.search_members(query) if query else db.get_all_members()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end",
                             values=(row["id"], row["name"], row["phone"], row["email"]),
                             tags=(tag,))
        self.tree.tag_configure("even", background="#F8F9FD")
        self.tree.tag_configure("odd",  background=WHITE)

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        self._selected_id = int(vals[0])
        self.vars["name"].set(vals[1])
        self.vars["phone"].set(vals[2])
        self.vars["email"].set(vals[3])

    # ── Actions ───────────────────────────────────────────────────────────────

    def _get_form(self):
        name  = self.vars["name"].get().strip()
        phone = self.vars["phone"].get().strip()
        email = self.vars["email"].get().strip()
        if not all([name, phone, email]):
            messagebox.showwarning("Validation", "All fields are required.")
            return None
        if not _valid_email(email):
            messagebox.showwarning("Validation", "Please enter a valid email address.")
            return None
        return name, phone, email

    def add_member(self):
        data = self._get_form()
        if not data:
            return
        name, phone, email = data
        try:
            db.add_member(Member(id=None, name=name, phone=phone, email=email))
        except Exception:
            messagebox.showerror("Error", "Email already exists.")
            return
        self.clear_form()
        self.load_members()
        messagebox.showinfo("Success", "Member added successfully.")

    def update_member(self):
        if not self._selected_id:
            messagebox.showwarning("Select", "Please select a member to update.")
            return
        data = self._get_form()
        if not data:
            return
        name, phone, email = data
        try:
            db.update_member(Member(id=self._selected_id, name=name, phone=phone, email=email))
        except Exception:
            messagebox.showerror("Error", "Email already exists for another member.")
            return
        self.load_members()
        messagebox.showinfo("Success", "Member updated.")

    def delete_member(self):
        if not self._selected_id:
            messagebox.showwarning("Select", "Please select a member to delete.")
            return
        if messagebox.askyesno("Confirm", "Delete this member?"):
            db.delete_member(self._selected_id)
            self.clear_form()
            self.load_members()

    def clear_form(self):
        for var in self.vars.values():
            var.set("")
        self._selected_id = None
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def refresh(self):
        self.load_members()
