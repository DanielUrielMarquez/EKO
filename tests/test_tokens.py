from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.config import settings
from app.core.tokens import create_access_token, decode_access_token


def test_create_access_token():
    token = create_access_token(1)

    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_access_token():
    token = create_access_token(1)

    payload = decode_access_token(token)

    assert payload["sub"] == "1"
    assert "iat" in payload
    assert "exp" in payload


def test_reject_invalid_token():
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("token-invalido")


def test_reject_expired_token():
    now = datetime.now(timezone.utc)

    payload = {
        "sub": "1",
        "iat": now - timedelta(minutes=60),
        "exp": now - timedelta(minutes=30),
    }

    expired_token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(expired_token)