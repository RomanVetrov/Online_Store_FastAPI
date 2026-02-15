"""Сервисный слой оплаты.

Здесь описаны бизнес-правила:
- когда можно создать оплату;
- как обрабатывать webhook;
- когда переводить заказ в paid.
"""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus
from app.models.payment import DEFAULT_CURRENCY, Payment, PaymentStatus
from app.payments.gateway import CreatePaymentRequest, PaymentGateway, WebhookEvent
from app.repositories.order_repo import get_order_by_id, update_order_status
from app.repositories.payment_repo import (
    create_payment,
    get_active_payment_for_order,
    get_payment_by_provider_payment_id,
    update_payment_after_create,
    update_payment_status,
)


class PaymentError(Exception):
    """Базовая ошибка домена оплаты."""


class PaymentStateError(PaymentError):
    """Недопустимая операция с платежом/заказом."""


class PaymentNotFoundError(PaymentError):
    """Платеж не найден."""


def _map_provider_status(provider_status: str) -> PaymentStatus:
    """Сопоставить статус провайдера с внутренним статусом платежа."""
    normalized = provider_status.lower()
    mapping = {
        "created": PaymentStatus.CREATED,
        "pending": PaymentStatus.PENDING,
        "succeeded": PaymentStatus.SUCCEEDED,
        "paid": PaymentStatus.SUCCEEDED,
        "failed": PaymentStatus.FAILED,
        "canceled": PaymentStatus.CANCELED,
        "cancelled": PaymentStatus.CANCELED,
    }
    if normalized not in mapping:
        raise PaymentStateError(f"Неизвестный статус провайдера: {provider_status}")
    return mapping[normalized]


async def create_payment_for_order(
    session: AsyncSession,
    *,
    order: Order,
    gateway: PaymentGateway,
    currency: str = DEFAULT_CURRENCY,
) -> Payment:
    """Создать платеж для заказа и отправить его в провайдер.

    Доступно только для заказа в статусе `pending`.
    Возвращает ошибку, если по заказу уже есть активный платёж.
    """
    if order.status != OrderStatus.PENDING:
        raise PaymentStateError("Оплата доступна только для заказа в статусе pending")

    existing = await get_active_payment_for_order(session, order.id)
    if existing:
        raise PaymentStateError("По этому заказу уже есть активный платёж")

    try:
        payment = await create_payment(
            session,
            order_id=order.id,
            amount=order.total_price,
            currency=currency,
            provider=gateway.provider_name,
            idempotency_key=uuid4().hex,
        )
    except IntegrityError:
        await session.rollback()
        raise PaymentStateError("По этому заказу уже есть активный платёж")

    provider_result = await gateway.create_payment(
        CreatePaymentRequest(
            payment_id=payment.id,
            order_id=order.id,
            amount=order.total_price,
            currency=currency,
            idempotency_key=payment.idempotency_key,
            description=f"Оплата заказа #{order.id}",
        )
    )
    return await update_payment_after_create(
        session,
        payment,
        provider_payment_id=provider_result.provider_payment_id,
        checkout_url=provider_result.checkout_url,
        provider_payload=provider_result.raw,
    )


async def process_webhook_event(
    session: AsyncSession,
    *,
    event: WebhookEvent,
) -> Payment:
    """Обработать webhook-событие и синхронизировать статус платежа/заказа."""
    payment = await get_payment_by_provider_payment_id(
        session,
        provider_payment_id=event.provider_payment_id,
    )
    if not payment:
        raise PaymentNotFoundError("Платеж не найден")

    new_status = _map_provider_status(event.status)
    fail_reason = (
        event.raw.get("fail_reason") if new_status == PaymentStatus.FAILED else None
    )
    payment = await update_payment_status(
        session,
        payment,
        status=new_status,
        provider_payload=event.raw,
        fail_reason=fail_reason,
    )

    if new_status == PaymentStatus.SUCCEEDED:
        order = await get_order_by_id(session, payment.order_id, load_items=False)
        if order and order.status == OrderStatus.PENDING:
            await update_order_status(session, order, new_status=OrderStatus.PAID)

    return payment
