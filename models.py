"""
models.py - Data models for the Library Management System
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    """Represents a book in the library."""
    id: Optional[int]
    title: str
    author: str
    category: str
    quantity: int
    available: int

    def to_tuple(self):
        return (self.title, self.author, self.category, self.quantity, self.available)


@dataclass
class Member:
    """Represents a library member."""
    id: Optional[int]
    name: str
    phone: str
    email: str

    def to_tuple(self):
        return (self.name, self.phone, self.email)


@dataclass
class Transaction:
    """Represents a book issue/return transaction."""
    id: Optional[int]
    book_id: int
    member_id: int
    issue_date: str
    return_date: Optional[str]
    status: str  # 'issued' or 'returned'
