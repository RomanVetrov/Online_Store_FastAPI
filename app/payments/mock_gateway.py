"""Mock-реализация платежного шлюза для локальной разработки."""

from __future__ import annotations

import json
from uuid import uuid4
from typing import Mapping

from app.payments.gateway import (
    CreatePaymentRequest,
    CreatePaymentResult,
    PaymentGateway,
    WebhookEvent,
)


class MockPaymentGateway(PaymentGateway):
    """Тестовый шлюз оплаты без внешнего провайдера."""

    provider_name: str = "mock"

    async def create_payment(self, req: CreatePaymentRequest) -> CreatePaymentResult:
        """Сгенерировать тестовый платеж и ссылку на оплату."""
        provider_payment_id = f"mock_{req.payment_id}_{uuid4().hex[:8]}"
        checkout_url = f"https://mock-pay.local/checkout/{provider_payment_id}"
        raw = {
            "provider": self.provider_name,
            "provider_payment_id": provider_payment_id,
            "checkout_url": checkout_url,
        }
        return CreatePaymentResult(
            provider_payment_id=provider_payment_id,
            checkout_url=checkout_url,
            raw=raw,
        )

    def verify_webhook_signature(
        self,
        *,
        headers: Mapping[str, str],
        body: bytes,
    ) -> bool:
        """В mock-режиме подпись не проверяется."""
        return True

    def parse_webhook(
        self,
        *,
        headers: Mapping[str, str],
        body: bytes,
    ) -> WebhookEvent:
        """Преобразовать JSON webhook в структуру WebhookEvent."""
        payload = json.loads(body.decode("utf-8"))

        event_id = payload.get("event_id")
        provider_payment_id = payload.get("provider_payment_id")
        status = payload.get("status")
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("Отсутствует или некорректный event_id")
        if not isinstance(provider_payment_id, str) or not provider_payment_id:
            raise ValueError("Отсутствует или некорректный provider_payment_id")
        if not isinstance(status, str) or not status:
            raise ValueError("Отсутствует или некорректный status")

        return WebhookEvent(
            event_id=event_id,
            provider_payment_id=provider_payment_id,
            status=status,
            raw=payload,
        )
