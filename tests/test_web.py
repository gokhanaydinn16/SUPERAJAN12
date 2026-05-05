from fastapi.testclient import TestClient

import superajan12.web as web_module
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


def test_web_runtime_bootstraps_once_on_startup(monkeypatch) -> None:
    calls: list[int] = []

    def fake_bootstrap_runtime(settings):
        calls.append(1)
        return settings

    monkeypatch.setattr(web_module, "bootstrap_runtime", fake_bootstrap_runtime)

    with TestClient(web_module.app) as client:
        assert client.get("/").status_code == 200
        assert client.get("/api/dashboard").status_code == 200

    assert calls == [1]
