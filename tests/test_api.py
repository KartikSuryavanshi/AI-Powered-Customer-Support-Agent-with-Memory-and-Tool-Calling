from fastapi.testclient import TestClient

from main import app


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"


def test_list_tickets() -> None:
    with TestClient(app) as client:
        response = client.get("/tickets")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
