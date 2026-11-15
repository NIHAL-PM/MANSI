from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_service_identity():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["x-trace-id"]


def test_readiness_is_available_in_development():
    assert TestClient(app).get("/ready").status_code == 200
