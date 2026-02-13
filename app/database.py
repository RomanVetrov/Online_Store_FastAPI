from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings
from collections.abc import AsyncGenerator

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # логи
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession]:  # асинхронно генерит асинк сессию
    async with AsyncSessionLocal() as session:
        yield session
