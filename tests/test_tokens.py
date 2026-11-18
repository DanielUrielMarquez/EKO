from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest

from app.core.config import settings
from app.core.tokens import create_access_token, decode_access_token


def test_create_access_token():
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    token = create_access_token(1, str(uuid4()), expires_at)

    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_access_token():
    jti = str(uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    token = create_access_token(1, jti, expires_at)

    payload = decode_access_token(token)

    assert payload["sub"] == "1"
    assert payload["jti"] == jti
    assert "iat" in payload
    assert "exp" in payload


def test_reject_invalid_token():
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("token-invalido")


def test_reject_expired_token():
    now = datetime.now(timezone.utc)

    payload = {
        "sub": "1",
        "jti": str(uuid4()),
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
