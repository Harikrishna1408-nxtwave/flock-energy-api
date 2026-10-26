from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "portal": "urja",
    }


def test_unknown_endpoint_returns_404():
    with TestClient(app) as client:
        response = client.get("/this-route-does-not-exist")

    assert response.status_code == 404
