
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


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
