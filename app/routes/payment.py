"""HTTP-эндпоинты платежного модуля."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.payments import MockPaymentGateway, PaymentGateway
from app.repositories.order_repo import get_order_by_id
from app.schemas.payment import PaymentRead
from app.security.dependences import get_current_user
from app.services.payment import (
    PaymentNotFoundError,
    PaymentStateError,
    create_payment_for_order,
    process_webhook_event,
)

router = APIRouter(prefix="/payments", tags=["payments"])


def get_payment_gateway() -> PaymentGateway:
    """DI-фабрика: вернуть активный платежный шлюз (сейчас mock)."""
    return MockPaymentGateway()


@router.post(
    "/orders/{order_id}",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать платеж по заказу",
)
async def create_payment_route(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    gateway: PaymentGateway = Depends(get_payment_gateway),
):
    """Создать платеж для заказа текущего пользователя."""
    order = await get_order_by_id(session, order_id, load_items=False)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден"
        )
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому заказу",
        )

    try:
        payment = await create_payment_for_order(
            session,
            order=order,
            gateway=gateway,
            provider="mock",
            currency="RUB",
        )
    except PaymentStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return PaymentRead.model_validate(payment)


@router.post(
    "/webhook/mock",
    response_model=PaymentRead,
    summary="Webhook mock-провайдера",
)
async def mock_webhook_route(
    request: Request,
    session: AsyncSession = Depends(get_db),
    gateway: PaymentGateway = Depends(get_payment_gateway),
):
    """Принять webhook от mock-провайдера и обновить состояния."""
    body = await request.body()
    if not gateway.verify_webhook_signature(headers=request.headers, body=body):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверная подпись webhook",
        )

    try:
        event = gateway.parse_webhook(headers=request.headers, body=body)
        payment = await process_webhook_event(session, event=event)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except PaymentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PaymentStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return PaymentRead.model_validate(payment)
