"""Pydantic-схемы для API оплаты."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.payment import PaymentStatus


class PaymentRead(BaseModel):
    """Схема ответа с данными платежа."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    amount: Decimal
    currency: str
    provider: str
    status: PaymentStatus
    provider_payment_id: str | None
    checkout_url: str | None
    fail_reason: str | None
    created_at: datetime
    updated_at: datetime


class MockWebhookPayload(BaseModel):
    """Тело mock-webhook запроса."""

    event_id: str
    provider_payment_id: str
    status: str
