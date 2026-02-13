from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    """Схема создания позиции в заказе (товар + количество при оформлении)."""
    product_id: int = Field(gt=0, description="ID товара")
    quantity: int = Field(gt=0, le=1000, description="Количество (1-1000)")
    
    # Валидация quantity через validator (альтернатива Field constraints)
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Дополнительная проверка quantity (можно расширить логику)."""
        if v > 1000:
            raise ValueError("Слишком большое количество товара в одной позиции")
        return v


class OrderItemRead(BaseModel):
    """Позиция заказа с ценой (снимок на момент оформления заказа)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    product_id: int
    quantity: int
    price: Decimal  # цена на момент заказа (историческая)


class OrderItemReadDetailed(BaseModel):
    """Позиция заказа с детальной информацией о товаре (название, цена)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    product_id: int
    quantity: int
    price: Decimal
    
    # Вложенная схема: клиент видит название товара, его категорию и т.д.
    # Требует подгрузки relationship в query (selectinload/joinedload)
    product: "ProductReadSimple"  # forward reference, определим ниже


class OrderCreate(BaseModel):
    """Схема оформления заказа: список товаров и их количество."""
    items: list[OrderItemCreate] = Field(
        min_length=1,
        max_length=100,  # защита от DOS: максимум 100 позиций
        description="Список товаров в заказе"
    )
    
    @field_validator('items')
    @classmethod
    def validate_unique_products(cls, items: list[OrderItemCreate]) -> list[OrderItemCreate]:
        product_ids = [item.product_id for item in items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Дублирование товаров в заказе. Увеличьте quantity вместо повторения.")
        return items


class OrderRead(BaseModel):
    """Базовая схема заказа: статус, сумма, дата создания."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    status: OrderStatus
    total_price: Decimal
    created_at: datetime
    updated_at: datetime


class OrderReadDetailed(BaseModel):
    """Детальная схема заказа со списком позиций и данными товаров."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    status: OrderStatus
    total_price: Decimal
    created_at: datetime
    updated_at: datetime
    
    # Вложенный список позиций с информацией о товарах
    items: list[OrderItemReadDetailed]


class OrderUpdateStatus(BaseModel):
    """Схема обновления статуса заказа (только статус, остальное не меняется)."""
    model_config = ConfigDict(extra='forbid')
    
    status: OrderStatus


class ProductReadSimple(BaseModel):
    """Упрощённая схема товара для вложенности в OrderItemReadDetailed (id, название, цена)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    price: Decimal  # текущая цена (для сравнения с исторической в OrderItem)

OrderItemReadDetailed.model_rebuild()