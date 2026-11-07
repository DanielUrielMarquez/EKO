from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["nombre"] == "EKO"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_database_health():
    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json()["database"] == "connected"


def test_database_session_is_closed(monkeypatch):
    class FakeSession:
        closed = False

        def execute(self, query):
            return None

        def close(self):
            self.closed = True

    fake_db = FakeSession()

    monkeypatch.setattr(
        "app.core.database.SessionLocal",
        lambda: fake_db,
    )

    response = client.get("/health/db")

    assert response.status_code == 200
    assert fake_db.closed is True
