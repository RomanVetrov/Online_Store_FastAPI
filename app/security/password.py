"""Password hashing/verify helpers (по-человечески).

- Argon2id - рекомендуемый вариант для паролей (устойчив к GPU, без утечек по времени).
- Параметры берём из конфигурации (.env), чтобы их можно было тюнить под железо 2026+ без правки кода.
- Хеширование/проверка отправляем в threadpool, чтобы не блокировать event loop.
- Ограничиваем максимальную длину пароля как простую защиту от DoS сверхдлинными строками.
- Периодически стоит перепроверять скорость (целевой SLA ~150–250 мс) и обновлять параметры.
"""

import logging

from fastapi.concurrency import run_in_threadpool
from argon2 import PasswordHasher
from argon2.low_level import Type
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash

from app.config import settings

log = logging.getLogger(__name__)

# Argon2id с явными параметрами из конфигурации.
pwd_hasher = PasswordHasher(
    time_cost=settings.ARGON_TIME_COST,
    memory_cost=settings.ARGON_MEMORY_COST,
    parallelism=settings.ARGON_PARALLELISM,
    hash_len=settings.ARGON_HASH_LEN,
    salt_len=settings.ARGON_SALT_LEN,
    type=Type.ID,  # гарантируем Argon2id
)


async def hash_password(*, password: str) -> str:
    """
    Хеширование пароля с использованием Argon2id.

    Args:
        password: Пароль в открытом виде

    Returns:
        str: Хеш пароля

    Raises:
        ValueError: Если пароль превышает максимальную длину
    """
    if len(password) > settings.ARGON_MAX_PASSWORD_LEN:
        raise ValueError("Пароль слишком длинный")
    return await run_in_threadpool(pwd_hasher.hash, password)


async def verify_password(*, password: str, hashed_password: str) -> bool:
    """
    Проверка пароля на соответствие хешу.

    Args:
        password: Пароль в открытом виде
        hashed_password: Сохраненный хеш пароля

    Returns:
        bool: True если пароль совпадает, False иначе
    """

    def _verify() -> bool:
        if len(password) > settings.ARGON_MAX_PASSWORD_LEN:
            return False
        try:
            return pwd_hasher.verify(hashed_password, password)
        except VerifyMismatchError:
            return False
        except (VerificationError, InvalidHash) as exc:
            log.warning(
                "Argon2 verify failed (%s)",
                exc.__class__.__name__,
            )
            return False

    return await run_in_threadpool(_verify)
