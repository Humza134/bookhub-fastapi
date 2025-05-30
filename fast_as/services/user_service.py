from sqlmodel.ext.asyncio.session import AsyncSession
from models.user_model import User, UserCreate
from fastapi import HTTPException, status
from sqlmodel import select
from utils import generate_pswd_hash

class UserService:
    async def get_user_by_email(self,email:str, session: AsyncSession) -> User | None:
        """
        Get user by email
        Args:
            email (str): The email of the user to retrieve.
            session (AsyncSession): The database session.
        Returns:
            User: The user object.
        """
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        return user
    
    async def user_exists(self, email: str, session: AsyncSession) -> User | None:
        """
        Check if user exists
        Args:
            email (str): The email of the user to check.
            session (AsyncSession): The database session.
        Returns:
            bool: True if user exists, False otherwise.
        """
        user = await self.get_user_by_email(email, session)
        if user:
            return user
        return None
    
    async def create_user(self, user_data: UserCreate, session: AsyncSession) -> User:
        """
        Create a new user
        Args:
            user_data (UserCreate): The data for the new user.
            session (AsyncSession): The database session.
        Returns:
            User: The created user object.
        """
        
        new_user = User(**user_data.model_dump())
        new_user.password_hashed = generate_pswd_hash(user_data.password)
        new_user.role = 'user'
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user