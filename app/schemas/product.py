from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    """Схема для создания продукта"""

    name: str = Field(max_length=100)
    description: str | None = Field(None, max_length=500)
    price: Decimal = Field(gt=0, decimal_places=2)  # цена > 0, 2 знака после запятой
    category_id: int = Field(gt=0)


class ProductUpdatePatch(BaseModel):
    """Схема для частичного обновления (PATCH)"""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=500)
    price: Decimal | None = Field(None, gt=0, decimal_places=2)
    category_id: int | None = Field(None, gt=0)
    is_active: bool | None = None


class ProductRead(BaseModel):
    """Схема для чтения продукта"""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    name: str
    description: str | None
    price: Decimal
    category_id: int
    is_active: bool
    created_at: datetime
