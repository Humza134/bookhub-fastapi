from sqlmodel.ext.asyncio.session import AsyncSession
from models.reviews_model import Review, ReviewCreate, ReviewUpdate
from services.book_service import BookService
from fastapi import HTTPException, status
from sqlmodel import select

book_service = BookService()

class ReviewService:
    async def add_review_service(
        self, session: AsyncSession, review_data: ReviewCreate, user_uid: str, book_uid: str
    ) -> Review:
        try:
            book = await book_service.get_book_service(book_uid, session)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found"
                )
            

            new_review = Review(**review_data.model_dump())
            new_review.user_uid = user_uid
            new_review.book_uid = book.uid
            session.add(new_review)
            await session.commit()
            await session.refresh(new_review)
            return new_review
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating review: {str(e)}"
            )