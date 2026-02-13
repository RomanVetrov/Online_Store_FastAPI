"""Репозиторий для работы с пользователями."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    """
    Получить пользователя по ID.

    Args:
        session: Асинхронная сессия БД
        user_id: Идентификатор пользователя

    Returns:
        User | None: Пользователь или None если не найден
    """
    return await session.get(User, user_id)


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """
    Получить пользователя по email.

    Args:
        session: Асинхронная сессия БД
        email: Email пользователя

    Returns:
        User | None: Пользователь или None если не найден
    """
    stmt = select(User).where(User.email == email)
    user = await session.execute(stmt)
    return user.scalar_one_or_none()


async def create_user(
    session: AsyncSession, *, email: str, hashed_password: str
) -> User:
    """
    Создать нового пользователя.

    Args:
        session: Асинхронная сессия БД
        email: Email пользователя
        hashed_password: Хешированный пароль

    Returns:
        User: Созданный пользователь
    """
    new_user = User(email=email, hashed_password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user
