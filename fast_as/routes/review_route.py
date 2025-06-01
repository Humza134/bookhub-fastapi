from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio.session import AsyncSession
from models.reviews_model import Review, ReviewCreate, ReviewUpdate
from models.user_model import User
from models.book_model import Book
from services.review_service import ReviewService
from database.connection import get_session
from dependencies import get_current_user, AccessTokenBearer

review_router = APIRouter()
review_service = ReviewService()
access_token_bearer = AccessTokenBearer()
# access_token_bearer = AccessTokenBearer()

@review_router.post("/{book_uid}", response_model=Review, status_code=status.HTTP_201_CREATED)
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


@review_router.get("/{review_uid}", response_model=Review, status_code=status.HTTP_200_OK)
async def get_review(
    review_uid: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    token_details: Annotated[dict, Depends(access_token_bearer)],
):
    """
    Get a specific review by UID.
    
    Args:
        review_uid (str): The UID of the review to retrieve.
        session (AsyncSession): The database session.
        user_details (User): The current user details.
    
    Returns:
        Review: The review object.
    """
    return await review_service.get_review_service(session, review_uid)

@review_router.patch("/{review_uid}", response_model=Review, status_code=status.HTTP_200_OK)
async def update_review(
    review_uid: str,
    review_data: ReviewUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_details: Annotated[User, Depends(get_current_user)],
):
    """
    Update a review by UID.
    
    Args:
        review_uid (str): The UID of the review to update.
        review_data (ReviewUpdate): The data to update the review with.
        session (AsyncSession): The database session.
        user_details (User): The current user details.
    
    Returns:
        Review: The updated review object.
    """
    user_uid = user_details.uid
    if not user_uid:
        raise HTTPException(status_code=400, detail="Invalid user details: missing user UID")
    
    return await review_service.update_review_service(session, review_uid, user_uid, review_data)

@review_router.delete("/{review_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_uid: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_details: Annotated[User, Depends(get_current_user)],
):
    """
    Delete a review by UID.
    
    Args:
        review_uid (str): The UID of the review to delete.
        session (AsyncSession): The database session.
        user_details (User): The current user details.
    
    Returns:
        dict: A message indicating successful deletion.
    """
    user_uid = user_details.uid
    if not user_uid:
        raise HTTPException(status_code=400, detail="Invalid user details: missing user UID")
    
    return await review_service.delete_review_to_from_book_service(session, review_uid, user_uid)