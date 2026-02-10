
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, Query, status, HTTPException

from app.database import get_db

from app.schemas.product import(
    ProductCreate,
    ProductRead,
    ProductUpdatePatch
)

from app.repositories.product_repo import (
    ProductAlreadyExists,
    get_product_list,
    create_product,
    update_product,
    deactivate_product
)
from app.dependency import ProductDep


router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=list[ProductRead], summary="Получить список товаров")
async def product_list_route(
    category_id: int | None = Query(None, description="Категория товаров"),
    only_active: bool = Query(True, description="Только активные товары"),
    limit: int | None = Query(50, ge=1, le=100),
    offset: int | None = Query(0, ge=0),
    session: AsyncSession = Depends(get_db)
    ):
    products = await get_product_list(
        session,
        category_id=category_id,
        only_active=only_active,
        limit=limit,
        offset=offset
    )
    return products


@router.get("/{id}", response_model=ProductRead, summary="Получить продукт(+категорию)")
async def product_with_relation_route(product: ProductDep):
    return product


@router.post(
        "/",response_model=ProductRead,
        status_code=status.HTTP_201_CREATED,
        summary="Создать продукт"
        )
async def create_product_route(
    payload: ProductCreate,
    session: AsyncSession = Depends(get_db)
    ):
    try:
        new_product = await create_product(
            session,
            **payload.model_dump()
        )
    except ProductAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ошибка уникальности: name уже занято"
        )
    return new_product


@router.patch(
    "/{id}",
    response_model=ProductRead,
    summary="Обновить продукт"
    )
async def update_product_route(
    product: ProductDep,
    update_data: ProductUpdatePatch,
    session: AsyncSession = Depends(get_db)
    ):
    update_dict = update_data.model_dump(exclude_unset=True)
    updated_product = await update_product(
        session,
        product,
        **update_dict
    )
    return updated_product


@router.post(
    "/{id}/deactivate",
    response_model=ProductRead,
    summary="Деактивировать продукт"
    )
async def deactivate_product_route(
    product: ProductDep,
    session: AsyncSession = Depends(get_db)
    ):
    return await deactivate_product(session, product)