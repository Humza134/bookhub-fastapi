import logging
from typing import List, Optional

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from sqlalchemy.orm import selectinload
from models.tags_model import Tag
from models.book_model import Book
from services.book_service import BookService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

book_service = BookService()

class TagService:
    async def get_all_tags_service(self, session: AsyncSession) -> List[Tag]:
        try:
            statement = select(Tag).order_by(desc(Tag.created_at))
            result = await session.exec(statement)
            tags = result.all()
            return list(tags)
        except Exception as e:
            await session.rollback()
            logger.error(f"Error getting all tags: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting tags: {str(e)}"
            )
        
    async def get_tag_service(self, tag_uid: str, session: AsyncSession) -> Tag:
        try:
            statement = select(Tag).where(Tag.uid == tag_uid)
            result = await session.exec(statement)
            tag = result.first()
            if not tag:
                logger.warning(f"Tag with UID {tag_uid} not found.")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tag not found"
                )
            return tag
        except Exception as e:
            await session.rollback()
            logger.error(f"Error getting tag with UID {tag_uid}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting tag: {str(e)}"
            )

    async def get_books_by_tag_service(self, tag_uid: str, session: AsyncSession) -> List[Book]:
        try:
            # tag fetch kro with related books
            statement = (
                select(Tag)
                .where(Tag.uid == tag_uid)
                .options(selectinload(Tag.books).selectinload(Book.reviews))
            )
            result = await session.exec(statement)
            tag = result.first()

            if not tag:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tag not found"
                )

            return tag.books  # ye sari books return karega jo is tag se linked hain

        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching books by tag: {str(e)}"
            )

    async def add_tags_to_book_service(self, book_uid: str, tag_names: List[str], session: AsyncSession, user_uid: str) -> Book:
            book = await book_service.get_book_service(book_uid, session)
            if str(book.user_uid) != str(user_uid):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to modify tags for this book"
                )

            for tag_name in tag_names:
                statement = select(Tag).where(Tag.name == tag_name)
                result = await session.exec(statement)
                tag = result.first()

                if not tag:  # create new tag if not exists
                    tag = Tag(name=tag_name)
                    session.add(tag)
                    await session.flush()

                if tag not in book.tags:
                    book.tags.append(tag)

            session.add(book)
            await session.commit()
            await session.refresh(book)
            return book
    
    async def remove_tag_from_book_service(self, book_uid: str, tag_uid: str, session: AsyncSession, user_uid: str):

        # book fetch karo
        book = await book_service.get_book_service(book_uid, session)

        # ownership check
        if str(book.user_uid) != str(user_uid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to modify tags for this book"
            )

        # tag fetch karo
        statement = select(Tag).where(Tag.uid == tag_uid)
        result = await session.exec(statement)
        tag = result.first()

        if not tag or tag not in book.tags:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found in this book"
            )

        # remove tag
        book.tags.remove(tag)

        session.add(book)
        await session.commit()
        await session.refresh(book)
        return book

