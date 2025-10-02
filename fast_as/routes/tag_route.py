from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio.session import AsyncSession
from models.tags_model import Tag, TagCreate, TagRead, TagUpdate
from models.book_model import BookReadWithReviwes, Book
from models.user_model import User
from services.tag_service import TagService
from database.connection import get_session
from dependencies import get_current_user, AccessTokenBearer

tag_router = APIRouter()
tag_service = TagService()
access_token_bearer = AccessTokenBearer()

# get all tags
@tag_router.get("/", response_model=list[TagRead], status_code=status.HTTP_200_OK)
async def get_all_tags(
    session: Annotated[AsyncSession, Depends(get_session)],
    token_details: Annotated[dict, Depends(access_token_bearer)],
): 
    """
    Get all tags
    """
    tags = await tag_service.get_all_tags_service(session)
    return tags

@tag_router.get("/{tag_uid}", response_model=TagRead, status_code=status.HTTP_200_OK)
async def get_tag(
    tag_uid: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    token_details: Annotated[dict, Depends(access_token_bearer)],
):
    """
    Get a specific tag by UID
    Args:
        tag_uid (str): The UID of the tag to retrieve.
        session (AsyncSession): The database session.
    Returns:
        Tag: The tag object.
    """
    tag = await tag_service.get_tag_service(tag_uid, session)
    return tag

@tag_router.get("/{tag_uid}/books", response_model=list[BookReadWithReviwes], status_code=status.HTTP_200_OK)
async def get_books_by_tag(
    tag_uid: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    token_details: Annotated[dict, Depends(access_token_bearer)],
):
    """
    Get all books associated with a specific tag by UID
    Args:
        tag_uid (str): The UID of the tag.
        session (AsyncSession): The database session.
    Returns:
        List[Book]: A list of book objects associated with the tag.
    """
    books = await tag_service.get_books_by_tag_service(tag_uid, session)
    return books

@tag_router.post("/{book_uid}/tags", response_model=Book, status_code=status.HTTP_200_OK)
async def add_tags_to_book(
    book_uid: str,
    tag_names: list[str],
    session: Annotated[AsyncSession, Depends(get_session)],
    user_details: Annotated[User, Depends(get_current_user)]
):
    """
    Add tags to a book
    Args:
        book_uid (str): The UID of the book to add tags to.
        tag_names (List[str]): A list of tag names to add to the book.
        session (AsyncSession): The database session.
        user_details (User): The current user details.
    Returns:
        Book: The updated book object with the added tags.
    """
    user_uid = user_details.uid
    if not user_uid:
        raise HTTPException(status_code=400, detail="Invalid user details: missing user UID")
    
    updated_book_with_tags = await tag_service.add_tags_to_book_service(book_uid, tag_names, session, user_uid)
    return updated_book_with_tags

@tag_router.delete("/{book_uid}/tags/{tag_uid}", response_model=Book, status_code=status.HTTP_200_OK)
async def remove_tag_from_book(
    book_uid: str,
    tag_uid: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_details: Annotated[User, Depends(get_current_user)]
):
    user_uid = user_details.uid
    if not user_uid:
        raise HTTPException(status_code=400, detail="Invalid user details: missing user UID")
    
    updated_book_without_tag = await tag_service.remove_tag_from_book_service(book_uid, tag_uid, session, user_uid)
    return updated_book_without_tag
