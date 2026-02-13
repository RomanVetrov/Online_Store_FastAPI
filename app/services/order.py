from __future__ import annotations
from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem
from app.repositories.order_repo import (
    OrderItemData,
    ProductNotFound,
    ProductNotActive,
    get_products_by_ids,
    create_order_db
)


async def create_order(
    session: AsyncSession,
    user_id: int,
    items: Sequence[OrderItemData]
) -> Order:
    """
    Создать заказ - БИЗНЕС-ЛОГИКА.
    Валидирует товары, рассчитывает цены, создаёт заказ.
    """
    # ШАГ 1: Получить все product_id
    product_ids = [item.product_id for item in items]
    
    # ШАГ 2: Загрузить товары через репозиторий
    products = await get_products_by_ids(session, product_ids)
    
    # ШАГ 3: ВАЛИДАЦИЯ существования
    found_ids = {p.id for p in products}
    missing_ids = set(product_ids) - found_ids
    if missing_ids:
        raise ProductNotFound(f"Товары не найдены: {sorted(missing_ids)}")
    
    # ШАГ 4: ВАЛИДАЦИЯ активности
    inactive_products = [p for p in products if not p.is_active]
    if inactive_products:
        inactive_ids = [p.id for p in inactive_products]
        raise ProductNotActive(f"Товары деактивированы: {inactive_ids}")
    
    # ШАГ 5: Создать маппинг для быстрого доступа
    products_map = {p.id: p for p in products}
    
    # ШАГ 6: БИЗНЕС-ЛОГИКА: создать OrderItem с ценами из Product
    order_items = []
    for item_data in items:
        product = products_map[item_data.product_id]
        order_item = OrderItem(
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            price=product.price  # берём текущую цену товара
        )
        order_items.append(order_item)
    
    # ШАГ 7: БИЗНЕС-ЛОГИКА: рассчитать общую сумму
    total_price = sum(
        Decimal(str(item.quantity)) * item.price 
        for item in order_items
    )
    
    # ШАГ 8: Сохранить через репозиторий (чистая работа с БД)
    new_order = await create_order_db(
        session,
        user_id=user_id,
        order_items=order_items,
        total_price=total_price
    )
    
    return new_order