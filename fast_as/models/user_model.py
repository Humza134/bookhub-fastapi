from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
import uuid
# from enum import Enum 


# class UserRole(str, Enum):
#     """Enum for user roles."""
#     ADMIN = "admin"
#     USER = "user"


class UserBase(SQLModel):
    username: str
    email: str


class User(UserBase, table=True):
    """Database model for a User."""
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    role: str = Field(default="user")
    password_hashed: str = Field(nullable=False)
    is_verified: bool = Field(default=False)
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})

    # Relationship: One-to-Many (User → Books)
    books: List["Book"] = Relationship(back_populates="user")
    reviews: List["Review"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    """Input model for creating a new user."""
    password: str


class UserReadWithBooks(BaseModel):
    title: str

class UserReadWithReviews(BaseModel):
    content: str
    rating: int

class UserRead(UserBase):
    """Output model for reading user data."""
    uid: uuid.UUID
    is_verified: bool
    role: str
class UserReadWithBooksAndReviews(UserBase):
    """Output model for reading user data."""
    uid: uuid.UUID
    is_verified: bool
    role: str
    books: List[UserReadWithBooks] = []  # type: ignore
    reviews: List[UserReadWithReviews] = []  # type: ignore


class UserLogin(SQLModel):
    """Input model for logging in."""
    email: str
    password: str

# UserReadWithBooks.model_rebuild()
# Book.model_rebuild()

# from sqlmodel import SQLModel, Field
# from datetime import datetime
# import uuid
# # from enum import Enum

# """User model for the FastAPI application."""

# # class UserRole(str, Enum):
# #     """Enum for user roles."""
# #     ADMIN = "admin"
# #     USER = "user"

# class UserBase(SQLModel):
#     username: str
#     email: str

# class User(UserBase, table=True):
#     """User model for the FastAPI application."""
#     uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
#     role: str = Field(default="user")  # Default role is 'user'
#     password_hashed: str = Field(nullable=False)
#     is_verified: bool = Field(default=False)
#     created_at: datetime | None = Field(default_factory=datetime.now)
#     updated_at: datetime | None = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})

# class UserCreate(UserBase):
#     """User model for creating a new user."""
#     password: str = Field(nullable=False)


# class UserRead(UserBase):
#     """User model for reading a user."""
#     uid: uuid.UUID
#     is_verified: bool

# class LoginUser(SQLModel):
#     """User model for logging in a user."""
#     email: str
#     password: str