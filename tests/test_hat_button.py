"""Unit tests for the interactive central Red Hat button component."""

import pygame
from src.engine.state import GameState
from src.ui.hat_button import HatButton


def test_initial_state_and_click_mechanics():
    """Verify default state values and manual click increments as proposed in Phase 2."""
    state = GameState()
    assert state.total_hats == 0
    assert state.hps == 0

    # Simulate manual click on central Red Hat button
    button = HatButton()
    button.handle_click(state)
    assert state.total_hats == 1

    for _ in range(9):
        button.handle_click(state)
    assert state.total_hats == 10


def test_button_hit_testing():
    """Verify button coordinate containment calculations."""
    button = HatButton(x=200, y=200, radius=50)
    assert button.is_point_inside((200, 200)) is True
    assert button.is_point_inside((230, 200)) is True
    assert button.is_point_inside((250, 200)) is True
    assert button.is_point_inside((251, 200)) is False
    assert button.is_point_inside((100, 100)) is False


def test_button_event_handling():
    """Verify mouse click and motion events update button state."""
    state = GameState()
    button = HatButton(x=100, y=100, radius=50)

    # Mouse motion over button
    motion_event = pygame.event.Event(pygame.MOUSEMOTION, {"pos": (100, 100), "rel": (0, 0), "buttons": (0, 0, 0)})
    button.handle_event(motion_event, state)
    assert button.is_hovered is True

    # Mouse motion off button
    motion_off = pygame.event.Event(pygame.MOUSEMOTION, {"pos": (300, 300), "rel": (0, 0), "buttons": (0, 0, 0)})
    button.handle_event(motion_off, state)
    assert button.is_hovered is False

    # Mouse click inside button
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (100, 100), "button": 1})
    handled = button.handle_event(click_event, state)
    assert handled is True
    assert state.total_hats == 1
    assert button.is_pressed is True

    # Mouse release
    release_event = pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": (100, 100), "button": 1})
    button.handle_event(release_event, state)
    assert button.is_pressed is False


def test_button_animation_update():
    """Verify click animation updates scale, pressed state, and popups over time."""
    state = GameState()
    button = HatButton(x=100, y=100, radius=50)
    button.handle_click(state)

    assert button.is_pressed is True
    assert button.scale == 0.90
    assert len(button.popups) == 1

    # Advance time past animation duration
    button.update(0.15)
    assert button.click_animation_timer == 0.0
    assert button.is_pressed is False
    assert button.scale >= 0.99

    # Advance time past popup lifetime (0.8s)
    button.update(1.0)
    assert len(button.popups) == 0
