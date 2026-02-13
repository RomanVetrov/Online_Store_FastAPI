from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependency import CategoryDep
from app.security.dependences import get_current_user
from app.schemas.category import CategoryRead, CategoryCreate, CategoryUpdatePatch
from app.repositories.category_repo import (
    CategoryAlreadyExists,
    deactivate_category,
    update_category,
    category_list,
    create_category
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/all", response_model=list[CategoryRead], summary="Получить список категорий")
async def get_categories_list_route(
    only_active: bool = Query(True, description="Только активные категории"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db),
):
    """Список категорий с фильтрацией и пагинацией."""
    categories = await category_list(
        session,
        only_active=only_active,
        limit=limit,
        offset=offset
    )
    return categories


@router.get("/{val}", response_model=CategoryRead, summary="Получить категорию")
async def get_category_route(category: CategoryDep):
    """Получение категории по ID или slug."""
    return category


@router.patch(
    "/{val}",
    response_model=CategoryRead,
    summary="Обновить категорию",
    dependencies=[Depends(get_current_user)]
)
async def category_update_route(
    category: CategoryDep,
    update_data: CategoryUpdatePatch,
    session: AsyncSession = Depends(get_db)
):
    """Частичное обновление категории (только переданные поля)."""
    update_dict = update_data.model_dump(exclude_unset=True)
    updated_category = await update_category(
        session,
        category=category,
        **update_dict
    )
    return updated_category


@router.post(
    "/",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать категорию",
    dependencies=[Depends(get_current_user)]
)
async def category_create_route(
    payload: CategoryCreate,
    session: AsyncSession = Depends(get_db)
):
    """Создание новой категории."""
    try:
        new_category = await create_category(
            session,
            **payload.model_dump()
        )
    except CategoryAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ошибка уникальности: name или slug уже заняты"
        )
    return new_category


@router.post(
    "/{val}/deactivate",
    response_model=CategoryRead,
    summary="Деактивировать категорию",
    dependencies=[Depends(get_current_user)]
)
async def deactivate_category_route(
    category: CategoryDep,
    session: AsyncSession = Depends(get_db)
):
    """Мягкое удаление категории (is_active=False)."""
    return await deactivate_category(session, category)
