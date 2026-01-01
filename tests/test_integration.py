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

def test_api_analyze_cmd_injection():
    req = {
        "code": "import os\nos.system(\"ping \" + user_input)",
        "language": "python"
    }
    resp = client.post("/api/v1/analyze", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert any(v["type"] == "cmd_injection" for v in data["vulnerabilities"])

def test_api_analyze_yaml_load():
    req = {
        "code": "import yaml\ncfg = yaml.load(data)",
        "language": "python"
    }
    resp = client.post("/api/v1/analyze", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert any(v["type"] == "insecure_yaml" for v in data["vulnerabilities"])

def test_api_analyze_eval():
    req = {
        "code": "def run(expr):\n    return eval(expr)",
        "language": "python"
    }
    resp = client.post("/api/v1/analyze", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert any(v["type"] == "dangerous_eval" for v in data["vulnerabilities"])
