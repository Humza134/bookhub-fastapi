from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from models.book_model import Book, BookCreate, BookUpdate, BookRead
from models.user_model import User
from services.book_service import BookService
from database.connection import get_session
from typing import Annotated
from sqlalchemy.ext.asyncio.session import AsyncSession
from dependencies import AccessTokenBearer, get_current_user

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()

#get all books
@book_router.get("/", response_model=list[BookRead], status_code=status.HTTP_200_OK)
async def get_all_books(
    session: Annotated[AsyncSession, Depends(get_session)],
    token_details: Annotated[dict, Depends(access_token_bearer)],
):
    """
    Get all books
    """
    # print(f"\n\n User details: {token_details}")
    books = await book_service.get_all_books_service(session)
    return books

@book_router.get("/user", response_model=list[BookRead], status_code=status.HTTP_200_OK)
async def get_user_book_submissions(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_details: Annotated[User, Depends(get_current_user)],
):
    """
    Get all books that belong to the user
    Args:
        session (AsyncSession): The database session.
        token_details (dict): The details of the user from the access token.
    """
    user_uid = user_details.uid
    if user_uid is None:
        raise HTTPException(status_code=400, detail="Invalid token details: missing user UID")
    

    books = await book_service.get_all_books_by_user(session, user_uid)
    return books

#get book by uid
@book_router.get("/{book_uid}", response_model=BookRead, status_code=status.HTTP_200_OK)
async def get_book(
    book_uid: str, session: Annotated[AsyncSession, Depends(get_session)],
    token_details: Annotated[dict, Depends(access_token_bearer)]
):
    """
    Get book by uid
    Args:
        book_uid (str): The UID of the book to retrieve.
        session (AsyncSession): The database session.
    Returns:
        Book: The book object.
    """
    book = await book_service.get_book_service(book_uid, session)
    return book

# create book
@book_router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate, session: Annotated[AsyncSession, Depends(get_session)],
    token_details: Annotated[dict, Depends(access_token_bearer)]
):
    """
    Create a new book
    Args:
        book_data (BookCreate): The data for the new book.
        session (AsyncSession): The database session.
    Returns:
        Book: The created book object.
    """
    user = token_details.get("user")
    if user is None or "uid" not in user:
        raise HTTPException(status_code=400, detail="Invalid token details: missing user UID")
    user_uid = user["uid"]
    book = await book_service.create_book_service(book_data, session, user_uid)
    return book


# update book
@book_router.patch("/{book_uid}", response_model=Book, status_code=status.HTTP_200_OK)
async def update_book(
    book_uid: str,
    book_data: BookUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    token_details: Annotated[dict, Depends(access_token_bearer)]
):
    """
    Update a book by UID
    Args:
        book_uid (str): The UID of the book to update.
        book_data (BookUpdate): The updated data for the book.
        session (AsyncSession): The database session.
    Returns:
        Book: The updated book object.
    """
    book = await book_service.update_book_service(book_uid, book_data, session)
    return book

@book_router.delete("/{book_uid}")
async def delete_book(
    book_uid: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    token_details: Annotated[dict, Depends(access_token_bearer)]
)-> dict[str, str]:
    """
    Delete a book by UID
    Args:
        book_uid (str): The UID of the book to delete.
        session (AsyncSession): The database session.
    Returns:
        dict[str, str]: A dictionary with a success message.
    """
    await book_service.delete_book_service(book_uid, session)
    return {"message": "Book deleted successfully"}
