from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    # Base de datos
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int = Field(default=5433, ge=1, le=65535)

    # Aplicación
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    # Seguridad
    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0)
    RATE_LIMIT_LOGIN_ATTEMPTS: int = Field(default=5, gt=0)
    RATE_LIMIT_LOGIN_WINDOW_SECONDS: int = Field(default=900, gt=0)

    # Inteligencia artificial
    GROQ_API_KEY: SecretStr | None = None
    GROQ_MODEL: str = "openai/gpt-oss-20b"

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
