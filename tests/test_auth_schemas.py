import pytest
from pydantic import ValidationError

from app.schemas.auth import UserLogin, UserRegister


def test_user_register_valid_data():
    user = UserRegister(
        email="eko@example.com",
        password="clave-segura-123",
    )

    assert user.email == "eko@example.com"


def test_user_register_rejects_invalid_email():
    with pytest.raises(ValidationError):
        UserRegister(
            email="correo-invalido",
            password="clave-segura-123",
        )


def test_user_register_rejects_short_password():
    with pytest.raises(ValidationError):
        UserRegister(
            email="eko@example.com",
            password="corta",
        )


def test_user_login_accepts_valid_data():
    user = UserLogin(
        email="eko@example.com",
        password="x",
    )

    assert user.email == "eko@example.com"