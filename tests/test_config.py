
import pytest
from pydantic import ValidationError

from app.core.config import Settings


@pytest.fixture
def valid_settings():
    return {
        "POSTGRES_DB": "eko",
        "POSTGRES_USER": "eko_app",
        "POSTGRES_PASSWORD": "test-password",
        "JWT_SECRET_KEY": "test-secret-key",
    }


def test_settings_accept_valid_configuration(valid_settings):
    settings = Settings(_env_file=None, **valid_settings)

    assert settings.POSTGRES_PORT == 5433
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings.RATE_LIMIT_LOGIN_ATTEMPTS == 5
    assert settings.RATE_LIMIT_LOGIN_WINDOW_SECONDS == 900


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("ACCESS_TOKEN_EXPIRE_MINUTES", 0),
        ("RATE_LIMIT_LOGIN_ATTEMPTS", -1),
        ("RATE_LIMIT_LOGIN_WINDOW_SECONDS", 0),
        ("POSTGRES_PORT", 70000),
        ("POSTGRES_PORT", 0),
    ],
)
def test_settings_reject_invalid_configuration(valid_settings, field, value):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **valid_settings, **{field: value})
