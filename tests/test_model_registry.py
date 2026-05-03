from superajan12.model_registry import ModelRegistry, ModelVersion


def test_candidate_promotion_requires_score_and_sample() -> None:
    registry = ModelRegistry()
    version = ModelVersion(name="baseline", version="v1", status="candidate")

    check = registry.evaluate_promotion(
        version,
        latest_score={"sample_count": 10, "score": 0.4, "total_pnl_usdc": 1.0},
    )

    assert check.ready is False
    assert "shadow" in check.next_statuses
    assert any("20 scored outcomes" in reason for reason in check.reasons)


def test_shadow_promotion_can_become_ready_for_approval() -> None:
    registry = ModelRegistry()
    version = ModelVersion(name="baseline", version="v1", status="shadow")

    check = registry.evaluate_promotion(
        version,
        latest_score={
            "sample_count": 60,
            "score": 0.8,
            "win_rate": 0.62,
            "total_pnl_usdc": 12.0,
            "avg_pnl_usdc": 0.2,
        },
    )

    assert check.ready is True
    assert check.next_statuses == ("approved", "retired")
    assert any("ready for approval" in reason for reason in check.reasons)


def test_approved_model_is_live_eligible_but_not_promotable() -> None:
    registry = ModelRegistry()
    version = ModelVersion(name="baseline", version="v1", status="approved")

    check = registry.evaluate_promotion(version, latest_score={"sample_count": 100, "score": 0.5})

    assert registry.can_trade_live(version) is True
    assert check.ready is False
    assert check.next_statuses == ("retired",)


def test_retire_transition_is_allowed_from_current_status() -> None:
    registry = ModelRegistry()
    version = ModelVersion(name="baseline", version="v1", status="retired")

    check = registry.evaluate_promotion(
        version,
        latest_score={
            "sample_count": 60,
            "score": 0.8,
            "win_rate": 0.62,
            "total_pnl_usdc": 12.0,
            "avg_pnl_usdc": 0.2,
        },
        current_status="shadow",
    )

    assert check.ready is True
    assert check.next_statuses == ("approved", "retired")
    assert any("ready to retire" in reason for reason in check.reasons)


def test_live_readiness_requires_approved_model_score_and_checklist() -> None:
    registry = ModelRegistry()
    version = ModelVersion(name="baseline", version="v1", status="approved")

    readiness = registry.evaluate_live_readiness(
        version,
        latest_score={
            "sample_count": 100,
            "score": 0.6,
            "win_rate": 0.58,
            "total_pnl_usdc": 25.0,
        },
        readiness_items=[{"passed": True, "label": "operator ready"}],
    )

    assert readiness.ready is True
    assert readiness.blockers == ()


def test_live_readiness_blocks_unapproved_or_weak_models() -> None:
    registry = ModelRegistry()
    version = ModelVersion(name="baseline", version="v1", status="shadow")

    readiness = registry.evaluate_live_readiness(
        version,
        latest_score={
            "sample_count": 20,
            "score": -0.1,
            "win_rate": 0.4,
            "total_pnl_usdc": -2.0,
        },
        readiness_items=[{"passed": False, "label": "manual approval"}],
    )

    assert readiness.ready is False
    assert any("approved" in blocker for blocker in readiness.blockers)
    assert any("100 scored outcomes" in blocker for blocker in readiness.blockers)
    assert any("manual approval" in blocker for blocker in readiness.blockers)
