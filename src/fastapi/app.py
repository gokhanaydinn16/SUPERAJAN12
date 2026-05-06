from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ParamValue:
    source: str
    default: Any = ...
    alias: str | None = None
    ge: Any = None
    le: Any = None
    convert_underscores: bool = False


def Query(default: Any = ..., *, alias: str | None = None, ge: Any = None, le: Any = None) -> ParamValue:
    return ParamValue(source="query", default=default, alias=alias, ge=ge, le=le)


def Header(
    default: Any = ...,
    *,
    alias: str | None = None,
    convert_underscores: bool = True,
) -> ParamValue:
    return ParamValue(
        source="header",
        default=default,
        alias=alias,
        convert_underscores=convert_underscores,
    )


def Cookie(default: Any = ..., *, alias: str | None = None) -> ParamValue:
    return ParamValue(source="cookie", default=default, alias=alias)


@dataclass
class HTTPException(Exception):
    status_code: int
    detail: Any = None

    def __str__(self) -> str:
        return str(self.detail)


class WebSocketDisconnect(Exception):
    pass


class WebSocket:
    async def accept(self) -> None:
        return None

    async def send_text(self, text: str) -> None:
        return None

    async def send_json(self, payload: Any) -> None:
        await self.send_text(json.dumps(payload))

    async def receive_text(self) -> str:
        raise WebSocketDisconnect()

    async def receive_json(self) -> Any:
        return json.loads(await self.receive_text())


@dataclass
class Route:
    method: str
    path: str
    endpoint: Callable[..., Any]
    response_class: Any = None


class FastAPI:
    def __init__(self, title: str, version: str) -> None:
        self.title = title
        self.version = version
        self.routes: list[Route] = []

    def get(self, path: str, response_class: Any = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self._add_route("GET", path, response_class=response_class)

    def post(self, path: str, response_class: Any = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self._add_route("POST", path, response_class=response_class)

    def websocket(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self._add_route("WEBSOCKET", path)

    def _add_route(self, method: str, path: str, response_class: Any = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.routes.append(Route(method=method, path=path, endpoint=func, response_class=response_class))
            return func

        return decorator
