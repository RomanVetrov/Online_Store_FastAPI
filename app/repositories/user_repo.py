from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User

async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    """ User по id """
    stmt = select(User).where(User.id == user_id)
    user = await session.execute(stmt)
    return user.scalar_one_or_none() # Возврат 1 или None. Исключение если >1

async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """ User по email """
    stmt = select(User).where(User.email == email)
    user = await session.execute(stmt)
    return user.scalar_one_or_none()

async def create_user(session: AsyncSession, *, email: str, hashed_password: str) -> User:
    """ Создать User """
    new_user = User(
        email=email,
        hashed_password=hashed_password
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user) # Синхрон объекта Python с базой
    return new_user

