from __future__ import annotations

from typing import TYPE_CHECKING
from decimal import Decimal
from enum import Enum

from sqlalchemy import CheckConstraint, ForeignKey, Identity, Index, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product


class OrderStatus(str, Enum):
    PENDING = "pending"  # Оформлен, ждёт оплаты
    PAID = "paid"  # Оплачен
    SHIPPED = "shipped"  # Отправлен
    DELIVERED = "delivered"  # Доставлен
    CANCELLED = "cancelled"  # Отменён


class Order(TimestampMixin, Base):
    """Заказ"""

    __tablename__ = "orders"
    __table_args__ = (
        # все заказы юзера со статусом ...
        Index("ix_orders_user_status", "user_id", "status"),
    )

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.PENDING, index=True)
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), CheckConstraint("total_price >= 0"), nullable=False
    )
    user: Mapped[User] = relationship(back_populates="orders")

    """ all - подгрузит items(позиции) сама в базу без add(item)
            delete-orphan - удалить из базы брошенные items(позиции)"""
    items: Mapped[list[OrderItem]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderItem.id",  # детерминированность порядка
    )


class OrderItem(Base):
    """Товарная позиция"""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), index=True
    )
    # RESTRICT = нельзя удалить товар если он в заказе
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), index=True
    )

    quantity: Mapped[int] = mapped_column(
        Integer, CheckConstraint("quantity > 0"), nullable=False
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), CheckConstraint("price >= 0"), nullable=False
    )

    order: Mapped[Order] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()
