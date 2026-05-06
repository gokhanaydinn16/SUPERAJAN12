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

from .app import Cookie, FastAPI, HTTPException, Header, ParamValue, Query, WebSocket, WebSocketDisconnect
from .responses import HTMLResponse

_QUEUE_SENTINEL = object()


@dataclass
class _Response:
    status_code: int
    _body: Any
    text: str

    def json(self) -> Any:
        return self._body


@dataclass
class _RequestInputs:
    query_params: dict[str, Any]
    headers: dict[str, Any]
    cookies: dict[str, Any]


class _ClientWebSocket(WebSocket):
    def __init__(self) -> None:
        self._accepted = False
        self._closed = False
        self._to_client: queue.Queue[Any] = queue.Queue(maxsize=500)
        self._to_server: queue.Queue[Any] = queue.Queue(maxsize=500)

    async def accept(self) -> None:
        self._accepted = True

    async def send_text(self, text: str) -> None:
        if self._closed:
            raise WebSocketDisconnect()
        self._to_client.put(str(text))

    async def send_json(self, payload: Any) -> None:
        await self.send_text(json.dumps(payload))

    async def receive_text(self) -> str:
        item = await asyncio.to_thread(self._to_server.get)
        if item is _QUEUE_SENTINEL:
            raise WebSocketDisconnect()
        return str(item)

    async def receive_json(self) -> Any:
        return json.loads(await self.receive_text())

    def client_send_text(self, text: str) -> None:
        if self._closed:
            raise WebSocketDisconnect()
        self._to_server.put(str(text))

    def client_send_json(self, payload: Any) -> None:
        self.client_send_text(json.dumps(payload))

    def client_receive_text(self, timeout: float = 1.0) -> str:
        item = self._to_client.get(timeout=timeout)
        if item is _QUEUE_SENTINEL:
            raise WebSocketDisconnect()
        return str(item)

    def close(self, code: int = 1000) -> None:
        if self._closed:
            return
        self._closed = True
        for target in (self._to_client, self._to_server):
            try:
                target.put_nowait(_QUEUE_SENTINEL)
            except queue.Full:
                pass


class _WebSocketSession:
    def __init__(self, endpoint, kwargs: dict[str, Any], websocket: _ClientWebSocket) -> None:
        self._endpoint = endpoint
        self._kwargs = kwargs
        self._websocket = websocket
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._task: asyncio.Task[Any] | None = None
        self._ready = threading.Event()
        self._error: BaseException | None = None

    def __enter__(self) -> _WebSocketSession:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._ready.wait(timeout=1.0)
        if self._error is not None:
            raise self._error
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
        except BaseException as exc:  # noqa: BLE001
            self._error = exc
        finally:
            loop.close()

    def send_text(self, text: str) -> None:
        self._websocket.client_send_text(text)

    def send_json(self, payload: Any) -> None:
        self._websocket.client_send_json(payload)

    def receive_text(self, timeout: float = 1.0) -> str:
        if self._error is not None:
            raise self._error
        return self._websocket.client_receive_text(timeout=timeout)

    def receive_json(self, timeout: float = 1.0) -> Any:
        return json.loads(self.receive_text(timeout=timeout))

    def close(self, code: int = 1000) -> None:
        self._websocket.close(code=code)
        if self._loop is not None and self._task is not None and not self._task.done():
            self._loop.call_soon_threadsafe(self._task.cancel)
        if self._thread is not None:
            self._thread.join(timeout=0.2)
        if self._error is not None and not isinstance(self._error, (asyncio.CancelledError, WebSocketDisconnect)):
            raise self._error


