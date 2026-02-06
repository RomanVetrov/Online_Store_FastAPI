from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from app.config import settings
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

def create_access_token(
    *,
    subject: str,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None  
    ) -> str:
    """ Создать JWT токен """
    now = datetime.now(timezone.utc) # время сейчас с UTC учётом зоны
    expire = now + (
        expires_delta or timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTE)
        ) # время жизни токена
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()), # с 1970 секунды когда создан
        "exp": int(expire.timestamp()), # с 1970 секунды время смерти
    }
    
    if extra_claims: # если есть доп. данные -> в токен
        payload.update(extra_claims)

    return jwt.encode(
        payload=payload,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    


class TokenExpired(Exception):
    pass

class TokenInvalid(Exception):
    pass

@dataclass(frozen=True)
class TokenData: ### Неизменяемость и явность/читаемость
    sub: str
    payload: dict[str, Any]


def decode_access_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={
                "require": ["sub", "exp"]
            }
        )
    except ExpiredSignatureError as e:
        raise TokenExpired("Токен истёк") from e
    except InvalidTokenError as e:
        raise TokenInvalid("Неверный токен/Ошибка валидации токена") from e
    
    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub:
        raise TokenInvalid("Ошибка субъекта в токене")

    return TokenData(sub=sub, payload=payload)
