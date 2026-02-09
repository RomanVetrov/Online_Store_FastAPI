from __future__ import annotations

from collections.abc import Sequence
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.category import Category

from sqlalchemy.exc import IntegrityError


class CategoryAlreadyExists(Exception):
    pass



async def get_category_with_relation(session: AsyncSession, val: int | str) -> Category | None:
    # Используем selectinload для коллекций (1:N)
    opts = [selectinload(Category.products)]
    
    if isinstance(val, int) or (isinstance(val, str) and val.isdigit()):
        return await session.get(Category, int(val), options=opts)
    
    # Поиск по slug
    res = await session.execute(
        select(Category).where(Category.slug == val).options(*opts)
    )
    return res.scalar_one_or_none()


async def category_list(
    session: AsyncSession,
    *,
    only_active: bool = True,
    limit: int | None = 50,
    offset: int | None = 0
    ) -> Sequence[Category]:
    """ Получить список Category """
    stmt = select(Category)
    if only_active:
        stmt = stmt.where(Category.is_active)
    if limit is not None:
        stmt = stmt.limit(limit)
    if offset is not None:
        stmt = stmt.offset(offset)
    categories = await session.execute(stmt)
    return categories.scalars().all()


async def create_category(session: AsyncSession, *, name: str, slug: str) -> Category:
    """ Создать Category / raise unique error """
    try:
        category = Category(name=name, slug=slug)
        session.add(category)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise CategoryAlreadyExists
    await session.refresh(category)
    return category


async def update_category(
        session: AsyncSession,
        category: Category,
        **kwargs
    ) -> Category:
    """ Обновить Category """
    for field, value in kwargs.items():
        setattr(category, field, value)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def deactivate_category(session: AsyncSession, category: Category) -> Category:
    """ Деактивировать Category """
    category.is_active = False
    session.add(category)
    await session.commit()
    return category
