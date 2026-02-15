"""Контракты платежного шлюза.

Здесь описан интерфейс, через который сервис оплаты работает с провайдером.
Это делает провайдера подменяемым.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping, Protocol


@dataclass(frozen=True, slots=True)
class CreatePaymentRequest:
    """Запрос на создание платежа в провайдере."""

    payment_id: int
    order_id: int
    amount: Decimal
    currency: str
    idempotency_key: str
    description: str | None = None
    return_url: str | None = None
    cancel_url: str | None = None


@dataclass(frozen=True, slots=True)
class CreatePaymentResult:
    """Ответ провайдера после создания платежа."""

    provider_payment_id: str
    checkout_url: str | None
    raw: dict[str, Any]


@dataclass(frozen=True, slots=True)
class WebhookEvent:
    """Нормализованное webhook-событие от провайдера."""

    event_id: str
    provider_payment_id: str
    status: str
    raw: dict[str, Any]


class PaymentGateway(Protocol):
    """Интерфейс платежного провайдера."""

    provider_name: str

    async def create_payment(self, req: CreatePaymentRequest) -> CreatePaymentResult:
        """Создать платеж у внешнего провайдера."""
        ...

    def verify_webhook_signature(
        self,
        *,
        headers: Mapping[str, str],
        body: bytes,
    ) -> bool:
        """Проверить подпись webhook-запроса."""
        ...

    def parse_webhook(
        self,
        *,
        headers: Mapping[str, str],
        body: bytes,
    ) -> WebhookEvent:
        """Распарсить webhook в единый формат приложения."""
        ...
