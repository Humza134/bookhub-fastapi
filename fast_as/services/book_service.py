import logging
from typing import List, Optional

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from sqlalchemy.orm import selectinload
from models.book_model import Book, BookCreate, BookUpdate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BookService:
    async def get_all_books_service(self, session: AsyncSession) -> List[Book]:
        # statement = select(Book).order_by(desc(Book.created_at))
        statement = select(Book).options(selectinload(Book.reviews))
        result = await session.exec(statement)
        books = result.all()
        return list(books)
    
    async def get_all_books_by_user(self, session: AsyncSession, user_uid: str) -> List[Book]:
        # statement = select(Book).where(Book.user_uid == user_uid)
        statement = select(Book).where(Book.user_uid == user_uid).options(selectinload(Book.reviews))
        result = await session.exec(statement)
        books = result.all()
        return list(books)
        
    
    async def get_book_service(self, book_uid: str, session: AsyncSession) -> Book:
        # statement = select(Book).where(Book.uid == book_uid)
        statement = select(Book).where(Book.uid == book_uid).options(selectinload(Book.reviews))
        result = await session.exec(statement)
        book = result.first()
        if not book:
            logger.warning(f"Book with UID {book_uid} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        return book

    async def create_book_service(self, book_data: BookCreate, session: AsyncSession, user_uid:str) -> Book:
        logger.info(f"Creating book with data: {book_data}")
        new_book = Book(**book_data.model_dump())
        new_book.user_uid = user_uid
        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)
        logger.info(f"Book created with UID: {new_book.uid}")
        return new_book

    async def update_book_service(self, book_uid: str, book_data: BookUpdate, session: AsyncSession) -> Book:
        book_to_update = await self.get_book_service(book_uid, session)
        update_data = book_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(book_to_update, key, value)
        session.add(book_to_update)
        await session.commit()
        await session.refresh(book_to_update)
        logger.info(f"Book with UID {book_uid} updated.")
        return book_to_update

    async def delete_book_service(self, book_uid: str, session: AsyncSession) -> dict:
        book_to_delete = await self.get_book_service(book_uid, session)
        await session.delete(book_to_delete)
        await session.commit()
        logger.info(f"Book with UID {book_uid} deleted.")
        return {"message": "Book deleted successfully"}
