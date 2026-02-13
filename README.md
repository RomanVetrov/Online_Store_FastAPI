# Online Store FastAPI

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-Migrations-222222)](https://alembic.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![JWT](https://img.shields.io/badge/Auth-JWT-black?logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![Redis](https://img.shields.io/badge/Redis-Planned-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Planned-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

Показательный backend-проект интернет-магазина на FastAPI.
Цель проекта: чистая слоистая архитектура, современный async-стек, удобная база для дальнейшего роста в production.

## Что есть сейчас
1. Регистрация/логин пользователей с JWT access token.
2. Работа с каталогом: категории и товары.
3. Заказы: создание, просмотр, отмена только из `pending`.
4. Базовый модуль оплаты через `MockPaymentGateway`.
5. Асинхронный SQLAlchemy 2.0 + Alembic миграции.
6. Pydantic v2, репозитории, сервисный слой, DI.

## Архитектура
Слои:
- `routes`: HTTP-слой и контракты API.
- `services`: бизнес-правила.
- `repositories`: работа с БД.
- `models`: ORM-модели.
- `schemas`: входные/выходные DTO.
- `payments`: абстракция и реализации платежного провайдера.

Ключевая идея:
- `routes` ничего не знают о деталях хранения.
- `services` не зависят от конкретной платежки напрямую.
- замена провайдера возможна через интерфейс `PaymentGateway`.

## Документация по оплате
- Базовая документация находится прямо в коде: `app/routes/payment.py`, `app/services/payment.py`, `app/repositories/payment_repo.py`, `app/models/payment.py`, `app/payments/gateway.py`.

## API (кратко)
Базовый префикс: `/api/v1`

Auth:
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

Catalog:
- `GET /categories/all`
- `GET /categories/{val}`
- `POST /categories/` (auth)
- `PATCH /categories/{val}` (auth)
- `POST /categories/{val}/deactivate` (auth)
- `GET /products/`
- `GET /products/{id}`
- `POST /products/` (auth)
- `PATCH /products/{id}` (auth)
- `POST /products/{id}/deactivate` (auth)

Orders:
- `POST /orders/` (auth)
- `GET /orders/me` (auth)
- `GET /orders/{order_id}` (auth)
- `POST /orders/{order_id}/cancel` (auth)

Payments (mock):
- `POST /payments/orders/{order_id}` (auth)
- `POST /payments/webhook/mock`

Swagger:
- `http://localhost:8000/docs`

## Быстрый старт
Требования:
- Python 3.12+
- PostgreSQL
- `uv` (рекомендуется)

1. Установить зависимости:
```bash
make install
```

2. Создать `.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/online_store
SECRET_KEY=change_me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTE=10
```

3. Применить миграции:
```bash
make init-db
```

4. Запустить приложение:
```bash
make dev
```

## Полезные команды
```bash
make lint
make format
make check
make revision m="описание"
make upgrade
make downgrade
```

## Что уже сделано хорошо
1. Четкое разделение ответственности по слоям.
2. Внятные доменные ограничения по заказам.
3. Подготовленная точка расширения под реальные платежные системы.
4. Миграции в репозитории, а не “ручные правки БД”.

## Что стоит докрутить дальше и зачем
1. Выбор провайдера через конфиг/DI, а не жестко `mock`.
Почему: чтобы переключить Stripe/ЮKassa без переписывания роутов и сервиса.

2. Идемпотентность webhook по `event_id`.
Почему: платежные сервисы часто шлют один и тот же webhook повторно, нужно безопасно игнорировать дубли.

3. Атомарная транзакция для обновления `Payment` и `Order`.
Почему: чтобы не получить ситуацию “платеж успешен, а заказ не перевелся в paid” при сбое посередине.

4. Refresh tokens + Redis.
Почему: управляемые сессии, logout/revoke, безопасность долгих сессий.

5. Rate limiting через Redis.
Почему: защита от brute-force и перегрузки API.

6. Docker Compose (app + db + redis).
Почему: одинаковое окружение на локали и сервере.

7. Автотесты + CI.
Почему: уверенные рефакторинги и предсказуемые релизы.
