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
        
    async def get_review_service(
            self, session: AsyncSession, review_uid: str
    )-> Review:
        try:
            statement = select(Review).where(Review.uid == review_uid)
            result = await session.exec(statement)
            review = result.first()
            if not review:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Review not found"
                )
            return review
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting review: {str(e)}"
            )
        
    async def update_review_service(
        self, session: AsyncSession, review_uid: str, user_uid:str, review_data: ReviewUpdate
    ) -> Review:
        try:
            review_to_update = await self.get_review_service(session, review_uid)

            # 2. Check ownership
            if str(review_to_update.user_uid) != str(user_uid):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to update this review"
                )

            update_data = review_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(review_to_update, key, value)
            session.add(review_to_update)
            await session.commit()
            await session.refresh(review_to_update)
            return review_to_update
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating review: {str(e)}"
    )

    async def delete_review_to_from_book_service(
            self, session: AsyncSession, review_uid: str, user_uid: str
    )-> dict:
        try:
            #get the review
            deleted_review = await self.get_review_service(session, review_uid)

            # 3. Check if the current user is the author of the review
            if str(deleted_review.user_uid) != str(user_uid):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to delete this review"
                )

            # 4. Delete the review
            await session.delete(deleted_review)
            await session.commit()
            return {"message": "Review deleted successfully"}
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting review: {str(e)}"
            )
            