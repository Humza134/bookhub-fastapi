from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, text
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from database.db_config import Config

engine = create_async_engine(
        url=Config.DATABASE_URL,
        echo=True,
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    Session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with Session() as session:
        yield session