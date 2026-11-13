"""Unit tests for the interactive central Red Hat button component."""

import pygame
from src.config import HAT_LOGO_PATH
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


def test_button_loads_official_logo_by_default():
    """Verify default HatButton initialization loads the official Red Hat logo."""
    button = HatButton()
    assert button.image is not None
    assert button.image.get_size() == (640, 486)
    assert button.image_path == HAT_LOGO_PATH


def test_button_fallback_when_image_missing_or_none():
    """Verify procedural fallback activates when image is None or path is missing."""
    # Test with image_path=None
    button_none = HatButton(image_path=None)
    assert button_none.image is None

    surf = pygame.Surface((300, 300))
    button_none.draw(surf)  # Procedural rendering should execute cleanly

    # Test with non-existent path
    button_missing = HatButton(image_path="nonexistent_logo_file.png")
    assert button_missing.image is None
    button_missing.draw(surf)  # Procedural rendering should execute cleanly


def test_button_draw_with_logo_in_all_states():
    """Verify drawing with official logo handles normal, hover, pressed, and popup states."""
    surface = pygame.Surface((400, 400), pygame.SRCALPHA)
    state = GameState()
    button = HatButton(x=200, y=200, radius=80)
    assert button.image is not None

    # Normal state render
    button.draw(surface)

    # Hovered state render
    button.is_hovered = True
    button.draw(surface)

    # Pressed state render (with tactile color tint)
    button.handle_click(state)
    assert button.is_pressed is True
    assert len(button.popups) > 0
    font = pygame.font.Font(None, 24)
    button.draw(surface, popup_font=font)


def test_button_scale_caching():
    """Verify smoothscaled logo surface is cached across frames with the same dimensions."""
    surface = pygame.Surface((400, 400))
    button = HatButton(x=200, y=200, radius=80)

    # First draw populates cache
    button.draw(surface)
    cached = button._cached_scaled_image
    assert cached is not None
    size1 = button._cached_size

    # Second draw with identical scale reuses cached surface
    button.draw(surface)
    assert button._cached_scaled_image is cached
    assert button._cached_size == size1

    # Changing scale updates cache to new size
    button.scale = 0.90
    button.draw(surface)
    assert button._cached_size != size1

