from superajan12.events import EventBus


def test_event_bus_history_filters_by_single_event_type() -> None:
    bus = EventBus(max_queue_size=20)
    bus.publish("scan.started", {"seq": 1})
    bus.publish("scan.completed", {"seq": 2})
    bus.publish("scan.started", {"seq": 3})

    started_only = bus.history(limit=10, event_type="scan.started")

    assert len(started_only) == 2
    assert all(event["type"] == "scan.started" for event in started_only)
    assert [event["payload"]["seq"] for event in started_only] == [1, 3]


def test_event_bus_history_filters_by_multiple_event_types() -> None:
    bus = EventBus(max_queue_size=20)
    bus.publish("risk.snapshot", {"seq": 1})
    bus.publish("scan.started", {"seq": 2})
    bus.publish("scan.completed", {"seq": 3})
    bus.publish("risk.snapshot", {"seq": 4})

    filtered = bus.history(limit=10, event_types=["scan.completed", "risk.snapshot"])

    assert len(filtered) == 3
    assert [event["type"] for event in filtered] == ["risk.snapshot", "scan.completed", "risk.snapshot"]


def test_event_bus_subscription_filters_event_types() -> None:
    bus = EventBus(max_queue_size=20)
    all_events = bus.subscribe()
    risk_only = bus.subscribe(event_types={"risk.snapshot"})

    bus.publish("scan.started", {"seq": 1})
    bus.publish("risk.snapshot", {"seq": 2})

    first_all = all_events.get_nowait().to_dict()
    second_all = all_events.get_nowait().to_dict()
    only_risk = risk_only.get_nowait().to_dict()

    assert [first_all["type"], second_all["type"]] == ["scan.started", "risk.snapshot"]
    assert only_risk["type"] == "risk.snapshot"
    assert only_risk["payload"]["seq"] == 2
