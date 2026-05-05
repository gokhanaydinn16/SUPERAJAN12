from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable
from uuid import uuid4


@dataclass(frozen=True)
class EventEnvelope:
    id: str
    type: str
    created_at: datetime
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "created_at": self.created_at.isoformat(),
            "payload": self.payload,
        }


PayloadFactory = Callable[[], dict[str, Any] | Awaitable[dict[str, Any]]]


class EventBus:
    """Small in-process event bus for desktop live UI updates.

    The desktop app needs a live-feeling operation stream without fake data.
    This bus emits real backend events: source health, scans, risk blocks,
    research notices, audit events, and paper/shadow position updates.
    """

    def __init__(self, max_queue_size: int = 500) -> None:
        self.max_queue_size = max_queue_size
        self._subscribers: set[asyncio.Queue[EventEnvelope]] = set()
        self._subscriber_filters: dict[asyncio.Queue[EventEnvelope], set[str] | None] = {}
        self._history: list[EventEnvelope] = []
        self._periodic_tasks: dict[str, asyncio.Task[None]] = {}
        self._periodic_lock = asyncio.Lock()

    def publish(self, event_type: str, payload: dict[str, Any] | None = None) -> EventEnvelope:
        event = EventEnvelope(
            id=str(uuid4()),
            type=event_type,
            created_at=datetime.now(timezone.utc),
            payload=payload or {},
        )
        self._history.append(event)
        self._history = self._history[-self.max_queue_size :]
        dead: list[asyncio.Queue[EventEnvelope]] = []
        for queue in self._subscribers:
            allowed_types = self._subscriber_filters.get(queue)
            if allowed_types is not None and event.type not in allowed_types:
                continue
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                dead.append(queue)
        for queue in dead:
            self._subscribers.discard(queue)
            self._subscriber_filters.pop(queue, None)
        return event

    def subscribe(self, *, event_types: list[str] | set[str] | tuple[str, ...] | None = None) -> asyncio.Queue[EventEnvelope]:
        queue: asyncio.Queue[EventEnvelope] = asyncio.Queue(maxsize=100)
        self._subscribers.add(queue)
        self._subscriber_filters[queue] = _normalize_event_types(event_types=event_types)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[EventEnvelope]) -> None:
        self._subscribers.discard(queue)
        self._subscriber_filters.pop(queue, None)

    def history(
        self,
        limit: int = 100,
        *,
        event_type: str | None = None,
        event_types: list[str] | set[str] | tuple[str, ...] | None = None,
    ) -> list[dict[str, Any]]:
        allowed_types = _normalize_event_types(event_type=event_type, event_types=event_types)
        events = self._history if allowed_types is None else [event for event in self._history if event.type in allowed_types]
        return [event.to_dict() for event in events[-limit:]]

    def periodic_publisher_names(self) -> list[str]:
        return sorted(name for name, task in self._periodic_tasks.items() if not task.done())

    async def ensure_periodic_publisher(
        self,
        name: str,
        *,
        event_type: str,
        payload_factory: PayloadFactory,
        interval_seconds: float,
        publish_immediately: bool = True,
    ) -> bool:
        """Ensure exactly one periodic publisher loop per name.

        Returns True when a new loop is created, False when a live loop already exists.
        """

        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be > 0")

        async with self._periodic_lock:
            running = self._periodic_tasks.get(name)
            if running is not None and not running.done():
                return False

            task = asyncio.create_task(
                self._run_periodic_publisher(
                    name=name,
                    event_type=event_type,
                    payload_factory=payload_factory,
                    interval_seconds=interval_seconds,
                    publish_immediately=publish_immediately,
                )
            )
            self._periodic_tasks[name] = task
            return True

    async def stop_periodic_publisher(self, name: str) -> bool:
        async with self._periodic_lock:
            task = self._periodic_tasks.pop(name, None)
        if task is None:
            return False
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        return True

    async def stop_all_periodic_publishers(self) -> None:
        names = self.periodic_publisher_names()
        for name in names:
            await self.stop_periodic_publisher(name)

    async def _run_periodic_publisher(
        self,
        *,
        name: str,
        event_type: str,
        payload_factory: PayloadFactory,
        interval_seconds: float,
        publish_immediately: bool,
    ) -> None:
        try:
            if publish_immediately:
                payload = await _resolve_payload(payload_factory)
                self.publish(event_type, payload)

            while True:
                await asyncio.sleep(interval_seconds)
                payload = await _resolve_payload(payload_factory)
                self.publish(event_type, payload)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            self.publish(
                "event_bus.periodic.error",
                {
                    "name": name,
                    "event_type": event_type,
                    "error": f"{exc.__class__.__name__}: {exc}",
                },
            )
        finally:
            current = self._periodic_tasks.get(name)
            if current is not None and current.done():
                self._periodic_tasks.pop(name, None)


async def _resolve_payload(payload_factory: PayloadFactory) -> dict[str, Any]:
    payload = payload_factory()
    if asyncio.iscoroutine(payload):
        resolved = await payload
    else:
        resolved = payload
    return dict(resolved)


def _normalize_event_types(
    *,
    event_type: str | None = None,
    event_types: list[str] | set[str] | tuple[str, ...] | None = None,
) -> set[str] | None:
    normalized: set[str] = set()
    if event_type:
        normalized.update(part for part in str(event_type).split(",") if part)
    if event_types is not None:
        for item in event_types:
            normalized.update(part for part in str(item).split(",") if part)
    return normalized or None


event_bus = EventBus()
