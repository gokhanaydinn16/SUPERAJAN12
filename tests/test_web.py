from fastapi.testclient import TestClient

from superajan12.web import app


def test_web_index_loads() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "SuperAjan12" in response.text
    assert "Kontrol Merkezi" in response.text


def test_dashboard_api_returns_expected_shape() -> None:
    client = TestClient(app)

    response = client.get("/api/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert "aggregate" in payload
    assert "top_markets" in payload
    assert "shadow" in payload
    assert payload["live_trading"] == "disabled"
