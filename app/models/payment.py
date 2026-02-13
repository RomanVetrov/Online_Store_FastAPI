"""ORM-модель платежа и его статусы.

Нужна, чтобы хранить жизненный цикл оплаты отдельно от заказа:
- кто провайдер;
- какой статус у оплаты;
- какие данные вернул провайдер.
"""

from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Identity, Index, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.order import Order


class PaymentStatus(str, Enum):
    """Внутренние статусы оплаты (каноничные для приложения)."""

    CREATED = "created"
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


class Payment(TimestampMixin, Base):
    """Платеж по заказу.

    Отдельная таблица нужна, чтобы не смешивать домен заказа и домен оплаты.
    """

    __tablename__ = "payments"
    __table_args__ = (
        Index("ix_payments_order_status", "order_id", "status"),
        Index("ix_payments_provider_payment_id", "provider_payment_id"),
    )

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        default=PaymentStatus.CREATED,
        nullable=False,
        index=True,
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
    )
    provider_payment_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    checkout_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    fail_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    order: Mapped[Order] = relationship()
