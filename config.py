from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    TG_API_KEY: SecretStr
    LZT_API_KEY: SecretStr

    CHAT_ID: int
    THREAD_ID: int | None = None
    ADMIN_ID: int

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432

    POLL_INTERVAL_SECONDS: int = 60
    MIN_SELLER_REVIEWS: int = 100
    MIN_POSITIVE_PERCENT: float = 90.0
    PRIME_MIN_AGE_YEARS: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD.get_secret_value(),
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        )


settings = Settings()
