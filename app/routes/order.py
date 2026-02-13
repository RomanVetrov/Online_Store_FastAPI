from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.order import OrderStatus
from app.models.user import User
from app.security.dependences import get_current_user

# Pydantic схемы
from app.schemas.order import OrderCreate, OrderRead, OrderReadDetailed

# Сервис (для создания заказа - бизнес-логика)
from app.services.order import create_order

# Репозиторий (для чтения/обновления - работа с БД)
from app.repositories.order_repo import (
    OrderItemData,
    get_order_by_id,
    get_user_orders,
    update_order_status,
    ProductNotFound,
    ProductNotActive,
)


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать заказ",
)
async def create_order_route(
    payload: OrderCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Создание нового заказа для текущего пользователя."""

    # Преобразование Pydantic → dataclass
    items_data = [
        OrderItemData(product_id=item.product_id, quantity=item.quantity)
        for item in payload.items
    ]

    # Вызов сервиса с обработкой исключений
    try:
        order = await create_order(session, user_id=current_user.id, items=items_data)
    except ProductNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProductNotActive as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return OrderRead.model_validate(order)


@router.get("/me", response_model=list[OrderRead], summary="Мои заказы")
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db),
):
    """Список заказов текущего пользователя."""

    orders = await get_user_orders(
        session, user_id=current_user.id, limit=limit, offset=offset
    )

    return [OrderRead.model_validate(order) for order in orders]


@router.get("/{order_id}", response_model=OrderReadDetailed, summary="Детали заказа")
async def get_order_details(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Детальная информация о заказе с позициями и товарами."""

    # Получаем заказ с подгрузкой items
    order = await get_order_by_id(session, order_id, load_items=True)

    # Проверка существования
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден"
        )

    # Проверка прав доступа
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к этому заказу"
        )

    return OrderReadDetailed.model_validate(order)


@router.post("/{order_id}/cancel", response_model=OrderRead, summary="Отменить заказ")
async def cancel_order_route(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Отмена заказа владельцем (разрешено только из pending)."""

    # Получаем заказ без items (для смены статуса не нужны)
    order = await get_order_by_id(session, order_id, load_items=False)

    # Проверка существования
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден"
        )

    # Проверка прав доступа
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к этому заказу"
        )

    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Заказ нельзя отменить в текущем статусе",
        )

    updated_order = await update_order_status(
        session, order, new_status=OrderStatus.CANCELLED
    )

    return OrderRead.model_validate(updated_order)
