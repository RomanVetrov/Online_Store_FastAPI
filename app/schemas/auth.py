"""Pydantic схемы для авторизации и пользователей."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterCreate(BaseModel):
    """Схема для регистрации нового пользователя."""

    email: EmailStr
    password: str = Field(min_length=8, description="Минимум 8 символов")


class LoginCreate(BaseModel):
    """Схема для входа пользователя."""

    email: EmailStr
    password: str = Field(min_length=8)


class Token(BaseModel):
    """JWT токен доступа."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"


class UserRead(BaseModel):
    """Схема для чтения данных пользователя."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime
