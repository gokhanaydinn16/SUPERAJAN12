from __future__ import annotations

import asyncio
import inspect
import json
import queue
import threading
from dataclasses import dataclass
from typing import Any, get_args, get_origin, get_type_hints
from urllib.parse import parse_qs, urlsplit

from pydantic import BaseModel

from .app import FastAPI, HTTPException, QueryValue, WebSocket, WebSocketDisconnect
from .responses import HTMLResponse


@dataclass
class _Response:
    status_code: int
    _body: Any
    text: str

    def json(self) -> Any:
        return self._body


class _ClientWebSocket(WebSocket):
    def __init__(self) -> None:
        self._accepted = False
        self._closed = False
        self._outgoing: queue.Queue[str] = queue.Queue(maxsize=500)

    async def accept(self) -> None:
        self._accepted = True

    async def send_text(self, text: str) -> None:
        if self._closed:
            raise WebSocketDisconnect()
        self._outgoing.put(str(text))

    def receive_text(self, timeout: float = 1.0) -> str:
        return self._outgoing.get(timeout=timeout)

    def close(self) -> None:
        self._closed = True


class _WebSocketSession:
    def __init__(self, endpoint, kwargs: dict[str, Any], websocket: _ClientWebSocket) -> None:
        self._endpoint = endpoint
        self._kwargs = kwargs
        self._websocket = websocket
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._task: asyncio.Task[Any] | None = None
        self._ready = threading.Event()
        self._error: Exception | None = None

    def __enter__(self) -> _WebSocketSession:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._ready.wait(timeout=1.0)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _run(self) -> None:
        loop = asyncio.new_event_loop()
        self._loop = loop
        asyncio.set_event_loop(loop)
        task = loop.create_task(self._endpoint(**self._kwargs))
        self._task = task
        self._ready.set()
        try:
            loop.run_until_complete(task)
        except asyncio.CancelledError:
            pass
        except Exception as exc:  # noqa: BLE001
            self._error = exc
        finally:
            loop.close()

    def receive_text(self, timeout: float = 1.0) -> str:
        if self._error is not None:
            raise self._error
        return self._websocket.receive_text(timeout=timeout)

    def receive_json(self, timeout: float = 1.0) -> Any:
        return json.loads(self.receive_text(timeout=timeout))

    def close(self) -> None:
        self._websocket.close()
        if self._loop is not None and self._task is not None and not self._task.done():
            self._loop.call_soon_threadsafe(self._task.cancel)
        if self._thread is not None:
            self._thread.join(timeout=0.2)


class TestClient:
    __test__ = False

    def __init__(self, app: FastAPI) -> None:
        self.app = app

    def get(self, path: str, params: dict[str, Any] | None = None) -> _Response:
        return self._request("GET", path, params=params)

    def post(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> _Response:
        return self._request("POST", path, params=params, json_body=json)

    def websocket_connect(self, path: str, params: dict[str, Any] | None = None) -> _WebSocketSession:
        route_path, merged_params = _extract_path_and_params(path, params=params)
        route = next(item for item in self.app.routes if item.method == "WEBSOCKET" and item.path == route_path)
        websocket = _ClientWebSocket()
        kwargs = _build_kwargs(
            route.endpoint,
            params=merged_params,
            json_body=None,
            extra_values={"websocket": websocket},
        )
        return _WebSocketSession(route.endpoint, kwargs, websocket)

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> _Response:
        route_path, merged_params = _extract_path_and_params(path, params=params)
        route = next(item for item in self.app.routes if item.method == method and item.path == route_path)
        kwargs = _build_kwargs(route.endpoint, params=merged_params, json_body=json_body)
        try:
            result = route.endpoint(**kwargs)
            if inspect.isawaitable(result):
                result = asyncio.run(result)
        except HTTPException as exc:
            payload = {"detail": exc.detail}
            return _Response(status_code=exc.status_code, _body=payload, text=str(exc.detail))
        if route.response_class is HTMLResponse:
            return _Response(status_code=200, _body=result, text=str(result))
        return _Response(status_code=200, _body=result, text=str(result))


def _extract_path_and_params(path: str, *, params: dict[str, Any] | None) -> tuple[str, dict[str, Any]]:
    parsed = urlsplit(path)
    parsed_params = parse_qs(parsed.query, keep_blank_values=False)
    merged: dict[str, Any] = {}
    for key, values in parsed_params.items():
        if not values:
            continue
        merged[key] = values if len(values) > 1 else values[0]
    if params:
        merged.update(params)
    return parsed.path or path, merged


def _build_kwargs(
    func,
    *,
    params: dict[str, Any],
    json_body: dict[str, Any] | None,
    extra_values: dict[str, Any] | None = None,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    extra_values = extra_values or {}
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)
    for name, parameter in signature.parameters.items():
        annotation = type_hints.get(name, parameter.annotation)
        if name in extra_values:
            kwargs[name] = extra_values[name]
            continue
        if name in params:
            kwargs[name] = _coerce_value(params[name], annotation)
            continue
        if json_body is not None:
            if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
                kwargs[name] = annotation(**json_body)
                continue
            if name in json_body:
                kwargs[name] = _coerce_value(json_body[name], annotation)
                continue
        default = parameter.default
        if isinstance(default, QueryValue):
            if default.default is ...:
                raise TypeError(f"Missing required query parameter: {name}")
            kwargs[name] = default.default
        elif default is not inspect._empty:
            kwargs[name] = default
        else:
            raise TypeError(f"Missing required parameter: {name}")
    return kwargs


def _coerce_value(value: Any, annotation: Any) -> Any:
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin in {list, set, tuple}:
        item_type = args[0] if args else str
        values = value if isinstance(value, list) else [value]
        converted = [_coerce_value(item, item_type) for item in values]
        if origin is set:
            return set(converted)
        if origin is tuple:
            return tuple(converted)
        return converted

    if origin is not None and args:
        non_none_args = [arg for arg in args if arg is not type(None)]
        if non_none_args:
            return _coerce_value(value, non_none_args[0])

    if isinstance(value, list):
        value = value[-1] if value else None

    if annotation is int:
        return int(value)
    if annotation is float:
        return float(value)
    if annotation is bool:
        if isinstance(value, str):
            return value.lower() in {"1", "true", "yes", "on"}
        return bool(value)
    return value
