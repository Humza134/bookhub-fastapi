from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from models.reviews_model import Review, ReviewCreate, ReviewUpdate
from models.user_model import User
from models.book_model import Book
from services.review_service import ReviewService
from database.connection import get_session
from typing import Annotated
from sqlalchemy.ext.asyncio.session import AsyncSession
from dependencies import get_current_user

review_router = APIRouter()
review_service = ReviewService()
# access_token_bearer = AccessTokenBearer()

@review_router.post("/book/{book_uid}", response_model=Review, status_code=status.HTTP_201_CREATED)
async def add_review(
    book_uid: str,
    review_data: ReviewCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_details: Annotated[User, Depends(get_current_user)],
):
    """
    Add a review for a book.
    
    Args:
        book_uid (str): The UID of the book to review.
        review_data (ReviewCreate): The data for the new review.
        session (AsyncSession): The database session.
        user_details (User): The current user details.
    
    Returns:
        Review: The created review object.
    """
    user_uid = user_details.uid
    if not user_uid:
        raise HTTPException(status_code=400, detail="Invalid user details: missing user UID")
    
    return await review_service.add_review_service(session, review_data, user_uid, book_uid)