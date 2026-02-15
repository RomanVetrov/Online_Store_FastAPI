"""Репозиторий платежей.

Отвечает только за доступ к таблице `payments`.
Бизнес-правила находятся в сервисном слое.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment, PaymentStatus


async def create_payment(
    session: AsyncSession,
    *,
    order_id: int,
    amount: Decimal,
    currency: str,
    provider: str,
    idempotency_key: str,
) -> Payment:
    """Создать платеж в локальной БД."""
    payment = Payment(
        order_id=order_id,
        amount=amount,
        currency=currency,
        provider=provider,
        status=PaymentStatus.CREATED,
        idempotency_key=idempotency_key,
    )
    session.add(payment)
    await session.commit()
    await session.refresh(payment)
    return payment


async def get_active_payment_for_order(
    session: AsyncSession,
    order_id: int,
) -> Payment | None:
    """Найти активный (CREATED или PENDING) платёж по заказу."""
    stmt = select(Payment).where(
        Payment.order_id == order_id,
        Payment.status.in_([PaymentStatus.CREATED, PaymentStatus.PENDING]),
    )
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_payment_by_provider_payment_id(
    session: AsyncSession,
    provider_payment_id: str,
) -> Payment | None:
    """Найти платеж по идентификатору провайдера."""
    stmt = select(Payment).where(Payment.provider_payment_id == provider_payment_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def update_payment_after_create(
    session: AsyncSession,
    payment: Payment,
    *,
    provider_payment_id: str,
    checkout_url: str | None,
    provider_payload: dict[str, Any] | None,
) -> Payment:
    """Записать данные провайдера после успешного создания платежа."""
    payment.provider_payment_id = provider_payment_id
    payment.checkout_url = checkout_url
    payment.provider_payload = provider_payload
    payment.status = PaymentStatus.PENDING
    await session.commit()
    await session.refresh(payment)
    return payment


async def update_payment_status(
    session: AsyncSession,
    payment: Payment,
    *,
    status: PaymentStatus,
    provider_payload: dict[str, Any] | None = None,
    fail_reason: str | None = None,
) -> Payment:
    """Обновить статус платежа и сопутствующие поля."""
    payment.status = status
    payment.provider_payload = provider_payload
    payment.fail_reason = fail_reason
    await session.commit()
    await session.refresh(payment)
    return payment
