from __future__ import annotations

from typing import TYPE_CHECKING
from decimal import Decimal
from enum import Enum

from sqlalchemy import ForeignKey, Identity, String, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product


class OrderStatus(str, Enum):
    PENDING = "pending" # Оформлен, ждёт оплаты
    PAID = "paid"  # Оплачен
    SHIPPED = "shipped"  # Отправлен
    DELIVERED = "delivered" # Доставлен
    CANCELLED = "cancelled" # Отменён


class Order(TimestampMixin, Base):
    """ Заказ """
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[OrderStatus] = mapped_column(String(20), default=OrderStatus.PENDING)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    user: Mapped[User] = relationship(back_populates="orders")
    items: Mapped[list[OrderItem]] = relationship(
        """ all - подгрузит items(позиции) сама в базу без add(item)
            delete-orphan - удалить из базы брошенные items(позиции)"""
        back_populates="order",
        cascade="all, delete-orphan" # 
    )


class OrderItem(Base):
    """ Товарная позиция """
    __tablename__ = "order_items"

