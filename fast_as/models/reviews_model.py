from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid
from typing import Optional, List

class ReviewBase(SQLModel):
    """Base model for a review."""
    content: str = Field(..., description="Content of the review")
    rating: int = Field(ge=1, le=5, description="Rating must be between 1 and 5")

class Review(ReviewBase, table=True):
    """Database model for a Review."""
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})

    # Relationship: Many-to-One (Review → User)
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="user.uid")
    user: "User" = Relationship(back_populates="reviews")

    # Relationship: Many-to-One (Review → Book)
    book_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="book.uid")
    book: "Book" = Relationship(back_populates="reviews")

class ReviewCreate(ReviewBase):
    """Input model for creating a new review."""
    pass

class ReviewRead(ReviewBase):
    """Output model for reading a review."""
    uid: uuid.UUID
    user_uid: uuid.UUID
    book_uid: uuid.UUID
    created_at: datetime
    updated_at: datetime

class ReviewUpdate(SQLModel):
    """Input model for updating a review."""
    content: Optional[str] = None
    rating: Optional[int] = None

