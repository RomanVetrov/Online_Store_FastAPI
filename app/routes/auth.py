from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.auth import RegisterCreate, Token, UserRead
from app.security.dependences import get_current_user
from app.security.jwt import create_access_token
from app.services.auth import register_user, authenticate_user
from app.repositories.user_repo import get_user_by_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
)
async def create_user(
    payload: RegisterCreate,
    session: AsyncSession = Depends(get_db),
):
    """Регистрация нового пользователя по email и паролю."""
    check_email = await get_user_by_email(session, payload.email)
    if check_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким Email уже зарегистрирован",
        )
    new_user = await register_user(session, payload.email, payload.password)
    return UserRead.model_validate(new_user)


@router.post("/login", response_model=Token, summary="Вход в систему")
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db),
):
    """Аутентификация пользователя и выдача JWT токена."""
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Аккаунт заблокирован"
        )

    access_token = create_access_token(
        subject=str(user.id),
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserRead, summary="Получить текущего пользователя")
async def current_user(current_user: User = Depends(get_current_user)):
    """Информация о текущем авторизованном пользователе."""
    return current_user
