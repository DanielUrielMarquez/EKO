from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import register_exception_handlers


def test_global_exception_handler():
    test_app = FastAPI()

    register_exception_handlers(test_app)

    @test_app.get("/test-error")
    def trigger_error():
        raise RuntimeError("Detalle interno que no debe exponerse")

    client = TestClient(
        test_app,
        raise_server_exceptions=False,
    )

    response = client.get("/test-error")

    assert response.status_code == 500

    assert response.json() == {
        "error": "internal_server_error",
        "message": "EKO tuvo un problema inesperado. Intentá nuevamente.",
    }

    assert "Detalle interno" not in response.text