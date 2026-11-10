from app.models import User
from app.services.auth_service import (
    authenticate_user,
    create_user,
    get_user_by_email,
)


def test_create_user(db_session):
    user = create_user(
        db_session,
        "eko@example.com",
        "clave-segura-123",
    )

    assert user is not None
    assert user.email == "eko@example.com"
    assert user.hashed_password != "clave-segura-123"


def test_create_user_normalizes_email(db_session):
    user = create_user(
        db_session,
        " EKO@EXAMPLE.COM ",
        "clave-segura-123",
    )

    assert user.email == "eko@example.com"


def test_create_duplicate_user(db_session):
    create_user(db_session, "eko@example.com", "clave-segura-123")

    duplicate = create_user(
        db_session,
        "eko@example.com",
        "otra-clave-segura",
    )

    assert duplicate is None


def test_get_user_by_email(db_session):
    create_user(db_session, "eko@example.com", "clave-segura-123")

    user = get_user_by_email(db_session, "eko@example.com")

    assert user is not None
    assert user.email == "eko@example.com"


def test_authenticate_user_success(db_session):
    create_user(db_session, "eko@example.com", "clave-segura-123")

    user = authenticate_user(
        db_session,
        "eko@example.com",
        "clave-segura-123",
    )

    assert user is not None
    assert user.email == "eko@example.com"


def test_authenticate_user_wrong_password(db_session):
    create_user(db_session, "eko@example.com", "clave-segura-123")

    user = authenticate_user(
        db_session,
        "eko@example.com",
        "contraseña-incorrecta",
    )

    assert user is None


def test_authenticate_nonexistent_user(db_session):
    user = authenticate_user(
        db_session,
        "inexistente@example.com",
        "clave-segura-123",
    )

    assert user is None


def test_authenticate_inactive_user(db_session):
    user = User(
        email="eko@example.com",
        hashed_password="",
        is_active=False,
    )

    from app.core.security import hash_password

    user.hashed_password = hash_password("clave-segura-123")

    db_session.add(user)
    db_session.commit()

    result = authenticate_user(
        db_session,
        "eko@example.com",
        "clave-segura-123",
    )

    assert result is None