from __future__ import annotations
from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product


@dataclass(frozen=True, slots=True)
class OrderItemData:
    """Данные для создания позиции в заказе."""

    product_id: int
    quantity: int


class ProductNotFound(Exception):
    """Товар не найден."""

    pass


class ProductNotActive(Exception):
    """Товар деактивирован."""

    pass


async def get_products_by_ids(
    session: AsyncSession, product_ids: list[int]
) -> list[Product]:
    """
    Получить товары по списку ID.
    """
    stmt = select(Product).where(Product.id.in_(product_ids))
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def create_order_db(
    session: AsyncSession, user_id: int, order_items: list[OrderItem], total_price
) -> Order:
    """Создать заказ в БД."""
    new_order = Order(user_id=user_id, total_price=total_price, items=order_items)
    session.add(new_order)
    await session.commit()
    await session.refresh(new_order)
    return new_order


async def get_order_by_id(
    session: AsyncSession, order_id: int, *, load_items: bool = False
) -> Order | None:
    """Получить заказ по ID."""
    if not load_items:
        return await session.get(Order, order_id)

    stmt = (
        select(Order)
        .where(Order.id == order_id)
        .options(
            # selectinload вместо joinedload для оптимизации при загрузке коллекции
            selectinload(Order.items).selectinload(OrderItem.product)
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_orders(
    session: AsyncSession, user_id: int, *, limit: int = 50, offset: int = 0
) -> Sequence[Order]:
    """Получить список заказов пользователя."""
    stmt = (
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def update_order_status(
    session: AsyncSession, order: Order, new_status: OrderStatus
) -> Order:
    """Обновить статус заказа."""
    order.status = new_status
    await session.commit()
    await session.refresh(order)
    return order
