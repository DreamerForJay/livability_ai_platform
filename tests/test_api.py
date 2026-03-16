from fastapi.testclient import TestClient

from src.api.app import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_regions():
    response = client.get("/regions")
    assert response.status_code == 200
    payload = response.json()
    assert payload["items"]
    assert payload["items"][0]["region_name"] == "台中市西屯區"


def test_resolve():
    response = client.post("/resolve", json={"query": "逢甲夜市"})
    assert response.status_code == 200
    assert response.json()["region_name"] == "台中市西屯區"
