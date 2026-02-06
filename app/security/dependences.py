from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.repositories.user_repo import get_user_by_id
from app.security.jwt import decode_access_token, TokenExpired, TokenInvalid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db)
) -> User:
    """
    Получить текущего активного пользователя.
    Если токен недействителен или пользователь заблокирован — кидаем ошибку.
    """

    # 1. Проверка токена (самая быстрая)
    try:
        token_data = decode_access_token(token)
    except (TokenExpired, TokenInvalid):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или истёкший токен. Войдите заново.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Проверка sub → int (защита от кривых токенов (идентиикатор))
    try:
        user_id = int(token_data.sub)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный идентификатор в токене",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Поиск пользователя (дорогой шаг — после быстрых проверок)
    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Сессия недействительна (пользователь не найден)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Проверка активности (в модели есть is_active)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт заблокирован. Обратитесь в поддержку.",
        )

    return user