from __future__ import annotations
from collections.abc import Sequence


from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from sqlalchemy.exc import IntegrityError


class ProductAlreadyExists(Exception):
    pass


async def get_product_with_relation(session: AsyncSession, id: int) -> Product | None:
    """Product по id с подгрузкой категории"""
    return await session.get(Product, id, options=[selectinload(Product.category)])


async def get_product_list(
    session: AsyncSession,
    category_id: int | None = None,
    only_active: bool = True,
    limit: int | None = 50,
    offset: int | None = 0,
) -> Sequence[Product]:
    """Получить список с Products"""
    stmt = select(Product).order_by(Product.id)
    if category_id:  # для категории товара, если надо
        stmt = stmt.where(Product.category_id == category_id)
    if only_active:
        stmt = stmt.where(Product.is_active)
    if limit is not None:
        stmt = stmt.limit(limit)
    if offset is not None:
        stmt = stmt.offset(offset)
    products = await session.execute(stmt)
    return products.scalars().all()


async def create_product(session: AsyncSession, **kwargs) -> Product:
    """Создать Product / raise unique error"""
    try:
        new_product = Product(**kwargs)
        session.add(new_product)
        await session.commit()
        await session.refresh(new_product)
    except IntegrityError:
        await session.rollback()
        raise ProductAlreadyExists
    return new_product


async def update_product(session: AsyncSession, product: Product, **kwargs) -> Product:
    """Обновить Product"""
    for field, value in kwargs.items():
        setattr(product, field, value)
    await session.commit()
    return product


async def deactivate_product(
    session: AsyncSession,
    product: Product,
) -> Product:
    """Деактивировать Product"""
    product.is_active = False
    await session.commit()
    return product
