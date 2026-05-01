from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
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


class EventBus:
    """Small in-process event bus for desktop live UI updates.

    The desktop app needs a live-feeling operation stream without fake data.
    This bus emits real backend events: source health, scans, risk blocks,
    research notices, audit events, and paper/shadow position updates.
    """

    def __init__(self, max_queue_size: int = 500) -> None:
        self.max_queue_size = max_queue_size
        self._subscribers: set[asyncio.Queue[EventEnvelope]] = set()
        self._history: list[EventEnvelope] = []

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
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                dead.append(queue)
        for queue in dead:
            self._subscribers.discard(queue)
        return event

    def subscribe(self) -> asyncio.Queue[EventEnvelope]:
        queue: asyncio.Queue[EventEnvelope] = asyncio.Queue(maxsize=100)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[EventEnvelope]) -> None:
        self._subscribers.discard(queue)

    def history(self, limit: int = 100) -> list[dict[str, Any]]:
        return [event.to_dict() for event in self._history[-limit:]]


event_bus = EventBus()
