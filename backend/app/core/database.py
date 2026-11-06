from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# Ubicación del archivo .env en la raíz de EKO
ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int = 5433

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


# Construcción segura de la URL de conexión
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host="127.0.0.1",
    port=settings.POSTGRES_PORT,
    database=settings.POSTGRES_DB,
)


# Motor de conexión
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# Sesiones para trabajar con la base de datos
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# Base para los futuros modelos
class Base(DeclarativeBase):
    pass


# Dependencia para utilizar sesiones en FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()