from superajan12.safety import SafetyController


def test_safety_controller_blocks_new_positions_in_safe_mode() -> None:
    controller = SafetyController()

    controller.enable_safe_mode("endpoint instability")
    state = controller.state()

    assert state.safe_mode is True
    assert state.kill_switch is False
    assert state.can_open_new_positions is False
    assert "endpoint instability" in state.reasons


def test_kill_switch_forces_safe_mode() -> None:
    controller = SafetyController()

    controller.enable_kill_switch("manual emergency stop")
    state = controller.state()

    assert state.kill_switch is True
    assert state.safe_mode is True
    assert state.can_open_new_positions is False
    assert "manual emergency stop" in state.reasons


def test_clear_safe_mode_resets_kill_switch_state() -> None:
    controller = SafetyController()

    controller.enable_safe_mode("operator pause")
    controller.enable_kill_switch("manual emergency stop")
    controller.clear_safe_mode()
    state = controller.state()

    assert state.safe_mode is False
    assert state.kill_switch is False
    assert state.can_open_new_positions is True
    assert state.reasons == ()
