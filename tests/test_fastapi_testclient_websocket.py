from fastapi import Body, Cookie, FastAPI, Header, Query, WebSocket
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field


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


def test_websocket_connect_supports_client_send_and_alias_inputs() -> None:
    app = FastAPI(title="test", version="0")

    @app.websocket("/ws")
    async def ws(
        websocket: WebSocket,
        channel_name: str = Query(..., alias="channel"),
        trace_id: str = Header(...),
        session_token: str = Cookie(..., alias="session"),
    ) -> None:
        await websocket.accept()
        await websocket.send_text(channel_name)
        await websocket.send_text(trace_id)
        await websocket.send_text(session_token)
        await websocket.send_text(await websocket.receive_text())

    client = TestClient(app)
    with client.websocket_connect(
        "/ws?channel=alerts",
        headers={"Trace-Id": "req-42", "Cookie": "session=fallback"},
        cookies={"session": "cookie-99"},
    ) as socket:
        socket.send_text("ping")
        assert socket.receive_text() == "alerts"
        assert socket.receive_text() == "req-42"
        assert socket.receive_text() == "cookie-99"
        assert socket.receive_text() == "ping"


def test_http_request_supports_query_header_and_cookie_aliases() -> None:
    app = FastAPI(title="test", version="0")

    @app.get("/inspect")
    def inspect_values(
        channel_name: str = Query(..., alias="channel"),
        trace_id: str = Header(...),
        session_token: str = Cookie(..., alias="session"),
    ) -> dict[str, str]:
        return {
            "channel": channel_name,
            "trace_id": trace_id,
            "session_token": session_token,
        }

    client = TestClient(app)
    response = client.get(
        "/inspect?channel=alerts",
        headers={"TRACE-ID": "req-7", "Cookie": "session=from-header"},
        cookies={"session": "cookie-7"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "channel": "alerts",
        "trace_id": "req-7",
        "session_token": "cookie-7",
    }


def test_http_request_supports_body_alias_for_scalars_and_models() -> None:
    app = FastAPI(title="test", version="0")

    class Payload(BaseModel):
        value: int = Field(alias="v")
        legacy: int = Field(validation_alias="legacy_value")

    @app.post("/inspect-body")
    def inspect_body(
        count: int = Body(..., alias="c"),
        payload: Payload | None = None,
    ) -> dict[str, int]:
        assert payload is not None
        return {
            "count": count,
            "value": payload.value,
            "legacy": payload.legacy,
        }

    client = TestClient(app)
    response = client.post(
        "/inspect-body",
        json={"c": "5", "v": "3", "legacy_value": "7"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "count": 5,
        "value": 3,
        "legacy": 7,
    }


def test_pydantic_field_name_wins_over_aliases_when_multiple_keys_exist() -> None:
    class Payload(BaseModel):
        value: int = Field(alias="v", validation_alias="legacy_value")

    payload = Payload(value="9", v="3", legacy_value="7")

    assert payload.value == 9
