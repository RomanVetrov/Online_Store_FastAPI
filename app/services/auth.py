"""Сервисный слой для работы с авторизацией и регистрацией пользователей."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.security.password import hash_password, verify_password
from app.repositories import user_repo


async def register_user(
    session: AsyncSession,
    email: str,
    password: str
) -> User:
    """
    Регистрация нового пользователя.

    Args:
        session: Асинхронная сессия БД
        email: Email пользователя
        password: Пароль в открытом виде

    Returns:
        User: Созданный пользователь
    """
    pass_hash = await hash_password(password=password)
    new_user = await user_repo.create_user(session, email=email, hashed_password=pass_hash)
    return new_user


async def authenticate_user(
    session: AsyncSession,
    email: str,
    password: str
) -> User | None:
    """
    Аутентификация пользователя.

    Args:
        session: Асинхронная сессия БД
        email: Email пользователя
        password: Пароль для проверки

    Returns:
        User | None: Пользователь если аутентификация успешна, иначе None
    """
    need_user = await user_repo.get_user_by_email(session, email)
    if not need_user:
        return None
    if not await verify_password(password=password, hashed_password=need_user.hashed_password):
        return None

    return need_user
