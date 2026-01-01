from fastapi.testclient import TestClient

from backend.api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analyze_endpoint():
    response = client.post(
        "/api/v1/analyze",
        json={"code": "strcpy(buf, input);", "language": "c"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["vulnerabilities"]
