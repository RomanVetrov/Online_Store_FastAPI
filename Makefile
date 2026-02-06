# =========================
# Default target
# =========================

.DEFAULT_GOAL := help


# =========================
# Variables
# =========================

APP = app.main:app

UVICORN = uv run uvicorn
ALEMBIC = uv run alembic
RUFF = uv run ruff


# =========================
# Phony targets
# =========================

.PHONY: help run dev prod lint lint-fix format check revision upgrade downgrade db-reset init-db pre-deploy clean install test docker-build docker-run docker-up docker-down


# =========================
# Help
# =========================

help:
	@echo ""
	@echo "Available commands:"
	@echo "  make install     - Установить зависимости проекта"
	@echo "  make init-db     - Применить миграции БД"
	@echo ""
	@echo "Development:"
	@echo "  make run         - Запустить приложение без перезагрузки (как в продакшене)"
	@echo "  make dev         - Запустить с автоперезагрузкой при изменении кода"
	@echo "  make lint        - Проверить код на ошибки и стиль"
	@echo "  make lint-fix    - Автоматически исправить ошибки стиля"
	@echo "  make format      - Отформатировать код по стандартам"
	@echo "  make check       - Полная проверка: lint + format (для CI/CD)"
	@echo "  make test        - Запустить все тесты"
	@echo ""
	@echo "Database migrations:"
	@echo "  make revision    - Создать новую миграцию БД (параметр: m='описание')"
	@echo "  make upgrade     - Применить все новые миграции"
	@echo "  make downgrade   - Откатить последнюю миграцию"
	@echo "  make db-reset    - Сбросить БД и переприменить все миграции"
	@echo ""
	@echo "Production:"
	@echo "  make pre-deploy  - Проверка перед деплоем (lint + format проверка)"
	@echo "  make prod        - Запустить приложение с Gunicorn для продакшена"
	@echo "  make clean       - Удалить кеш, tmp файлы и .pyc"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build - Собрать Docker образ приложения"
	@echo "  make docker-run   - Запустить контейнер локально"
	@echo "  make docker-up    - Поднять все сервисы (docker-compose)"
	@echo "  make docker-down  - Остановить все контейнеры"
	@echo ""


# =========================
# App run
# =========================

install:
	uv sync

run:
	$(UVICORN) $(APP) --host 0.0.0.0 --port 8000

dev:
	$(UVICORN) $(APP) --reload --host 0.0.0.0 --port 8000

prod:
	gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000


# =========================
# Lint / format
# =========================

lint:
	$(RUFF) check .

lint-fix:
	$(RUFF) check . --fix

format:
	$(RUFF) format .

check:
	$(RUFF) check .
	$(RUFF) format --check .

test:
	uv run pytest -v


# =========================
# Alembic
# =========================

init-db:
	$(ALEMBIC) upgrade head

revision:
	$(ALEMBIC) revision --autogenerate -m "$(m)"

upgrade:
	$(ALEMBIC) upgrade head

downgrade:
	$(ALEMBIC) downgrade -1

db-reset:
	$(ALEMBIC) downgrade base
	$(ALEMBIC) upgrade head


# =========================
# Production
# =========================

pre-deploy: check
	@echo "Ready for deployment!"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete


# =========================
# Docker
# =========================

docker-build:
	docker build -t online-store-fastapi .

docker-run:
	docker run -p 8000:8000 --env-file .env online-store-fastapi

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down
