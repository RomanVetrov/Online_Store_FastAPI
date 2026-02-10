from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.category import router as category_router
from app.routes.product import router as product_router

app = FastAPI(
    title="Online Store API",
    description="API для интернет-магазина с авторизацией и управлением товарами",
    version="0.1.0"
)

app.include_router(auth_router)
app.include_router(category_router)
app.include_router(product_router)
