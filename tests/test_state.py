"""Unit tests for GameState model and progression tracking."""

from src.engine.state import GameState


def test_initial_state_defaults():
    """Verify default initial values for fresh game state."""
    state = GameState()
    assert state.total_hats == 0
    assert state.lifetime_hats == 0
    assert state.total_clicks == 0
    assert state.hps == 0
    assert state.click_power == 1.0
    assert state.generators == {}
    assert state.upgrades_unlocked == []


def test_state_manual_click():
    """Verify manual click increments hats and click counters."""
    state = GameState()
    earned = state.click()
    assert earned == 1.0
    assert state.total_hats == 1.0
    assert state.lifetime_hats == 1.0
    assert state.total_clicks == 1

    for _ in range(4):
        state.click()
    assert state.total_hats == 5.0
    assert state.lifetime_hats == 5.0
    assert state.total_clicks == 5


def test_state_add_hats():
    """Verify passive/reward hat addition."""
    state = GameState()
    state.add_hats(25.5)
    assert state.total_hats == 25.5
    assert state.lifetime_hats == 25.5
    # total_clicks should remain 0 on passive gain
    assert state.total_clicks == 0


def test_state_serialization_roundtrip():
    """Verify GameState serializes to dict and reconstructs faithfully."""
    state = GameState(
        total_hats=150.0,
        lifetime_hats=500.0,
        total_clicks=42,
        hps=12.5,
        generators={"rhel": 5, "ansible": 1},
        upgrades_unlocked=["selinux_hardening"],
    )
    data = state.to_dict()
    assert data["version"] == 1
    assert data["total_hats"] == 150.0
    assert data["total_clicks"] == 42
    assert data["generators"]["rhel"] == 5

    restored = GameState.from_dict(data)
    assert restored.total_hats == 150.0
    assert restored.lifetime_hats == 500.0
    assert restored.total_clicks == 42
    assert restored.hps == 12.5
    assert restored.generators == {"rhel": 5, "ansible": 1}
    assert restored.upgrades_unlocked == ["selinux_hardening"]
