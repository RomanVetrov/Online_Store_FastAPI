"""Утилиты для работы с JWT токенами."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from app.config import settings


def create_access_token(
    *,
    subject: str,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Создание JWT access токена.

    Args:
        subject: Идентификатор субъекта (обычно user_id)
        extra_claims: Дополнительные claims для включения в токен
        expires_delta: Время жизни токена (по умолчанию из настроек)

    Returns:
        str: JWT токен
    """
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTE)
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload=payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )


class TokenExpired(Exception):
    """Исключение для истёкших токенов."""

    pass


class TokenInvalid(Exception):
    """Исключение для невалидных токенов."""

    pass


@dataclass(frozen=True)
class TokenData:
    """Данные из декодированного JWT токена."""

    sub: str
    payload: dict[str, Any]


def decode_access_token(token: str) -> TokenData:
    """
    Декодирование и валидация JWT токена.

    Args:
        token: JWT токен для декодирования

    Returns:
        TokenData: Декодированные данные токена

    Raises:
        TokenExpired: Если токен истёк
        TokenInvalid: Если токен невалиден или поврежден
    """
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"require": ["sub", "exp"]},
        )
    except ExpiredSignatureError as e:
        raise TokenExpired("Токен истёк") from e
    except InvalidTokenError as e:
        raise TokenInvalid("Неверный токен/Ошибка валидации токена") from e

    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub:
        raise TokenInvalid("Ошибка субъекта в токене")

    return TokenData(sub=sub, payload=payload)
