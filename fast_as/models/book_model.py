from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
import uuid
from models.reviews_model import ReviewWithBook
from models.book_tag_model import BookTag
from models.tags_model import TagRead

class BookBase(SQLModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str


class Book(BookBase, table=True):
    """Database model for a Book."""
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="user.uid")
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})

    # Relationship: Many-to-One (Book → User)
    user: Optional["User"] = Relationship(back_populates="books")

    # Relationship: One-to-Many (Book → Review)
    reviews: List["Review"] = Relationship(back_populates="book")

    tags: List["Tag"] = Relationship(
        link_model=BookTag,
        back_populates="books"
    )


class BookCreate(BookBase):
    """Input model for creating a new book."""
    pass

class BookRead(BookBase):
    pass

class BookReadWithReviwes(BookBase):
    """Output model for reading a book."""
    uid: uuid.UUID
    user_uid: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    reviews: List[ReviewWithBook] = []  # type: ignore
    
class BookReadWithReviwesAndTags(BookReadWithReviwes):
    """Output model for reading a book."""
    tags: List[TagRead]

class BookUpdate(SQLModel):
    """Input model for updating a book."""
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None



# from sqlmodel import SQLModel, Field
# from datetime import datetime
# import uuid

# class BookBase(SQLModel):
#     title: str
#     author: str
#     publisher: str
#     published_date: str
#     page_count: int
#     language: str

# class Book(BookBase, table=True):
#     uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
#     user_uid: uuid.UUID = Field(default=None, foreign_key="user.uid")
#     created_at: datetime | None = Field(default_factory=datetime.now)
#     updated_at: datetime | None = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})

# class BookCreate(BookBase):
#     pass

# class BookUpdate(SQLModel):
#     title: str | None = Field(default=None, nullable=True)
#     author: str | None = Field(default=None, nullable=True)
#     publisher: str | None = Field(default=None, nullable=True)
#     published_date: str | None = Field(default=None, nullable=True)
#     page_count: int | None = Field(default=None, nullable=True)
#     language: str | None = Field(default=None, nullable=True)
    