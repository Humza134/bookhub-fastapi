from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
import uuid

class BookTag(SQLModel, table=True):
    """Database model for a Book-Tag association."""
    book_uid: uuid.UUID = Field(foreign_key="book.uid", primary_key=True)
    tag_uid: uuid.UUID = Field(foreign_key="tag.uid", primary_key=True)