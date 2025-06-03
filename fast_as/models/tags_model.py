from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
import uuid
from models.book_tag_model import BookTag

class TagBase(SQLModel):
    """Base model for a Tag."""
    name: str
    
class Tag(TagBase, table=True):
    """Database model for a Tag."""
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    books: List["Book"] = Relationship(
        link_model=BookTag,
        back_populates="tags"
    )
    
class TagCreate(TagBase):
    """Input model for creating a new tag."""
    pass

class TagUpdate(SQLModel):
    """Input model for updating a tag."""
    name: Optional[str] = None