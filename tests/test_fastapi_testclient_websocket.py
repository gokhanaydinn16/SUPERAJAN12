from fastapi import FastAPI, Query, WebSocket
from fastapi.testclient import TestClient


def test_websocket_connect_parses_query_params() -> None:
    app = FastAPI(title="test", version="0")

    @app.websocket("/ws")
    async def ws(websocket: WebSocket, topics: list[str] | None = Query(default=None), limit: int = Query(default=20)) -> None:
        await websocket.accept()
        await websocket.send_text(",".join(topics or []))
        await websocket.send_text(str(limit))

    client = TestClient(app)
    with client.websocket_connect("/ws?topics=alpha&topics=beta&limit=5") as socket:
        assert socket.receive_text() == "alpha,beta"
        assert socket.receive_text() == "5"


def test_websocket_connect_preserves_defaults_without_filters() -> None:
    app = FastAPI(title="test", version="0")

    @app.websocket("/ws")
    async def ws(websocket: WebSocket, limit: int = Query(default=20)) -> None:
        await websocket.accept()
        await websocket.send_text(str(limit))

    client = TestClient(app)
    with client.websocket_connect("/ws") as socket:
        assert socket.receive_text() == "20"


def test_websocket_connect_params_override_url_query() -> None:
    app = FastAPI(title="test", version="0")

    @app.websocket("/ws")
    async def ws(websocket: WebSocket, limit: int = Query(default=20)) -> None:
        await websocket.accept()
        await websocket.send_text(str(limit))

    client = TestClient(app)
    with client.websocket_connect("/ws?limit=3", params={"limit": 9}) as socket:
        assert socket.receive_text() == "9"
