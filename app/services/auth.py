from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession 
from app.models.user import User
from app.security.password import hash_password, verify_password
from app.repositories import user_repo

async def register_user(
        session: AsyncSession,
        email: str,
        password: str) -> User:
    """ Регистрация User """
    pass_hash = hash_password(password)
    new_user = await user_repo.create_user(session, email=email, hashed_password=pass_hash)
    return new_user


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User | None:
    """ Проверка наличия User и валидности пароля """
    need_user = await user_repo.get_user_by_email(session, email)
    if not need_user:
        return None
    if not verify_password(password, need_user.hashed_password):
        return None

    return need_user
