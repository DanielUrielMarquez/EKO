
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


logger = logging.getLogger("eko")


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        errors = []

        for error in exc.errors():
            field = ".".join(
                str(part)
                for part in error.get("loc", [])
                if part != "body"
            )

            error_type = error.get("type")

            if error_type == "missing":
                message = "El campo es obligatorio."

            elif error_type == "string_too_short":
                message = "El mensaje no puede estar vacío."

            elif error_type == "string_too_long":
                message = "El mensaje supera el máximo de 2000 caracteres."

            elif error_type == "value_error":
                message = "El mensaje no puede estar vacío."

            else:
                message = "Revisá el valor enviado."

            errors.append({
                "field": field or "request",
                "message": message,
            })

        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": "Los datos enviados no son válidos.",
                "details": errors,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ):
        logger.exception(
            "Error inesperado en %s %s",
            request.method,
            request.url.path,
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "EKO tuvo un problema inesperado. Intentá nuevamente.",
            },
        )
