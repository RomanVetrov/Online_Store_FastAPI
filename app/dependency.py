"""FastAPI зависимости для переиспользования в роутах."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.category import Category
from app.models.user import User
from app.repositories.category_repo import get_category_with_relation
from app.repositories.user_repo import get_user_by_id


async def get_category_or_404(
    val: int | str,
    session: AsyncSession = Depends(get_db)
) -> Category:
    """
    Получить категорию по ID или slug, иначе 404.

    Args:
        val: ID категории (int) или slug (str)
        session: Асинхронная сессия БД

    Returns:
        Category: Объект категории

    Raises:
        HTTPException: 404 если категория не найдена
    """
    category = await get_category_with_relation(session, val)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )
    return category


async def get_user_or_404(
    user_id: int,
    session: AsyncSession = Depends(get_db)
) -> User:
    """
    Получить пользователя по ID, иначе 404.

    Args:
        user_id: ID пользователя
        session: Асинхронная сессия БД

    Returns:
        User: Объект пользователя

    Raises:
        HTTPException: 404 если пользователь не найден
    """
    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


CategoryDep = Annotated[Category, Depends(get_category_or_404)]
"""Type alias для инъекции категории с автоматической проверкой существования."""

UserDep = Annotated[User, Depends(get_user_or_404)]
"""Type alias для инъекции пользователя с автоматической проверкой существования."""