class TestClient:
    __test__ = False

    def __init__(self, app: FastAPI) -> None:
        self.app = app

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        cookies: dict[str, Any] | None = None,
    ) -> _Response:
        return self._request("GET", path, params=params, headers=headers, cookies=cookies)

    def post(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        cookies: dict[str, Any] | None = None,
    ) -> _Response:
        return self._request("POST", path, params=params, json_body=json, headers=headers, cookies=cookies)

    def websocket_connect(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        cookies: dict[str, Any] | None = None,
        subprotocols: list[str] | None = None,
    ) -> _WebSocketSession:
        route_path, inputs = _extract_request_inputs(path, params=params, headers=headers, cookies=cookies)
        route = next(item for item in self.app.routes if item.method == "WEBSOCKET" and item.path == route_path)
        websocket = _ClientWebSocket()
        kwargs = _build_kwargs(
            route.endpoint,
            inputs=inputs,
            json_body=None,
            extra_values={"websocket": websocket, "subprotocols": subprotocols},
        )
        return _WebSocketSession(route.endpoint, kwargs, websocket)

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        cookies: dict[str, Any] | None = None,
    ) -> _Response:
        route_path, inputs = _extract_request_inputs(path, params=params, headers=headers, cookies=cookies)
        route = next(item for item in self.app.routes if item.method == method and item.path == route_path)
        kwargs = _build_kwargs(route.endpoint, inputs=inputs, json_body=json_body)
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


def _extract_request_inputs(
    path: str,
    *,
    params: dict[str, Any] | None,
    headers: dict[str, Any] | None,
    cookies: dict[str, Any] | None,
) -> tuple[str, _RequestInputs]:
    parsed = urlsplit(path)
    parsed_params = parse_qs(parsed.query, keep_blank_values=False)
    merged_params: dict[str, Any] = {}
    for key, values in parsed_params.items():
        if not values:
            continue
        merged_params[key] = values if len(values) > 1 else values[0]
    if params:
        merged_params.update(params)

    normalized_headers = _normalize_headers(headers)
    merged_cookies = _parse_cookie_header(normalized_headers.get("cookie"))
    if cookies:
        merged_cookies.update(cookies)

    return parsed.path or path, _RequestInputs(
        query_params=merged_params,
        headers=normalized_headers,
        cookies=merged_cookies,
    )


def _build_kwargs(
    func,
    *,
    inputs: _RequestInputs,
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

        default = parameter.default
        value_found, value = _resolve_request_value(name=name, annotation=annotation, default=default, inputs=inputs)
        if value_found:
            kwargs[name] = value
            continue

        if json_body is not None:
            if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
                kwargs[name] = annotation(**json_body)
                continue
            if name in json_body:
                kwargs[name] = _coerce_value(json_body[name], annotation)
                continue

        if isinstance(default, ParamValue):
            if default.default is ...:
                raise TypeError(f"Missing required {default.source} parameter: {name}")
            kwargs[name] = default.default
        elif default is not inspect._empty:
            kwargs[name] = default
        else:
            raise TypeError(f"Missing required parameter: {name}")
    return kwargs


def _resolve_request_value(*, name: str, annotation: Any, default: Any, inputs: _RequestInputs) -> tuple[bool, Any]:
    if isinstance(default, ParamValue):
        source_values = {
            "query": inputs.query_params,
            "header": inputs.headers,
            "cookie": inputs.cookies,
        }[default.source]
        for candidate in _lookup_candidates(name=name, marker=default):
            if candidate in source_values:
                return True, _coerce_value(source_values[candidate], annotation)
        return False, None

    if name in inputs.query_params:
        return True, _coerce_value(inputs.query_params[name], annotation)
    return False, None


def _lookup_candidates(*, name: str, marker: ParamValue) -> list[str]:
    explicit_alias = marker.alias
    if marker.source == "header":
        derived = name.replace("_", "-") if marker.convert_underscores else name
        ordered = [explicit_alias, derived, name]
        return [item.lower() for item in ordered if item]
    ordered = [explicit_alias, name]
    return [item for item in ordered if item]


def _normalize_headers(headers: dict[str, Any] | None) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    if not headers:
        return normalized
    for key, value in headers.items():
        normalized[str(key).lower()] = value
    return normalized


def _parse_cookie_header(value: Any) -> dict[str, str]:
    if not value or not isinstance(value, str):
        return {}
    cookies: dict[str, str] = {}
    for part in value.split(";"):
        item = part.strip()
        if not item or "=" not in item:
            continue
        name, cookie_value = item.split("=", 1)
        cookies[name.strip()] = cookie_value.strip()
    return cookies


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
