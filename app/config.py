from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTE: int = 10
    # Argon2 tuning (can be overridden via .env)
    ARGON_TIME_COST: int = 3
    ARGON_MEMORY_COST: int = 65536  # KiB (≈64 MiB)
    ARGON_PARALLELISM: int = 2
    ARGON_HASH_LEN: int = 32
    ARGON_SALT_LEN: int = 16
    ARGON_MAX_PASSWORD_LEN: int = 1024  # basic DoS guard

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # лишние полня из .env игнорировать а не ошибка
    )


settings = Settings()
