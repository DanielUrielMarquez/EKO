from app.models import User, UserSession


def test_register_first_user(client_with_db):
    response = client_with_db.post(
        "/auth/register",
        json={
            "email": "eko@example.com",
            "password": "clave-segura-123",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "eko@example.com"
    assert "hashed_password" not in response.json()


def test_register_rejects_short_password(client_with_db):
    response = client_with_db.post(
        "/auth/register",
        json={
            "email": "eko@example.com",
            "password": "corta",
        },
    )

    assert response.status_code == 422


def test_register_closes_after_first_user(client_with_db, db_session):
    first_response = client_with_db.post(
        "/auth/register",
        json={
            "email": "eko@example.com",
            "password": "clave-segura-123",
        },
    )

    second_response = client_with_db.post(
        "/auth/register",
        json={
            "email": "otra@example.com",
            "password": "otra-clave-segura",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 403
    assert db_session.query(User).count() == 1


def test_login_returns_access_token(client_with_db):
    client_with_db.post(
        "/auth/register",
        json={
            "email": "eko@example.com",
            "password": "clave-segura-123",
        },
    )

    response = client_with_db.post(
        "/auth/login",
        json={
            "email": "eko@example.com",
            "password": "clave-segura-123",
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_rejects_wrong_password(client_with_db):
    client_with_db.post(
        "/auth/register",
        json={
            "email": "eko@example.com",
            "password": "clave-segura-123",
        },
    )

    response = client_with_db.post(
        "/auth/login",
        json={
            "email": "eko@example.com",
            "password": "clave-incorrecta",
        },
    )

    assert response.status_code == 401
def test_login_blocks_after_five_failed_attempts(client_with_db):
    client_with_db.post("/auth/register", json={"email": "eko@example.com", "password": "clave-segura-123"})

    for _ in range(5):
        response = client_with_db.post("/auth/login", json={"email": "eko@example.com", "password": "incorrecta"})
        assert response.status_code == 401

    response = client_with_db.post("/auth/login", json={"email": "eko@example.com", "password": "incorrecta"})

    assert response.status_code == 429
    assert response.headers["Retry-After"]


def test_successful_login_resets_failed_attempts(client_with_db):
    client_with_db.post("/auth/register", json={"email": "eko@example.com", "password": "clave-segura-123"})

    for _ in range(4):
        response = client_with_db.post("/auth/login", json={"email": "eko@example.com", "password": "incorrecta"})
        assert response.status_code == 401

    response = client_with_db.post("/auth/login", json={"email": "eko@example.com", "password": "clave-segura-123"})
    assert response.status_code == 200

    for _ in range(5):
        response = client_with_db.post("/auth/login", json={"email": "eko@example.com", "password": "incorrecta"})
        assert response.status_code == 401

    response = client_with_db.post("/auth/login", json={"email": "eko@example.com", "password": "incorrecta"})
    assert response.status_code == 429

def test_login_blocks_correct_password_after_limit(client_with_db):
    client_with_db.post(
        "/auth/register",
        json={
            "email": "eko@example.com",
            "password": "clave-segura-123",
        },
    )

    for _ in range(5):
        client_with_db.post(
            "/auth/login",
            json={
                "email": "eko@example.com",
                "password": "incorrecta",
            },
        )

    response = client_with_db.post(
        "/auth/login",
        json={
            "email": "eko@example.com",
            "password": "clave-segura-123",
        },
    )

    assert response.status_code == 429
    assert response.headers["Retry-After"]



def test_login_creates_database_session(client_with_db, db_session):
    client_with_db.post("/auth/register", json={"email": "eko@example.com", "password": "clave-segura-123"})

    response = client_with_db.post("/auth/login", json={"email": "eko@example.com", "password": "clave-segura-123"})

    assert response.status_code == 200
    assert db_session.query(UserSession).count() == 1


def test_logout_revokes_session_and_invalidates_token(client_with_db, db_session):
    client_with_db.post("/auth/register", json={"email": "eko@example.com", "password": "clave-segura-123"})

    login_response = client_with_db.post("/auth/login", json={"email": "eko@example.com", "password": "clave-segura-123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    logout_response = client_with_db.post("/auth/logout", headers=headers)

    assert logout_response.status_code == 204

    session = db_session.query(UserSession).one()
    assert session.revoked_at is not None

    protected_response = client_with_db.get("/chat/conversations", headers=headers)
    assert protected_response.status_code == 401
