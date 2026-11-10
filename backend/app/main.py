from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.api.routes.auth import router as auth_router

from app.api.routes.chat import router as chat_router
from app.core.database import get_db
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import setup_logging


setup_logging()

app = FastAPI(
    title="EKO",
    description="Entorno de Knowledge Operativo",
    version="0.1.0",
)
register_exception_handlers(app)
app.include_router(chat_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {
        "nombre": "EKO",
        "mensaje": "Hola, estoy funcionando.",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "EKO Backend",
    }


@app.get("/health/db")
def database_health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "service": "EKO Backend",
            "database": "connected",
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database connection unavailable",
        )