from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import engine


app = FastAPI(
    title="EKO",
    description="Entorno de Knowledge Operativo",
    version="0.1.0",
)


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
def database_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

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